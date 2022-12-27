#!/bin/bash

# exit when any command fails
set -e

# functions
check_for_kube_file() {
  if grep "kind: Deployment\|kind: ConfigMap\|kind: Service\|kind: Secret" $FILE > /dev/null 2>&1;then
    return 0
  else
    return 1
  fi
}

check_and_apply() {
if check_for_kube_file;then
  echo dry run client
  kubectl apply --dry-run='client' -f $FILE
  echo dry run server
  kubectl apply --dry-run='server' -f $FILE
  if [ "$APPLY" = "true" ];then
    echo APPLY $FILE
    kubectl apply -f $FILE
  fi
else
  echo $FILE not valid kube file
fi
}

check_and_delete() {
if check_for_kube_file;then
  echo dry run client
  kubectl delete --dry-run='client' -f $FILE
  echo dry run server
  kubectl delete --dry-run='server' -f $FILE
  if [ "$APPLY" = "true" ];then
    echo DELETE $FILE
    kubectl delete -f $FILE
  fi
else
  echo $FILE not valid kube file
fi
}

get_github_event() {
ATTEMPTS=$2
CURRENT_HEAD=$1

while [ "$ATTEMPTS" -gt 0 ]
do
  echo ATTEMPTS=$ATTEMPTS 1>&2
  GITHUB_EVENT_RESPONSE=$(gh api -H "Accept: application/vnd.github+json" /repos/$GITHUB_REPOSITORY_OWNER/$GITHUB_REPOSITORY_NAME/events | jq .[0])
  GITHUB_EVENT_HEAD=$(echo $GITHUB_EVENT_RESPONSE | jq -r .payload.head)
  echo GITHUB_EVENT_HEAD=$GITHUB_EVENT_HEAD 1>&2
  echo CURRENT_HEAD=$CURRENT_HEAD 1>&2
  if [ "$GITHUB_EVENT_HEAD" = "$CURRENT_HEAD" ];then
    echo git head and github event head matched 1>&2
    echo $GITHUB_EVENT_RESPONSE
    break
  else
    echo try again 1>&2
  fi
  if [ "$ATTEMPTS" -eq 1 ];then
    echo can not get right github event EXIT WTITH ERROR 1>&2
    exit 1
  fi
  ATTEMPTS=$(( $ATTEMPTS - 1 ))
  sleep 3
done
}

# run checks
DELETED_FILES=/tmp/deleted_files
echo > $DELETED_FILES
rm $DELETED_FILES
echo get kube config
echo "$KUBE_CONFIG_DATA" | base64 -d > /tmp/config
export KUBECONFIG=/tmp/config
echo get kube nodes
kubectl get nodes
echo get git changes
git config --global --add safe.directory /github/workspace
#GIT_HEAD=$(git rev-parse HEAD)
#echo GIT_HEAD=$GIT_HEAD
#GITHUB_EVENT=$(gh api -H "Accept: application/vnd.github+json" /repos/$GITHUB_REPOSITORY_OWNER/$GITHUB_REPOSITORY_NAME/events | jq .[0])
#GITHUB_EVENT=$(get_github_event $GIT_HEAD 3)
#echo GITHUB_EVENT=$GITHUB_EVENT
#echo GITHUB_CONTEXT=$GITHUB_CONTEXT
LAST_COMMIT=$(echo $GITHUB_EVENT | jq -r .after)
echo LAST_COMMIT=$LAST_COMMIT
PREV_COMMIT=$(echo $GITHUB_EVENT | jq -r .before)
echo PREV_COMMIT=$PREV_COMMIT
#CURRENT_COMMIT=$(git rev-parse HEAD)
#echo CURRENT_COMMIT=$CURRENT_COMMIT
#
echo found commits...
echo $GITHUB_EVENT | jq -r '.commits[] | "\"\(.message)\" (\(.sha))"'
echo get changed files...
for FILE in $((
                git diff --name-only $PREV_COMMIT $LAST_COMMIT
              ) | sort )
do
  echo -=[ processing $FILE ]=-
  if [ -f $FILE ];then
    check_and_apply
  else
    echo file $FILE looks like deleted - will check
    echo $FILE >> $DELETED_FILES
  fi
done
# 
if [ -f "$DELETED_FILES" ];then
  echo check for deleted files
  git checkout $PREV_COMMIT > /dev/null 2>&1
  for FILE in $(cat $DELETED_FILES)
  do
    echo -=[ processing $FILE ]=-
    if [ -f $FILE ];then
      check_and_delete
    else
      echo can not find $FILE
    fi
  done
  rm $DELETED_FILES
else
  echo check for deleted files skipped
fi
rm $KUBECONFIG

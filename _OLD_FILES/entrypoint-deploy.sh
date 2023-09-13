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
LAST_COMMIT=$(git --no-pager log | head -1 | sed 's#commit ##g')
echo LAST_COMMIT=$LAST_COMMIT
#
for FILE in $((
           for GID in $(git --no-pager show $LAST_COMMIT | grep ^--- | grep -v /dev/null | sed 's#--- a/##g');do echo $GID; done
           for GIA in $(git --no-pager show $LAST_COMMIT | grep ^+++ | grep -v /dev/null | sed 's#+++ b/##g');do echo $GIA; done
           ) | sort | uniq )
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
  PREV_COMMIT=$(git --no-pager log | grep ^commit | head -2 | tail -1 | sed 's#commit ##g')
  echo PREV_COMMIT=$PREV_COMMIT
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
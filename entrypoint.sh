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
  echo check $FILE
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
# run checks
DELETED_FILES=/tmp/deleted_files
echo > $DELETED_FILES
echo get kube config
echo "$KUBE_CONFIG_DATA" | base64 -d > /tmp/config
export KUBECONFIG=/tmp/config
echo get kube nodes
kubectl get nodes
echo get git changes
git config --global --add safe.directory /github/workspace
LAST_COMMIT=$(git --no-pager log | head -1 | awk -F"it " '{print $2}')
echo LAST_COMMIT=$LAST_COMMIT
#
for FILE in $((
           for GID in $(git --no-pager show $LAST_COMMIT | grep ^--- | grep -v /dev/null | awk -F"a/" '{print $2}');do echo $GID; done
           for GIA in $(git --no-pager show $LAST_COMMIT | grep ^+++ | grep -v /dev/null | awk -F"b/" '{print $2}');do echo $GIA; done
           ) | sort | uniq )
do
  if [ -f $FILE ];then
    check_and_apply
#    if check_for_kube_file;then
#      echo check $FILE
#      echo dry run client
#      kubectl apply --dry-run='client' -f $FILE
#      echo dry run server
#      kubectl apply --dry-run='server' -f $FILE
#      if [ "$APPLY" = "true" ];then
#        echo APPLY $FILE
#        kubectl apply -f $FILE
#      fi
#    else
#      echo $FILE not valid kube file
#    fi
  else
    echo file $FILE deleted
    echo $FILE >> $DELETED_FILES
  fi
done
# 
echo check for deleted files
PREV_COMMIT=$(git --no-pager log | grep ^commit | head -2 | tail -1 | awk -F"it " '{print $2}')
echo PREV_COMMIT=$PREV_COMMIT
git checkout $PREV_COMMIT
for FILE in $(cat $DELETED_FILES)
do
  if [ -f $FILE ];then
    check_and_apply
  fi
done
rm /tmp/config

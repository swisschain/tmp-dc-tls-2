#!/bin/bash

# exit when any command fails
set -e

# run checks
echo "$KUBE_CONFIG_DATA" | base64 -d > /tmp/config
export KUBECONFIG=/tmp/config
kubectl get nodes
git config --global --add safe.directory /github/workspace
#CU=$(id -u)
#ls -la | head
#chown -R $CU ./
#ls -la | head
#git log 
#git --no-pager log | head -100
LAST_COMMIT=$(git --no-pager log | head -1 | awk -F"it " '{print $2}')
echo LAST_COMMIT=$LAST_COMMIT
#git show
#git --no-pager show $LAST_COMMIT
#
for FILE in $((
           for GID in $(git --no-pager show $LAST_COMMIT | grep ^--- | grep -v /dev/null | awk -F"a/" '{print $2}');do echo $GID; done
           for GIA in $(git --no-pager show $LAST_COMMIT | grep ^+++ | grep -v /dev/null | awk -F"b/" '{print $2}');do echo $GIA; done
           ) | sort | uniq )
do
  if [ -f $FILE ];then
    if grep "kind: Deployment\|kind: ConfigMap\|kind: Service\|kind: Secret" $FILE > /dev/null 2>&1;then
      echo check $FILE
      echo dry run client
      kubectl apply --dry-run='client' -f $FILE
      echo dry run server
      kubectl apply --dry-run='server' -f $FILE
      if [ "$APPLY" = "true" ];then
        echo APPLY $FILE
        kubectl apply -f $FILE
      fi
    fi
  fi
done
rm /tmp/config

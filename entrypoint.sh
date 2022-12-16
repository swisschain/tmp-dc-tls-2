#!/bin/bash

# exit when any command fails
set -e

git config --global --add safe.directory /github/workspace
gh repo view
echo GITHUB_EVENT_NUMBER=$GITHUB_EVENT_NUMBER
echo GITHUB_REPOSITORY_OWNER=$GITHUB_REPOSITORY_OWNER
echo GITHUB_REPOSITORY_NAME=$GITHUB_REPOSITORY_NAME
#gh api -H "Accept: application/vnd.github+json" /repos/swisschain/tmp-dc-tls/pulls
#- run: gh api -H "Accept: application/vnd.github+json" /repos/${{ github.repository_owner }}/${{ github.event.repository.name }}/pulls
#bash-3.2$ cat /tmp/www | jq '.[] | select(.number == '14') | .body' | sed 's#\\r\\n#\n#g'
#PR_BODY=$(gh api -H "Accept: application/vnd.github+json" /repos/swisschain/tmp-dc-tls/pulls | jq '.[] | select(.number == $GITHUB_EVENT_NUMBER) | .body')
PR_BODY=$(gh api -H "Accept: application/vnd.github+json" /repos/$GITHUB_REPOSITORY_OWNER/$GITHUB_REPOSITORY_NAME/pulls/$GITHUB_EVENT_NUMBER | jq .body)

if echo ${PR_BODY} | grep ~deployment-order > /dev/null 2>&1;then
  echo deployment-order detected
  PR_BODY_STR_COUNT=$(echo ${PR_BODY} | sed 's#\\r\\n#\n#g' | wc -l | awk '{print $1}')
  echo PR_BODY_STR_COUNT=$PR_BODY_STR_COUNT
  for SI in $(echo ${PR_BODY} | sed 's#\\r\\n#\n#g' | grep -A $PR_BODY_STR_COUNT ~deployment-order)
  do
    echo $SI
    if [ "$SI" = ^$ ];then
      echo epty string found
    fi
  done
else
  echo ND
fi

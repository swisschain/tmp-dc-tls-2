#!/usr/bin/python

import os

cmd = "gh api -H "Accept: application/vnd.github+json" /repos/$GITHUB_REPOSITORY_OWNER/$GITHUB_REPOSITORY_NAME/pulls/$GITHUB_EVENT_NUMBER | jq .body"

returned_value = os.system(cmd)
print('returned value:', returned_value)

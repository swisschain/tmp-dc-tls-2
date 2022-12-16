#!/usr/bin/python

import os
import subprocess

cmd1 = "gh api -H \"Accept: application/vnd.github+json\" /repos/$GITHUB_REPOSITORY_OWNER/$GITHUB_REPOSITORY_NAME/pulls/$GITHUB_EVENT_NUMBER | jq .body | sed 's#\\r\\n#\n#g' > /tmp/pr_body"
cmd2 = "gh api -H \"Accept: application/vnd.github+json\" /repos/$GITHUB_REPOSITORY_OWNER/$GITHUB_REPOSITORY_NAME/pulls/$GITHUB_EVENT_NUMBER | jq .body"

returned_value = os.system(cmd1)
returned_output = subprocess.check_output(cmd2)
print('returned value:', returned_value)
print('returned output:', returned_output)

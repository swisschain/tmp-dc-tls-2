#!/usr/bin/python

import os
import subprocess

cmd1 = "gh api -H \"Accept: application/vnd.github+json\" /repos/$GITHUB_REPOSITORY_OWNER/$GITHUB_REPOSITORY_NAME/pulls/$GITHUB_EVENT_NUMBER | jq .body | sed 's#\\r\\n#\n#g' > /tmp/pr_body"
cmd2 = "gh api -H \"Accept: application/vnd.github+json\" /repos/$GITHUB_REPOSITORY_OWNER/$GITHUB_REPOSITORY_NAME/pulls/$GITHUB_EVENT_NUMBER"

returned_value = os.system(cmd1)
returned_output = subprocess.check_output(cmd2)
print('returned value:', returned_value)
print('returned output:', returned_output)

pr_body = open('/tmp/pr_body', 'r')
pr_body_strings = pg_body.readlines()

#count = 0
for str in pr_body_strings:
    #count += 1
    #print("Line{}: {}".format(count, str.strip()))
    print("Line: {}".format(str.strip()))

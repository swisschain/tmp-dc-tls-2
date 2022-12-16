#!/usr/bin/python

import os
import subprocess
import json

cmd1 = "gh api -H \"Accept: application/vnd.github+json\" /repos/$GITHUB_REPOSITORY_OWNER/$GITHUB_REPOSITORY_NAME/pulls/$GITHUB_EVENT_NUMBER | jq .body > /tmp/pr_body"
#cmd1 = "gh api -H \"Accept: application/vnd.github+json\" /repos/$GITHUB_REPOSITORY_OWNER/$GITHUB_REPOSITORY_NAME/pulls/$GITHUB_EVENT_NUMBER | jq .body | sed 's/\\r\\n/\n/g' > /tmp/pr_body"
cmd2 = "/usr/local/bin/gh api -H \"Accept: application/vnd.github+json\" /repos/$GITHUB_REPOSITORY_OWNER/$GITHUB_REPOSITORY_NAME/pulls/$GITHUB_EVENT_NUMBER"

#returned_value = os.system(cmd1)
#returned_output = subprocess.check_output(cmd2)
#print('returned value:', returned_value)
#print('returned output:', returned_output)

#pr_body = open('/tmp/pr_body', 'r')
#pr_body_strings = pr_body.readlines()

#for line in pr_body_strings:
#  print("Line: {}".format(line.strip()))

cmd_pipe = subprocess.Popen(cmd2, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
for gh_response_line in cmd_pipe.stdout.readlines():
    gh_response_line_json = json.loads(gh_response_line)
    #print(line_json["body"]) 
    for pr_comment_line in gh_response_line_json["body"].readlines():
        print(pr_comment_line) 
    #print("Line: {}".format(line.strip()))
retval = p.wait()

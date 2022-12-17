#!/usr/bin/python

import os
import subprocess
import json

#cmd1 = "gh api -H \"Accept: application/vnd.github+json\" /repos/$GITHUB_REPOSITORY_OWNER/$GITHUB_REPOSITORY_NAME/pulls/$GITHUB_EVENT_NUMBER | jq .body > /tmp/pr_body"
#cmd1 = "gh api -H \"Accept: application/vnd.github+json\" /repos/$GITHUB_REPOSITORY_OWNER/$GITHUB_REPOSITORY_NAME/pulls/$GITHUB_EVENT_NUMBER | jq .body | sed 's/\\r\\n/\n/g' > /tmp/pr_body"
cmd = "gh api -H \"Accept: application/vnd.github+json\" /repos/$GITHUB_REPOSITORY_OWNER/$GITHUB_REPOSITORY_NAME/pulls/$GITHUB_EVENT_NUMBER"

#returned_value = os.system(cmd1)
#returned_output = subprocess.check_output(cmd2)
#print('returned value:', returned_value)
#print('returned output:', returned_output)

count=0
deployment_order_list = {}
deployment_order = open('deployment-order-group-priorities', 'r')
deployment_order_strings = deployment_order.readlines()
for line in deployment_order_strings:
  count+=1
  deployment_order_list["line"]=count
  print(count)
  print(line.strip())
  print(deployment_order_list["line"])

cmd_pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
for gh_response_line in cmd_pipe.stdout.readlines():
    gh_response_line_json = json.loads(gh_response_line)
    #print(gh_response_line_json["body"]) 
    gh_response_comments=gh_response_line_json["body"].split("\r\n")

found_deployment_order=0
for pr_comment_line in gh_response_comments:
    print(pr_comment_line)
    if "~deployment-order" in pr_comment_line:
        print("found1")
        found_deployment_order=1
    if pr_comment_line == '' and found_deployment_order == 1:
        print("empty2")
        break

#!/usr/bin/python

import os
import subprocess
import json

#LOG = "DEBUG"
LOG = "INFO"
gh_cmd = "gh api -H \"Accept: application/vnd.github+json\" /repos/$GITHUB_REPOSITORY_OWNER/$GITHUB_REPOSITORY_NAME/pulls/$GITHUB_EVENT_NUMBER"
#kube_cmd_debug = "echo KUBE_CONFIG_DATA=$KUBE_CONFIG_DATA && echo $KUBE_CONFIG_DATA | base64 -d > /tmp/config && cat /tmp/config && export KUBECONFIG=/tmp/config && set | grep KUBECONFIG  && kubectl get nodes"
#kube_cmd_info = "echo $KUBE_CONFIG_DATA | base64 -d > /tmp/config"
kube_cmd1 = "mkdir ~/.kube"
kube_cmd2 = "echo $KUBE_CONFIG_DATA | base64 -d > ~/.kube/config
kube_cmd3 = "cat ~/.kube/config"

print("get github pr comment...")
found_pr_body=0
cmd_pipe = subprocess.Popen(gh_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
for gh_response_line in cmd_pipe.stdout.readlines():
    if LOG == 'DEBUG':
      print('gh_response_line:', gh_response_line)
    gh_response_line_json = json.loads(gh_response_line)
    if LOG == 'DEBUG':
      print('gh_response_line_json:', gh_response_line_json)
    print('gh_response_line_json["body"]:', gh_response_line_json["body"])
    if gh_response_line_json["body"] != None:
        found_pr_body=1
        gh_response_comments=gh_response_line_json["body"].split("\r\n")
    print('found_pr_body:', found_pr_body)

if found_pr_body:
  print("parse comment...")
  found_deployment_order=0
  for pr_comment_line in gh_response_comments:
    print('pr_comment_line:', pr_comment_line)
    if "~deployment-order" in pr_comment_line:
        print("deployment-order detected...")
        found_deployment_order=1
    if pr_comment_line == '' and found_deployment_order == 1:
        print("enpty string found...")
        break
else:
  print("comment not found...")
  print("read group file...")
  count=0
  deployment_order_list = {}
  deployment_order = open('deployment-order-group-priorities', 'r')
  deployment_order_strings = deployment_order.readlines()
  for line in deployment_order_strings:
    count+=1
    deployment_order_list["line"]=count
    print('count:', count)
    print('line:', line.strip())
    print('deployment_order_list["line"]:', deployment_order_list["line"])

print("get kube config...")
kube_cmd1_returned_value = os.system(kube_cmd1)
print('kube_cmd1_returned_value:', kube_cmd1_returned_value)
kube_cmd2_returned_value = os.system(kube_cmd2)
print('kube_cmd2_returned_value:', kube_cmd2_returned_value)
cmd_pipe = subprocess.Popen(kube_cmd3, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
for kubectl_response_line in cmd_pipe.stdout.readlines():
  print('kubectl_response_line:', kubectl_response_line)

#!/usr/bin/python

import os
import subprocess
import json

#LOG = "DEBUG"
LOG = "INFO"
gh_cmd = "gh api -H \"Accept: application/vnd.github+json\" /repos/$GITHUB_REPOSITORY_OWNER/$GITHUB_REPOSITORY_NAME/pulls/$GITHUB_EVENT_NUMBER"
git_cmd_commits = "git --no-pager log -2"
git_cmd_safe_directory = "git config --global --add safe.directory /github/workspace"
git_cmd_show = "git --no-pager show "
#kube_cmd_debug = "echo KUBE_CONFIG_DATA=$KUBE_CONFIG_DATA && echo $KUBE_CONFIG_DATA | base64 -d > /tmp/config && cat /tmp/config && export KUBECONFIG=/tmp/config && set | grep KUBECONFIG  && kubectl get nodes"
#kube_cmd_info = "echo $KUBE_CONFIG_DATA | base64 -d > /tmp/config"
kube_cmd_dir = "mkdir ~/.kube"
kube_cmd_config = "echo $KUBE_CONFIG_DATA | base64 -d > ~/.kube/config"
kube_cmd_config_debug = "cat ~/.kube/config"
kube_cmd_nodes = "kubectl get nodes"

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

deployment_order_names = {}
if found_pr_body:
  print("parse comment...")
  found_deployment_order=0
  count=0
  for pr_comment_line in gh_response_comments:
    print('pr_comment_line:', pr_comment_line)
    if found_deployment_order == 1:
      count+=1
      #print('add to deployment_order_names count={}, line={}, check_count={}'.format(count, line.strip(), deployment_order_names["line"]))
      deployment_order_names["line"]=count
      print('count:', count)
      print('line:', line.strip())
      print('deployment_order_names["line"]:', deployment_order_names["line"])
    if "~deployment-order" in str(pr_comment_line):
        print("deployment-order detected...")
        found_deployment_order=1
    if pr_comment_line == '' and found_deployment_order == 1:
        print("enpty string found...")
        break
else:
  print("comment not found...")
  print("read group file...")
  count=0
  deployment_order = open('deployment-order-group-priorities', 'r')
  deployment_order_strings = deployment_order.readlines()
  for line in deployment_order_strings:
    count+=1
    #print('add to deployment_order_names count={}, line={}, check_count={}'.format(count, line.strip(), deployment_order_names["line"]))
    deployment_order_names["line"]=count
    print('count:', count)
    print('line:', line.strip())
    print('deployment_order_names["line"]:', deployment_order_names["line"])

print("get git current and previous commits...")
git_cmd_safe_directory_returned_value = os.system(git_cmd_safe_directory)
print('git_cmd_safe_directory_returned_value:', git_cmd_safe_directory_returned_value)
cmd_pipe = subprocess.Popen(git_cmd_commits, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
count=0
commits=[]
for git_response_line in cmd_pipe.stdout.readlines():
  print('git_response_line:', git_response_line)
  if "commit" in str(git_response_line):
    commit_id_array=str(git_response_line).split(" ")
    print('commit_id_array:', commit_id_array)
    print('commit_id:', commit_id_array[1].strip())
    #commits[count]=commit_id_array[1]
    commits[0]='67e3338f94f890f2bcaef190e662db71a92252f5'
    count+=1

print("get git current commits changes...")
git_cmd_show=git_cmd_show + commits[0]
print("git command:", git_cmd_show)
cmd_pipe = subprocess.Popen(git_cmd_show, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
for git_response_line in cmd_pipe.stdout.readlines():
  print('git_response_line:', git_response_line)

print("get kube config...")
kube_cmd_dir_returned_value = os.system(kube_cmd_dir)
print('kube_cmd_dir_returned_value:', kube_cmd_dir_returned_value)
kube_cmd_config_returned_value = os.system(kube_cmd_config)
print('kube_cmd_config_returned_value:', kube_cmd_config_returned_value)
if LOG == 'DEBUG':
  cmd_pipe = subprocess.Popen(kube_cmd_config_debug, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  for kubectl_response_line in cmd_pipe.stdout.readlines():
    print('kubectl_response_line:', kubectl_response_line)
cmd_pipe = subprocess.Popen(kube_cmd_nodes, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
for kubectl_response_line in cmd_pipe.stdout.readlines():
  print('kubectl_response_line:', kubectl_response_line)

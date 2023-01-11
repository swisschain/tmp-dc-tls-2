#!/usr/bin/python

import os
import subprocess
import json
import yaml

#LOG = "INFO"
#LOG = "DEBUG"
LOG = os.getenv('LOG')

#gh_cmd = "gh api -H \"Accept: application/vnd.github+json\" /repos/$GITHUB_REPOSITORY_OWNER/$GITHUB_REPOSITORY_NAME/pulls/$GITHUB_EVENT_NUMBER"
#kube_cmd_debug = "echo KUBE_CONFIG_DATA=$KUBE_CONFIG_DATA && echo $KUBE_CONFIG_DATA | base64 -d > /tmp/config && cat /tmp/config && export KUBECONFIG=/tmp/config && set | grep KUBECONFIG  && kubectl get nodes"
#kube_cmd_info = "echo $KUBE_CONFIG_DATA | base64 -d > /tmp/config"

print("get github pr comment...")
found_pr_body=0
#cmd_pipe = subprocess.Popen(gh_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#for gh_response_line in cmd_pipe.stdout.readlines():
#    if LOG == 'DEBUG':
#      print('gh_response_line:', gh_response_line)
gh_full_json_env = os.getenv('GITHUB_FULL_JSON')
gh_full_json = json.loads(gh_full_json_env)
if LOG == 'DEBUG':
  print('gh_full_json:', gh_full_json)
print('gh_full_json["event"]["pull_request"]["body"]:', gh_full_json["event"]["pull_request"]["body"])
if gh_full_json["event"]["pull_request"]["body"] != None:
  found_pr_body=1
  gh_pr_comment=gh_full_json["event"]["pull_request"]["body"].split("\r\n")
print('found_pr_body:', found_pr_body)

deployment_order_names = {}
if found_pr_body:
  print("parse comment...")
  found_deployment_order=0
  count=0
  for pr_comment_line in gh_pr_comment:
    print('pr_comment_line:', pr_comment_line)
    if pr_comment_line == '' and found_deployment_order == 1:
        print("enpty string found...")
        break
    if "```" in str(pr_comment_line) and found_deployment_order == 1:
        print("end of comment string found...")
        break
    if found_deployment_order == 1:
      count+=1
      #print('add to deployment_order_names count={}, line={}, check_count={}'.format(count, line.strip(), deployment_order_names["line"]))
      deployment_order_names["pr_comment_line"]=count
      print('count:', count)
      print('pr_comment_line:', pr_comment_line)
      print('deployment_order_names["pr_comment_line"]:', deployment_order_names["pr_comment_line"])
    if "~deployment-order" in str(pr_comment_line):
        print("deployment-order detected...")
        found_deployment_order=1
else:
  print("comment not found...")
  print("read group file...")
  count=0
  deployment_order = open('deployment-order-group-priorities', 'r')
  deployment_order_strings = deployment_order.readlines()
  for group_file_line in deployment_order_strings:
    count+=1
    #print('add to deployment_order_names count={}, line={}, check_count={}'.format(count, line.strip(), deployment_order_names["line"]))
    deployment_order_names["group_file_line"]=count
    print('count:', count)
    print('group_file_line:', group_file_line)
    print('deployment_order_names["group_file_line"]:', deployment_order_names["group_file_line"])

print("get git current and previous commits...")
event_name=gh_full_json["event_name"]
print('event_name:', event_name)
event_number=gh_full_json["event"]["number"]
print('event_number:', event_number)
event_action=gh_full_json["event"]["action"]
print('event_action:', event_action)
commits=gh_full_json["event"]["pull_request"]["commits"]
print('commits:', commits)
commits_url=gh_full_json["event"]["pull_request"]["commits_url"]
print('commits_url:', commits_url)
#print('git_cmd_safe_directory_returned_value:', git_cmd_safe_directory_returned_value)
#git_cmd_commits = "gh api -H \"Accept: application/vnd.github+json\" /repos/$GITHUB_REPOSITORY_OWNER/$GITHUB_REPOSITORY_NAME/pulls/$GITHUB_EVENT_NUMBER"
git_cmd_commits = "gh api -H \"Accept: application/vnd.github+json\" " + commits_url 
print('git_cmd_commits:', git_cmd_commits)
cmd_pipe = subprocess.Popen(git_cmd_commits, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#count=0
##commits=[None] * len(2)
#commits=[None] * 2
for git_response_line in cmd_pipe.stdout.readlines():
  gh_commits_json = json.loads(git_response_line)
  gh_commits_json_len=len(gh_commits_json)
  if LOG == 'DEBUG':
    print('git_response_line:', git_response_line)
    print('gh_commits_json_len:', gh_commits_json_len)
    print('gh_commits_json[0]["sha"]:', gh_commits_json[0]["sha"])
    print('gh_commits_json[gh_commits_json_len - 1]["sha"]:', gh_commits_json[gh_commits_json_len - 1]["sha"])
last_commit=gh_commits_json[0]["sha"]
print('last_commit:', last_commit)
prev_commit=gh_commits_json[gh_commits_json_len - 1]["sha"]
print('prev_commit:', prev_commit)

print("get git current commits changes...")
git_cmd_safe_directory = "git config --global --add safe.directory /github/workspace"
git_cmd_safe_directory_returned_value = os.system(git_cmd_safe_directory)
git_cmd_diff = "git diff --name-only " + prev_commit + " " + last_commit
print("git_cmd_diff:", git_cmd_diff)
cmd_pipe = subprocess.Popen(git_cmd_diff, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
for git_response_line in cmd_pipe.stdout.readlines():
  print('git_response_line:', git_response_line)
  print('git_response_line[0:-1]:', git_response_line[0:-1])
  with open(git_response_line[0:-1], 'r') as changed_file:
    try:
      changed_file_yaml = yaml.load(changed_file, Loader=yaml.SafeLoader)
      #print(yaml.safe_load(stream))
      print('changed_file_yaml:', changed_file_yaml)
      for key, value in changed_file_yaml.items():
        print('key:', key)
      #print('changed_file_yaml["Kind"]:', changed_file_yaml["Kind"])
    except yaml.YAMLError as exc:
      print(exc)

print("get kube config...")
kube_cmd_dir = "mkdir ~/.kube"
kube_cmd_dir_returned_value = os.system(kube_cmd_dir)
print('kube_cmd_dir_returned_value:', kube_cmd_dir_returned_value)
kube_cmd_config = "echo $KUBE_CONFIG_DATA | base64 -d > ~/.kube/config"
kube_cmd_config_returned_value = os.system(kube_cmd_config)
print('kube_cmd_config_returned_value:', kube_cmd_config_returned_value)
if LOG == 'DEBUG':
  kube_cmd_config_debug = "cat ~/.kube/config"
  cmd_pipe = subprocess.Popen(kube_cmd_config_debug, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  for kubectl_response_line in cmd_pipe.stdout.readlines():
    print('kubectl_response_line:', kubectl_response_line)
kube_cmd_nodes = "kubectl get nodes"
cmd_pipe = subprocess.Popen(kube_cmd_nodes, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
for kubectl_response_line in cmd_pipe.stdout.readlines():
  print('kubectl_response_line:', kubectl_response_line)

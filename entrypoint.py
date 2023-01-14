#!/usr/bin/python

import os
import subprocess
import json
from my_kubernetes import is_kube_yaml_valid
from my_kubernetes import get_kube_nodes
from my_git import git_safe_directory
from my_git import git_diff_files_list
from my_yaml import yaml_load

LOG = os.getenv('LOG')

print("get github pr comment...")
found_pr_body = 0
gh_full_json_env = os.getenv('GITHUB_FULL_JSON')
gh_full_json = json.loads(gh_full_json_env)
if LOG == 'DEBUG':
  print('gh_full_json:', gh_full_json)
print('gh_full_json["event"]["pull_request"]["body"]:', gh_full_json["event"]["pull_request"]["body"])
if gh_full_json["event"]["pull_request"]["body"] != None:
  found_pr_body = 1
  gh_pr_comment = gh_full_json["event"]["pull_request"]["body"].split("\r\n")
print('found_pr_body:', found_pr_body)

deployment_order_names = {}
if found_pr_body:
  print("parse comment...")
  found_deployment_order = 0
  count = 0
  for pr_comment_line in gh_pr_comment:
    print('pr_comment_line:', pr_comment_line)
    if pr_comment_line == '' and found_deployment_order == 1:
        print("empty string found...")
        break
    if "```" in str(pr_comment_line) and found_deployment_order == 1:
        print("end of comment string found...")
        break
    if found_deployment_order == 1:
      count += 1
      deployment_order_names["pr_comment_line"] = count
      print('count:', count)
      print('pr_comment_line:', pr_comment_line)
      print('deployment_order_names["pr_comment_line"]:', deployment_order_names["pr_comment_line"])
    if "~deployment-order" in str(pr_comment_line):
        print("deployment-order detected...")
        found_deployment_order = 1
else:
  print("comment not found...")
  print("read group file...")
  count = 0
  deployment_order = open('deployment-order-group-priorities', 'r')
  deployment_order_strings = deployment_order.readlines()
  for group_file_line in deployment_order_strings:
    count += 1
    deployment_order_names["group_file_line"] = count
    print('count:', count)
    print('group_file_line:', group_file_line)
    print('deployment_order_names["group_file_line"]:', deployment_order_names["group_file_line"])

print("get git current and previous commits...")
event_name = gh_full_json["event_name"]
print('event_name:', event_name)
event_number = gh_full_json["event"]["number"]
print('event_number:', event_number)
event_action = gh_full_json["event"]["action"]
print('event_action:', event_action)
commits = gh_full_json["event"]["pull_request"]["commits"]
print('commits:', commits)
commits_url = gh_full_json["event"]["pull_request"]["commits_url"]
print('commits_url:', commits_url)
#print('git_cmd_safe_directory_returned_value:', git_cmd_safe_directory_returned_value)
#git_cmd_commits = "gh api -H \"Accept: application/vnd.github+json\" /repos/$GITHUB_REPOSITORY_OWNER/$GITHUB_REPOSITORY_NAME/pulls/$GITHUB_EVENT_NUMBER"
git_cmd_commits = "gh api -H \"Accept: application/vnd.github+json\" " + commits_url 
print('git_cmd_commits:', git_cmd_commits)
cmd_pipe = subprocess.Popen(git_cmd_commits, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#count=0
##commits=[None] * len(2)
#commits=[None] * 2
for changed_file_name in cmd_pipe.stdout.readlines():
  gh_commits_json = json.loads(changed_file_name)
  gh_commits_json_len = len(gh_commits_json)
  if LOG == 'DEBUG':
    print('git_response_line:', changed_file_name)
    print('gh_commits_json_len:', gh_commits_json_len)
    print('gh_commits_json[0]["sha"]:', gh_commits_json[0]["sha"])
    print('gh_commits_json[gh_commits_json_len - 1]["sha"]:', gh_commits_json[gh_commits_json_len - 1]["sha"])
last_commit = gh_commits_json[0]["sha"]
print('last_commit:', last_commit)
prev_commit = gh_commits_json[gh_commits_json_len - 1]["sha"]
print('prev_commit:', prev_commit)

print("get git current commits changes...")
git_safe_directory
changed_files_list = git_diff_files_list(prev_commit, last_commit)
for changed_file_name in changed_files_list:
  if os.path.exists(changed_file_name):
    changed_file_yaml = yaml_load(changed_file_name)
    if is_kube_yaml_valid(changed_file_yaml):
      print("valid YAML file")
    else:
      print("NOT valid YAML file")
  else:
    print("no such file exists at this time")

print("get kube config...")
set_up_kube_config
print("get kube nodes...")
get_kube_nodes
#!/usr/bin/python

import os
import json
from my_kubernetes import set_up_kube_config
from my_kubernetes import get_kube_nodes
from my_kubernetes import is_kube_yaml_valid
from my_git import git_safe_directory
from my_git import git_diff_files_list
from my_github import git_first_last_commit
from my_yaml import yaml_load
from my_yaml import get_yaml_path_key

print("prepare git repository...")
git_safe_directory()
print("get github pr comment...")
found_pr_body = 0
gh_full_json_env = os.getenv('GITHUB_FULL_JSON')
gh_full_json = json.loads(gh_full_json_env)
if os.getenv('LOG') == 'DEBUG':
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
      deployment_order_names[pr_comment_line] = count
      print('count:', count)
      print('pr_comment_line:', pr_comment_line)
      print('deployment_order_names[pr_comment_line]:', deployment_order_names[pr_comment_line])
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
    deployment_order_names[group_file_line] = count
    print('count:', count)
    print('group_file_line:', group_file_line)
    print('deployment_order_names[group_file_line]:', deployment_order_names[group_file_line])
deployment_order_names_len = len(deployment_order_names)
print('deployment_order_names_len:', deployment_order_names_len)
#for deployment_order_name_key, deployment_order_name_value in deployment_order_names:
for deployment_order_name_key, deployment_order_name_value in deployment_order_names.items():
    print('deployment_order_name_key:', deployment_order_name_key)
    print('deployment_order_name_value:', deployment_order_name_value)

print("get git current and previous commits...")
commits = git_first_last_commit()

print("get git current commits changes...")
deleted_files_list = []
changed_files_list = git_diff_files_list(commits[0], commits[1])
print("parse changed files...")
# Initialize 2d array to append to end of array files without 'deployment-order-group' label
# First index number of deployment-order-group sequence
#deployment_order = [None] * len(deployment_order_names)
deployment_order = [[]] * (deployment_order_names_len + 1)
#deployment_order = [None] * deployment_order_names_len
for changed_file_name in changed_files_list:
  print('processing:', changed_file_name)
  if os.path.exists(changed_file_name):
    changed_file_yaml = yaml_load(changed_file_name)
    if isinstance(changed_file_yaml, dict):
      if is_kube_yaml_valid(changed_file_yaml):
        print('changed_file_name valid kube file:', changed_file_name)
        deployment_order_group = get_yaml_path_key(changed_file_yaml, 'metadata.labels.deployment-order-group')
        if deployment_order_group:
          print('fount deployment_order_group:', deployment_order_group)
          deployment_order_group_index_key = 'group:' + deployment_order_group
          print('deployment_order_group_index_key:', deployment_order_group_index_key)
          print('index number deployment_order_names[deployment_order_group_index_key]:', deployment_order_names[deployment_order_group_index_key])
          deployment_order[deployment_order_names[deployment_order_group_index_key]].append(changed_file_name)
        else:
          print('deployment-order-group not found - append to end of array')
          #deployment_order[deployment_order_names_len + 1].append(changed_file_name)
          deployment_order[deployment_order_names_len].append(changed_file_name)
      else:
        print('changed_file_name not valid kube file - skip:', changed_file_name)
    else:
      print('changed_file_name not valid yaml file - skip:', changed_file_name)
  else:
    print('changed_file_name not exist - will check in previous commit:', changed_file_name)
    deleted_files_list.append(changed_file_name)

print("get kube config...")
set_up_kube_config()
print("get kube nodes...")
get_kube_nodes()

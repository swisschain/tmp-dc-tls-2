#!/usr/bin/python

import os
import json
from my_kubernetes import set_up_kube_config
from my_kubernetes import get_kube_nodes
from my_kubernetes import is_kube_yaml_valid
from my_git import git_safe_directory
from my_git import get_git_diff_files_list
from my_github import get_gh_pr_comment
from my_github import get_commit_hash_by_number
from my_github import get_order_list_from_comment
from my_github import get_order_list_from_file
from my_github import initialize_2d_array
from my_github import check_2d_array
from my_yaml import yaml_load
from my_yaml import get_yaml_path_key

print("prepare git repository...")
git_safe_directory()
print("get github pr comment...")
found_pr_body = 0
gh_full_json_env = os.getenv('GITHUB_FULL_JSON')
#print('gh_full_json_env:', gh_full_json_env)
gh_full_json = json.loads(gh_full_json_env)
#if os.getenv('LOG') == 'DEBUG':
#  print('gh_full_json:', gh_full_json)
#print('gh_full_json["event"]["pull_request"]["body"]:', gh_full_json["event"]["pull_request"]["body"])
#if gh_full_json["event"]["pull_request"]["body"] != None:
#  found_pr_body = 1
#  gh_pr_comment = gh_full_json["event"]["pull_request"]["body"].split("\r\n")
#print('found_pr_body:', found_pr_body)
gh_pr_comment = get_gh_pr_comment(gh_full_json)

deployment_order_names = {}
if gh_pr_comment:
  print("parse comment...")
  deployment_order_names = get_order_list_from_comment(gh_pr_comment)
else:
  print("deployment order in comment not found...")
  print("read group file...")
  deployment_order_names = get_order_list_from_file('deployment-order-group-priorities')

print("TEST read group file...")
deployment_order_names_tmp = get_order_list_from_file('deployment-order-group-priorities')
for deployment_order_name_key, deployment_order_name_value in deployment_order_names_tmp.items():
    print('deployment_order_name_key:', deployment_order_name_key)
    print('deployment_order_name_value:', deployment_order_name_value)

deployment_order_names_len = len(deployment_order_names)
if os.getenv('LOG') == 'DEBUG':
    print('deployment_order_names_len:', deployment_order_names_len)
#for deployment_order_name_key, deployment_order_name_value in deployment_order_names:
print("SHOW order array from comment...")
for deployment_order_name_key, deployment_order_name_value in deployment_order_names.items():
    print('deployment_order_name_key:', deployment_order_name_key)
    print('deployment_order_name_value:', deployment_order_name_value)

print("get git current and previous commits...")
gh_token = os.getenv('GITHUB_TOKEN')
commits_url = gh_full_json["event"]["pull_request"]["commits_url"]
commits_count = gh_full_json["event"]["pull_request"]["commits"]
first_commit = get_commit_hash_by_number(gh_token, commits_url, 1)
last_commit = get_commit_hash_by_number(gh_token, commits_url, commits_count)
if os.getenv('LOG') == 'DEBUG':
    print('commits_url:', commits_url)
    print('commits_count:', commits_count)
    print('first_commit:', first_commit)
    print('last_commit:', last_commit)

print("get git current commits changes...")
deleted_files_list = []
changed_files_list = get_git_diff_files_list(first_commit, last_commit)
print("parse changed files...")
# Initialize 2d array to append to end of array files without 'deployment-order-group' label
# First index number of deployment-order-group sequence
#deployment_order = [[]] * (deployment_order_names_len + 1)
deployment_order = initialize_2d_array(len(deployment_order_names) + 1)
#for i in range(len(deployment_order_names) + 1):
#    deployment_order.append([])
#deployment_order = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
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
          print('add to array:', deployment_order_names[deployment_order_group_index_key])
          #c = deployment_order_names[deployment_order_group_index_key]
          #print('c:', c)
          deployment_order[deployment_order_names[deployment_order_group_index_key]].append(changed_file_name)
          #deployment_order[c].append('changed_file_name')
          check_2d_array(deployment_order)
        else:
          print('deployment-order-group not found - append to end of array')
          #deployment_order[deployment_order_names_len + 1].append(changed_file_name)
          print('add to array:', deployment_order_names_len)
          deployment_order[deployment_order_names_len].append(changed_file_name)
          check_2d_array(deployment_order)
      else:
        print('changed_file_name not valid kube file - skip:', changed_file_name)
    else:
      print('changed_file_name not valid yaml file - skip:', changed_file_name)
  else:
    print('changed_file_name not exist - will check in previous commit:', changed_file_name)
    deleted_files_list.append(changed_file_name)
print('Check deployment_order array...')
check_2d_array(deployment_order)
#for deployment_order_number in deployment_order:
#    for deployment_file_number in deployment_order_number:
#        #print('deployment_order_number:', deployment_order_number)
#        print('deployment_file_number:', deployment_file_number)
#        #print('deployment_order[deployment_order_number][deployment_file_number]:', deployment_order[deployment_order_number][deployment_file_number])
#for i in range(len(deployment_order)):
#    for j in range(len(deployment_order[i])):
#        print('i:', i)
#        print('j:', j)
#        print('deployment_order[i][j]:', deployment_order[i][j])

#deployment_order = [['00', '01', '02'], ['10', '11', '12'], ['20', '21', '22']]
#deployment_order[0].append('03')
#deployment_order[2].append('23')
#print('Check TEST deployment_order array...')
#check_2d_array(deployment_order)
#for deployment_order_number in deployment_order:
#    for deployment_file_number in deployment_order_number:
#        #print('deployment_order_number:', deployment_order_number)
#        print('deployment_file_number:', deployment_file_number)
#        #print('deployment_order[deployment_order_number][deployment_file_number]:', deployment_order[deployment_order_number][deployment_file_number])
#for i in range(len(deployment_order)):
#    for j in range(len(deployment_order[i])):
#        print('i:', i)
#        print('j:', j)
#        print('deployment_order[i][j]:', deployment_order[i][j])

#print("get kube config...")
#set_up_kube_config()
#if os.getenv('LOG') == 'DEBUG':
#    print("get kube nodes...")
#    get_kube_nodes()

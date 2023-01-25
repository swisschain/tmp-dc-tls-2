#!/usr/bin/python

import os
import json
from my_common import to_str
from my_common import run_shell_command
from my_common import initialize_array
from my_common import check_2d_array
from my_common import add_string_to_gile
from my_kubernetes import set_up_kube_config
from my_kubernetes import get_kube_nodes
from my_kubernetes import is_kube_object_type_valid
from my_kubernetes import kube_apply_files_list
from my_git import git_safe_directory
from my_git import get_git_switch_to_commit
from my_git import get_git_diff_files_list
from my_github import convert_order_list
from my_github import get_gh_pr_comment
from my_github import add_gh_pr_comment
from my_github import get_git_commit_hash_by_number
from my_github import get_order_list_from_comment
from my_github import get_order_list_from_file

from my_yaml import yaml_load
from my_yaml import get_yaml_path_key

# Set git repository permissions
print("prepare git repository...")
git_safe_directory()
print("get github pr comment...")
# Set pool request comment from GitHub environment variable
gh_full_json_env = os.getenv('GITHUB_FULL_JSON')
gh_full_json = json.loads(gh_full_json_env)
if os.getenv('LOG') == 'DEBUG':
    print('gh_full_json:', gh_full_json)
    print('gh_full_json["event"]["pull_request"]["body"]:', gh_full_json["event"]["pull_request"]["body"])
gh_pr_comment = get_gh_pr_comment(gh_full_json)

# Try to find deployment order in GitHub pool request comment else read it from file
deployment_order_names = {}
if gh_pr_comment:
  print("parse comment...")
  deployment_order_names = get_order_list_from_comment(gh_pr_comment)
else:
  print("deployment order in comment not found...")
  print("read group file...")
  deployment_order_names = get_order_list_from_file('deployment-order-group-priorities')

# Convert array with groups
deployment_order_numbers = convert_order_list(deployment_order_names)
if os.getenv('LOG') == 'DEBUG':
    print('deployment_order_numbers:', deployment_order_numbers)

if os.getenv('LOG') == 'DEBUG':
    print("TEST read group file...")
    deployment_order_names_tmp = get_order_list_from_file('deployment-order-group-priorities')
    print('deployment_order_names_tmp:', deployment_order_names_tmp)

if os.getenv('LOG') == 'DEBUG':
    deployment_order_names_len = len(deployment_order_names)
    print('deployment_order_names_len:', deployment_order_names_len)
print("SHOW order array from comment...")
print('deployment_order_names:', deployment_order_names)

print("get git current and previous commits...")
gh_token = os.getenv('GITHUB_TOKEN')
commits_url = gh_full_json["event"]["pull_request"]["commits_url"]
comments_url = gh_full_json["event"]["pull_request"]["comments_url"]
commits_count = gh_full_json["event"]["pull_request"]["commits"]
first_commit = get_git_commit_hash_by_number(gh_token, commits_url, 1)
last_commit = get_git_commit_hash_by_number(gh_token, commits_url, commits_count)
if os.getenv('LOG') == 'DEBUG':
    print('commits_url:', commits_url)
print('commits_count:', commits_count)
print('first_commit:', first_commit)
print('last_commit:', last_commit)

print("get git current commits changes...")
gh_comment_body_preview = ''
gh_comment_body_details = ''
# Get All
files_list_git_changed = get_git_diff_files_list(first_commit, last_commit, 'All')
# Get Added
files_list_git_added = get_git_diff_files_list(first_commit, last_commit, 'Added')
if files_list_git_added:
    gh_comment_body_preview = gh_comment_body_preview + str(len(files_list_git_added)) + ' added<br>'
for file in files_list_git_added:
    gh_comment_body_details = gh_comment_body_details + '+ ' + to_str(file) + '<br>'
# Get Modified
files_list_git_modified = get_git_diff_files_list(first_commit, last_commit, 'Modified')
if files_list_git_modified:
    gh_comment_body_preview = gh_comment_body_preview + str(len(files_list_git_modified)) + ' modified<br>'
for file in files_list_git_modified:
    gh_comment_body_details = gh_comment_body_details + '~ ' + to_str(file) + '<br>'
# Get Renamed
files_list_git_renamed = get_git_diff_files_list(first_commit, last_commit, 'Renamed')
if files_list_git_renamed:
    gh_comment_body_preview = gh_comment_body_preview + str(len(files_list_git_renamed)) + ' renamed<br>'
for file in files_list_git_renamed:
    gh_comment_body_details = gh_comment_body_details + '~ ' + to_str(file) + '<br>'
# Get Deleted
files_list_git_deleted = get_git_diff_files_list(first_commit, last_commit, 'Deleted')
if files_list_git_deleted:
    gh_comment_body_preview = gh_comment_body_preview + str(len(files_list_git_deleted)) + ' deleted<br>'
for file in files_list_git_deleted:
    gh_comment_body_details = gh_comment_body_details + '- ' + to_str(file) + '<br>'
# Compare
if len(files_list_git_changed) != len(files_list_git_added) + len(files_list_git_modified) + len(files_list_git_renamed) + len(files_list_git_deleted):
    print("Warning: not accounted git diff files!")
    not_accounted = len(files_list_git_changed) - len(files_list_git_added) + len(files_list_git_modified) + len(files_list_git_renamed) + len(files_list_git_deleted)
    gh_comment_body_preview = gh_comment_body_preview + str(not_accounted) + ' UNKNOW<br>'
    print("len(files_list_git_changed):", len(files_list_git_changed))
    print("len(files_list_git_added):", len(files_list_git_added))
    print("len(files_list_git_modified):", len(files_list_git_modified))
    print("len(files_list_git_renamed):", len(files_list_git_renamed))
    print("len(files_list_git_deleted):", len(files_list_git_deleted))
gh_comment_body_details = gh_comment_body_details + '<br><br>Sequence of updating:<br><br>'
print("parse changed files...")
########################################################################################################################
# Initialize two dimensional array 'files_list_deployment_order' to append file names to index number                  #
# founded for deployment-order-group item                                                                              #
# First index - number of deployment-order-group sequence                                                              #
# If kubernetes file type Deployment - add to 'files_list_deployment_order' array                                      #
# If kubernetes file type 'ConfigMap', 'Service' or 'Secret' add to 'files_list_other_types' array                     #
# If file doesn't exist add to 'deleted_files_list' array                                                              #
########################################################################################################################
files_list_deployment_order = initialize_array(len(deployment_order_names))
files_list_deployment_no_group = initialize_array(1)
files_list_other_types = initialize_array(1)
files_list_deleted = initialize_array(1)
for changed_file_name in files_list_git_changed:
    print('processing:', to_str(changed_file_name))
    if os.path.exists(changed_file_name):
        changed_file_yaml = yaml_load(changed_file_name)
        if changed_file_yaml:
            if is_kube_object_type_valid(changed_file_yaml, ['Deployment']):
                if os.getenv('LOG') == 'DEBUG':
                    print('changed_file_name valid kube file:', changed_file_name)
                deployment_order_group = get_yaml_path_key(changed_file_yaml, 'metadata.labels.deployment-order-group')
                if deployment_order_group:
                    deployment_order_group_index_key = 'group:' + deployment_order_group
                    if deployment_order_group_index_key in deployment_order_names:
                        if os.getenv('LOG') == 'DEBUG':
                            print('fount deployment_order_group:', deployment_order_group)
                            print('deployment_order_group_index_key:', deployment_order_group_index_key)
                            print('index number deployment_order_names[deployment_order_group_index_key]:', deployment_order_names[deployment_order_group_index_key])
                            print('add to array:', deployment_order_names[deployment_order_group_index_key])
                        files_list_deployment_order[deployment_order_names[deployment_order_group_index_key]].append(changed_file_name)
                        if os.getenv('LOG') == 'DEBUG':
                            check_2d_array(files_list_deployment_order)
                    else:
                        print('Warning: NOT fount deployment_order_group:', deployment_order_group)
                else:
                    if os.getenv('LOG') == 'DEBUG':
                        print('deployment-order-group not found - append to end of array')
                        print('add to no group array')
                    files_list_deployment_no_group[0].append(changed_file_name)
            elif is_kube_object_type_valid(changed_file_yaml, ['ConfigMap', 'Service', 'Secret']):
                files_list_other_types[0].append(changed_file_name)
            else:
                if os.getenv('LOG') == 'DEBUG':
                    print('changed_file_name not valid kube file - skip:', changed_file_name)
        else:
            if os.getenv('LOG') == 'DEBUG':
                print('changed_file_name not valid yaml file - skip:', changed_file_name)
    else:
        if os.getenv('LOG') == 'DEBUG':
            print('changed_file_name not exist - will check in previous commit:', changed_file_name)
        files_list_deleted[0].append(changed_file_name)
print('Apply to kubernetes...')
hosts_name = os.getenv('HOSTS_NAME')
hosts_ip = os.getenv('HOSTS_IP')
add_string_to_gile('/etc/hosts', hosts_ip + ' ' + hosts_name)
run_shell_command('cat /etc/hosts | grep ' + hosts_name, 'Output=True')
set_up_kube_config()
get_kube_nodes()
gh_comment_body_part = kube_apply_files_list(['group:other'], files_list_other_types)
gh_comment_body_details = gh_comment_body_details + gh_comment_body_part
gh_comment_body_part = kube_apply_files_list(deployment_order_numbers, files_list_deployment_order)
gh_comment_body_details = gh_comment_body_details + gh_comment_body_part
gh_comment_body_part = kube_apply_files_list(['group:no group'], files_list_deployment_no_group)
gh_comment_body_details = gh_comment_body_details + gh_comment_body_part
print('Check files_list_deleted array...')
get_git_switch_to_commit(last_commit)
gh_comment_body_part = kube_apply_files_list(['group:deleted'], files_list_deleted)
gh_comment_body_details = gh_comment_body_details + gh_comment_body_part

print('Combine comment for GitHub pool request...')
gh_comment_body = "<html><body>Previewing update:<br><br>" + gh_comment_body_preview + "<br><details><summary>Details</summary>Previewing update:<br><br>" + gh_comment_body_details + "</details></body></html>"
#gh_comment_body = "<html><body>Previewing update:<br><br><pre><code>" + gh_comment_body_preview + "</code></pre><br><details><summary>Details</summary>Previewing update:<br><br>" + gh_comment_body_details + "</details></body></html>"
add_gh_pr_comment(gh_token, comments_url, gh_comment_body)


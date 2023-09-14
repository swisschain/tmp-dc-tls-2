#!/usr/bin/python

import os
import sys
import json
from my_common import to_str
from my_common import run_shell_command
from my_common import is_path_allowed
from my_common import is_extension_allowed
from my_common import initialize_array
from my_common import check_2d_array
from my_common import add_string_to_file
from my_kubernetes import set_up_kube_config
from my_kubernetes import get_kube_nodes
from my_kubernetes import is_kube_object_type_valid
from my_kubernetes import get_valid_kube_files
from my_kubernetes import kube_apply_files_list
from my_git import git_safe_directory
from my_git import get_git_switch_to_commit
from my_git import get_git_diff_files_list
from my_github import convert_order_list
from my_github import add_gh_pr_comment
from my_github import get_gh_pr_number_from_env
from my_github import get_gh_pr_comment_from_env
from my_github import get_gh_pr_comment_by_pr_id
from my_github import get_gh_commit_hash_by_number
from my_github import create_comments_url_by_pr_id
from my_github import get_order_list_from_comment
from my_github import get_order_list_from_file
from my_yaml import yaml_load
from my_yaml import get_yaml_path_key
from my_json import get_valid_json_files

# Set git repository permissions
print("prepare git repository...")
git_safe_directory()
print("get github pr comment...")
# Get GitHub environment variables
gh_full_json_env = os.getenv('GITHUB_FULL_JSON')
if os.getenv('LOG') == 'DEBUG':
    print('main gh_full_json_env:', gh_full_json_env)
gh_token = os.getenv('GITHUB_TOKEN')
# Load json from full GitHub environment variable
gh_full_json = json.loads(gh_full_json_env)
if os.getenv('LOG') == 'DEBUG':
    print('main gh_full_json:', gh_full_json)
# Get variables from json
event_name = gh_full_json["event_name"]
print('event_name:', event_name)

# Get GitHub pool request comment
gh_pr_number = 0
gh_template_url = ''
gh_pr_comment = ''
if event_name == "pull_request":
    gh_pr_comment = get_gh_pr_comment_from_env(gh_full_json)
if event_name == "push":
    print('Try to parse merge commit message...')
    gh_pr_number_mc = get_gh_pr_number_from_env(gh_full_json, '^Merge pull request #([0-9]+) from .*')
    print('Try to parse squash merge message...')
    gh_pr_number_sm = get_gh_pr_number_from_env(gh_full_json, '^.+\(#([0-9]+)\)')
    # Use gh_template_url to get protocol, server, repository owner and repository name
    gh_template_url = gh_full_json["event"]["repository"]["issues_url"]
    if gh_pr_number_mc:
        gh_pr_number = gh_pr_number_mc
        gh_pr_comment = get_gh_pr_comment_by_pr_id(gh_token, gh_template_url, gh_pr_number_mc)
        if os.getenv('LOG') == 'DEBUG':
            print('main gh_pr_number:', gh_pr_number)
            print('main gh_pr_comment:', gh_pr_comment)
    elif gh_pr_number_sm:
        gh_pr_number = gh_pr_number_sm
        gh_pr_comment = get_gh_pr_comment_by_pr_id(gh_token, gh_template_url, gh_pr_number_sm)
        if os.getenv('LOG') == 'DEBUG':
            print('main gh_pr_number:', gh_pr_number)
            print('main gh_pr_comment:', gh_pr_comment)
    else:
        print("Looks like it is not merge pull request, just simple push - EXIT...")
        exit(0)

# Try to find deployment order in GitHub pool request comment else read it from file
deployment_order_names = {}
if gh_pr_comment:
    print("parse comment...")
    deployment_order_names = get_order_list_from_comment(gh_pr_comment)
    if os.getenv('LOG') == 'DEBUG':
        print('main type(deployment_order_names)', type(deployment_order_names))
        print('main deployment_order_names:', deployment_order_names)
    if isinstance(deployment_order_names, dict):
        if os.getenv('LOG') == 'DEBUG':
            deployment_order_names_len = len(deployment_order_names)
            print('main deployment_order_names_len:', deployment_order_names_len)
        # Convert array with groups
        deployment_order_numbers = convert_order_list(deployment_order_names)
    else:
        print("deployment order in comment not found...")
        print("read group file...")
        deployment_order_names = get_order_list_from_file('deployment-order-group-priorities')
        if os.getenv('LOG') == 'DEBUG':
            print('main type(deployment_order_names)', type(deployment_order_names))
            print('main deployment_order_names:', deployment_order_names)
        if isinstance(deployment_order_names, dict):
            if os.getenv('LOG') == 'DEBUG':
                deployment_order_names_len = len(deployment_order_names)
                print('main deployment_order_names_len:', deployment_order_names_len)
            # Convert array with groups
            deployment_order_numbers = convert_order_list(deployment_order_names)
else:
    print("comment not found...")
    print("read group file...")
    deployment_order_names = get_order_list_from_file('deployment-order-group-priorities')
    if os.getenv('LOG') == 'DEBUG':
        print('main type(deployment_order_names)', type(deployment_order_names))
        print('deployment_order_names:', deployment_order_names)
    if isinstance(deployment_order_names, dict):
        if os.getenv('LOG') == 'DEBUG':
            deployment_order_names_len = len(deployment_order_names)
            print('main deployment_order_names_len:', deployment_order_names_len)
        # Convert array with groups
        deployment_order_numbers = convert_order_list(deployment_order_names)

#if os.getenv('LOG') == 'DEBUG':
#    print("main TEST read group file...")
#    deployment_order_names_tmp = get_order_list_from_file('deployment-order-group-priorities')
#    print('main deployment_order_names_tmp:', deployment_order_names_tmp)

print("get git current and previous commits...")
comments_url = ''
if event_name == "pull_request":
    commits_url = gh_full_json["event"]["pull_request"]["commits_url"]
    comments_url = gh_full_json["event"]["pull_request"]["comments_url"]
    commits_count = gh_full_json["event"]["pull_request"]["commits"]
    print('commits_count:', commits_count)
    first_commit = get_gh_commit_hash_by_number(gh_token, commits_url, 1)
    last_commit = get_gh_commit_hash_by_number(gh_token, commits_url, commits_count)
    if os.getenv('LOG') == 'DEBUG':
        print('main commits_url:', commits_url)
if event_name == "push":
    comments_url = create_comments_url_by_pr_id(gh_template_url, gh_pr_number)
    first_commit = gh_full_json["event"]["before"]
    last_commit = gh_full_json["event"]["after"]
print('first_commit:', first_commit)
print('last_commit:', last_commit)

print("get git all changed files...")
files_list_git_changed = get_git_diff_files_list(first_commit, last_commit, 'All', event_name)
print("start parsing changed files...")
########################################################################################################################
# Initialize two dimensional array 'files_list_deployment_order' to append file names to index number                  #
# founded for deployment-order-group item                                                                              #
# First index - number of deployment-order-group sequence                                                              #
# If kubernetes file type Deployment - add to 'files_list_deployment_order' array                                      #
# If kubernetes file type 'ConfigMap', 'Service' or 'Secret' add to 'files_list_other_types' array                     #
# If file doesn't exist add to 'deleted_files_list' array                                                              #
########################################################################################################################
files_list_other_types = get_valid_kube_files(deployment_order_names, files_list_git_changed, 'OTHER')
files_list_deployment_order = get_valid_kube_files(deployment_order_names, files_list_git_changed, 'WITHGROUP')
files_list_deployment_no_group = get_valid_kube_files(deployment_order_names, files_list_git_changed, 'WITHOUTGROUP')
files_list_not_valid_yamls = get_valid_kube_files(deployment_order_names, files_list_git_changed, 'NOTVALID')
files_list_not_valid_jsons = get_valid_json_files(deployment_order_names, files_list_git_changed, 'NOTVALID')
# get only not founded files, after switch to previous commit will validate them
files_list_probably_deleted = get_valid_kube_files(deployment_order_names, files_list_git_changed, 'DELETED')
print('files_list_other_types:', files_list_other_types)
print('files_list_deployment_order:', files_list_deployment_order)
print('files_list_deployment_no_group:', files_list_deployment_no_group)
print('files_list_not_valid:', files_list_not_valid_yamls)
print('files_list_probably_deleted:', files_list_probably_deleted)
#
print("get git changed files by type of change...")
files_list_git_added = get_git_diff_files_list(first_commit, last_commit, 'Added', event_name)
files_list_git_modified = get_git_diff_files_list(first_commit, last_commit, 'Modified', event_name)
files_list_git_renamed = get_git_diff_files_list(first_commit, last_commit, 'Renamed', event_name)
files_list_git_deleted = get_git_diff_files_list(first_commit, last_commit, 'Deleted', event_name)
#
print("prepare git pool request message...")
gh_comment_body_preview = ''
gh_comment_body_details = ''
# Added files
if files_list_git_added:
    gh_comment_body_preview = gh_comment_body_preview + str(len(files_list_git_added)) + ' added<br>'
for file in files_list_git_added:
    if file in files_list_not_valid_yamls[0]:
        gh_comment_body_details = gh_comment_body_details + '+ ' + to_str(file) + ' (NOT VALID YAML)<br>'
    elif file in files_list_not_valid_jsons[0]:
        gh_comment_body_details = gh_comment_body_details + '+ ' + to_str(file) + ' (NOT VALID JSON)<br>'
    else:
        gh_comment_body_details = gh_comment_body_details + '+ ' + to_str(file) + '<br>'
# Modified files
if files_list_git_modified:
    gh_comment_body_preview = gh_comment_body_preview + str(len(files_list_git_modified)) + ' modified<br>'
for file in files_list_git_modified:
    if file in files_list_not_valid_yamls[0]:
        gh_comment_body_details = gh_comment_body_details + '~ ' + to_str(file) + ' (NOT VALID YAML)<br>'
    elif file in files_list_not_valid_jsons[0]:
        gh_comment_body_details = gh_comment_body_details + '+ ' + to_str(file) + ' (NOT VALID JSON)<br>'
    else:
        gh_comment_body_details = gh_comment_body_details + '~ ' + to_str(file) + '<br>'
# Renamed files
if files_list_git_renamed:
    gh_comment_body_preview = gh_comment_body_preview + str(len(files_list_git_renamed)) + ' renamed<br>'
for file in files_list_git_renamed:
    if file in files_list_not_valid_yamls[0]:
        gh_comment_body_details = gh_comment_body_details + '~ ' + to_str(file) + ' (NOT VALID YAML)<br>'
    elif file in files_list_not_valid_jsons[0]:
        gh_comment_body_details = gh_comment_body_details + '+ ' + to_str(file) + ' (NOT VALID JSON)<br>'
    else:
        gh_comment_body_details = gh_comment_body_details + '~ ' + to_str(file) + '<br>'
# Deleted files
if files_list_git_deleted:
    gh_comment_body_preview = gh_comment_body_preview + str(len(files_list_git_deleted)) + ' deleted<br>'
for file in files_list_git_deleted:
    if file in files_list_not_valid_yamls[0]:
        gh_comment_body_details = gh_comment_body_details + '- ' + to_str(file) + ' (NOT VALID YAML)<br>'
    elif file in files_list_not_valid_jsons[0]:
        gh_comment_body_details = gh_comment_body_details + '+ ' + to_str(file) + ' (NOT VALID JSON)<br>'
    else:
        gh_comment_body_details = gh_comment_body_details + '- ' + to_str(file) + '<br>'
# Compare all with changed by type
if len(files_list_git_changed) != len(files_list_git_added) + len(files_list_git_modified) + len(files_list_git_renamed) + len(files_list_git_deleted):
    print("Warning: not accounted git diff files!")
    not_accounted = len(files_list_git_changed) - len(files_list_git_added) + len(files_list_git_modified) + len(files_list_git_renamed) + len(files_list_git_deleted)
    gh_comment_body_preview = gh_comment_body_preview + str(not_accounted) + ' UNKNOWN TYPE OF CHANGE<br>'
    print("len(files_list_git_changed):", len(files_list_git_changed))
    print("len(files_list_git_added):", len(files_list_git_added))
    print("len(files_list_git_modified):", len(files_list_git_modified))
    print("len(files_list_git_renamed):", len(files_list_git_renamed))
    print("len(files_list_git_deleted):", len(files_list_git_deleted))
# if founded not valid files
if files_list_not_valid_yamls[0] or files_list_not_valid_jsons[0]:
    gh_comment_body_preview = gh_comment_body_preview + '<br>'
    if files_list_not_valid_yamls[0] and files_list_not_valid_jsons[0]:
        gh_comment_body_preview = gh_comment_body_preview + str(len(files_list_not_valid_yamls[0]) + len(files_list_not_valid_jsons[0])) + ' NOT VALID YAML AND JSON FILES FOUNDED - WILL STOP UPDATE!<br>'
    else:
        if files_list_not_valid_yamls[0]:
            gh_comment_body_preview = gh_comment_body_preview + str(
                len(files_list_not_valid_yamls[0])) + ' NOT VALID YAML FILES FOUNDED - WILL STOP UPDATE!<br>'
        if files_list_not_valid_jsons[0]:
            gh_comment_body_preview = gh_comment_body_preview + str(
                len(files_list_not_valid_jsons[0])) + ' NOT VALID JSON FILES FOUNDED - WILL STOP UPDATE!<br>'
    gh_comment_body_details = gh_comment_body_details + '<br><br>Update is stopped!<br><br>'
else:
    gh_comment_body_details = gh_comment_body_details + '<br><br>Sequence of updating:<br><br>'
    if os.getenv('LOG') == 'DEBUG':
        print('main type(deployment_order_numbers)', type(deployment_order_numbers))

    if isinstance(deployment_order_numbers, list):
        print('Apply to kubernetes...')
        hosts_name = os.getenv('HOSTS_NAME')
        hosts_ip = os.getenv('HOSTS_IP')
        add_string_to_file('/etc/hosts', hosts_ip + ' ' + hosts_name)
        run_shell_command('cat /etc/hosts | grep ' + hosts_name, 'Output=True')
        set_up_kube_config()
        get_kube_nodes()
        gh_comment_body_part = kube_apply_files_list(['group:other'], files_list_other_types)
        gh_comment_body_details = gh_comment_body_details + gh_comment_body_part
        gh_comment_body_part = kube_apply_files_list(deployment_order_numbers, files_list_deployment_order)
        gh_comment_body_details = gh_comment_body_details + gh_comment_body_part
        gh_comment_body_part = kube_apply_files_list(['group:no group'], files_list_deployment_no_group)
        gh_comment_body_details = gh_comment_body_details + gh_comment_body_part
        print('Check files_list_deleted array - skip...')
        #get_git_switch_to_commit(last_commit)
        #files_list_deleted = get_valid_kube_files(deployment_order_names, files_list_probably_deleted[0], 'KUBE_VALID  ')
        #print('files_list_deleted:', files_list_deleted)
        #gh_comment_body_part = kube_apply_files_list(['group:deleted'], files_list_deleted)
        #gh_comment_body_details = gh_comment_body_details + gh_comment_body_part
    else:
        print('Skip applying due to empty order...')

print('Combine comment for GitHub pool request...')
if event_name == "pull_request":
    gh_comment_body = "<html><body>Previewing update:<br><br>" + gh_comment_body_preview + "<br><details><summary>Details</summary>Previewing update:<br><br>" + gh_comment_body_details + "</details></body></html>"
    # gh_comment_body = "<html><body>Previewing update:<br><br><pre><code>" + gh_comment_body_preview + "</code></pre><br><details><summary>Details</summary>Previewing update:<br><br>" + gh_comment_body_details + "</details></body></html>"
if event_name == "push":
    gh_comment_body = "<html><body>Applying update:<br><br>" + gh_comment_body_preview + "<br><details><summary>Details</summary>Previewing update:<br><br>" + gh_comment_body_details + "</details></body></html>"
    # gh_comment_body = "<html><body>Previewing update:<br><br><pre><code>" + gh_comment_body_preview + "</code></pre><br><details><summary>Details</summary>Previewing update:<br><br>" + gh_comment_body_details + "</details></body></html>"
# Push comment message to pool request
add_gh_pr_comment(gh_token, comments_url, gh_comment_body)
# Fail pool request action job if we have not valid files
if files_list_not_valid_yamls[0] or files_list_not_valid_jsons[0]:
    sys.exit("Fail pool request action job due to have not valid files")

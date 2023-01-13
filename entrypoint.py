#!/usr/bin/python

import os
import subprocess
import json
import yaml
from my_kubernetes import is_kube_yaml_valid
from my_kubernetes import get_kube_nodes

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
for git_response_line in cmd_pipe.stdout.readlines():
  gh_commits_json = json.loads(git_response_line)
  gh_commits_json_len = len(gh_commits_json)
  if LOG == 'DEBUG':
    print('git_response_line:', git_response_line)
    print('gh_commits_json_len:', gh_commits_json_len)
    print('gh_commits_json[0]["sha"]:', gh_commits_json[0]["sha"])
    print('gh_commits_json[gh_commits_json_len - 1]["sha"]:', gh_commits_json[gh_commits_json_len - 1]["sha"])
last_commit = gh_commits_json[0]["sha"]
print('last_commit:', last_commit)
prev_commit = gh_commits_json[gh_commits_json_len - 1]["sha"]
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
  print('git_response_line.strip():', git_response_line.strip())
  if os.path.exists(git_response_line[0:-1]):
    with open(git_response_line[0:-1], 'r') as changed_file:
      try:
        changed_file_yaml = yaml.load(changed_file, Loader=yaml.SafeLoader)
      except yaml.YAMLError as exc:
        print('yaml file parse exception:', exc)
    print('changed_file_yaml:', changed_file_yaml)
    if isinstance(changed_file_yaml, dict):
      if is_kube_yaml_valid(changed_file_yaml):
        print("valid YAML file")
      else:
        print("NOT valid YAML file")
      changed_file_yaml_len = len(changed_file_yaml)
      print('changed_file_yaml_len:', changed_file_yaml_len)
      print(type(changed_file_yaml))
      #for i in range(0, len(changed_file_yaml)):
      #  print('i:', i)
        #for key, value in changed_file_yaml[i].items():
        #  print(key, ":", value)
        #print('')
      #for key, value in changed_file_yaml.items():
      #  if "kind" in key.lower():
      #  print('Kind key:', value)
      #yaml_kind_key = changed_file_yaml.get("Kind")
      #yaml_kind_key = changed_file_yaml["Kind"]
      #if yaml_kind_key:
      #  print("Kind exist")
      #else:
      #  print("Kind NOT exist")
    #else:
    #  print("NOT valid YAML file")
    #for key, value in changed_file_yaml.items():
    #  print('key:', key)
    #print('changed_file_yaml["Kind"]:', changed_file_yaml["Kind"])
  else:
    print("no such file exists at this time")

get_kube_nodes
#!/usr/bin/python

import os
import subprocess
import json

LOG = "INFO"
LOG = "DEBUG"
gh_cmd = "gh api -H \"Accept: application/vnd.github+json\" /repos/$GITHUB_REPOSITORY_OWNER/$GITHUB_REPOSITORY_NAME/events"
#gh_cmd = "gh api -H \"Accept: application/vnd.github+json\" /repos/$GITHUB_REPOSITORY_OWNER/$GITHUB_REPOSITORY_NAME/pulls/$GITHUB_EVENT_NUMBER"
#git_cmd_commits = "git --no-pager log -2"
#git_cmd_safe_directory = "git config --global --add safe.directory /github/workspace"
#git_cmd_show = "git --no-pager show "
#git_cmd_branch = "git branch -a"
#kube_cmd_debug = "echo KUBE_CONFIG_DATA=$KUBE_CONFIG_DATA && echo $KUBE_CONFIG_DATA | base64 -d > /tmp/config && cat /tmp/config && export KUBECONFIG=/tmp/config && set | grep KUBECONFIG  && kubectl get nodes"
#kube_cmd_info = "echo $KUBE_CONFIG_DATA | base64 -d > /tmp/config"
#kube_cmd_dir = "mkdir ~/.kube"
#kube_cmd_config = "echo $KUBE_CONFIG_DATA | base64 -d > ~/.kube/config"
#kube_cmd_config_debug = "cat ~/.kube/config"
#kube_cmd_nodes = "kubectl get nodes"

print("get github event...")
cmd_pipe = subprocess.Popen(gh_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
for gh_response_line in cmd_pipe.stdout.readlines():
  print('gh_response_line:', gh_response_line)

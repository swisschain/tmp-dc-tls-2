import os
import json
import requests
import subprocess

# Set right git directory permissions
def git_safe_directory():
    git_cmd_safe_directory = "git config --global --add safe.directory /github/workspace"
    responce_code = os.system(git_cmd_safe_directory)
    return responce_code

# Get changed files list
def git_diff_files_list(prev_commit, last_commit):
    git_cmd_diff = "git diff --name-only " + prev_commit + " " + last_commit
    print("git_cmd_diff:", git_cmd_diff)
    cmd_pipe = subprocess.Popen(git_cmd_diff, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    files_list = []
    for git_response_line in cmd_pipe.stdout.readlines():
        print('git_response_line.strip():', git_response_line.strip())
        files_list.append(git_response_line.strip())
    return files_list

# Get first and last commits of pool request
def git_first_last_commit():
    commits = []
    gh_token = os.getenv('GITHUB_TOKEN')
    gh_full_json_env = os.getenv('GITHUB_FULL_JSON')
    gh_full_json = json.loads(gh_full_json_env)
    event_name = gh_full_json["event_name"]
    print('event_name:', event_name)
    event_number = gh_full_json["event"]["number"]
    print('event_number:', event_number)
    event_action = gh_full_json["event"]["action"]
    print('event_action:', event_action)
    commits_count = gh_full_json["event"]["pull_request"]["commits"]
    print('commits_count:', commits_count)
    commits_url = gh_full_json["event"]["pull_request"]["commits_url"]
    print('commits_url:', commits_url)
    print('get first commit')
    commits_url_first_page = commits_url + "?per_page=1&page=1"
    git_cmd_commits = "gh api -H \"Accept: application/vnd.github+json\" " + commits_url_first_page
    print('git_cmd_commits:', git_cmd_commits)
    cmd_pipe = subprocess.Popen(git_cmd_commits, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for changed_file_name in cmd_pipe.stdout.readlines():
        gh_commits_json = json.loads(changed_file_name)
        gh_commits_json_len = len(gh_commits_json)
        #if os.getenv('LOG') == 'DEBUG':
        print('git_response_line:', changed_file_name)
        print('gh_commits_json_len:', gh_commits_json_len)
        print('gh_commits_json[0]["sha"]:', gh_commits_json[0]["sha"])
        #print('gh_commits_json[gh_commits_json_len - 1]["sha"]:', gh_commits_json[gh_commits_json_len - 1]["sha"])
    #commits[0] = gh_commits_json[0]["sha"]
    commits.append(gh_commits_json[0]["sha"])
    print('first_commit:', commits[0])
    print('get last commit')
    commits_url_last_page = commits_url + "?per_page=1&page=" + str(commits_count)
    print('commits_url_last_page:', commits_url_last_page)
    #commits_url_last_page = commits_url + "?page=2&per_page=60"
    #git_cmd_commits = "gh api -H \"Accept: application/vnd.github+json\" " + commits_url_last_page
    #git_cmd_commits = "curl -s -H \"Accept: application/vnd.github+json\" -H \"X-GitHub-Api-Version: 2022-11-28\" -H \"Authorization: Bearer " + gh_token + "\" " + commits_url_last_page
    #print('git_cmd_commits:', git_cmd_commits)
    #headers = {"Authorization": "Bearer MYREALLYLONGTOKENIGOT"}
    headers = {
        'Authorization': 'Bearer ' + str(gh_token),
        'Accept': 'application / vnd.github + json',
        'X-GitHub-Api-Version': '2022-11-28'
            }
    response = requests.get(commits_url_last_page, headers=headers)
    print('response:', response)
    #cmd_pipe = subprocess.Popen(git_cmd_commits, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    #for changed_file_name in cmd_pipe.stdout.readlines():
    #    gh_commits_json = json.loads(changed_file_name)
    #    gh_commits_json_len = len(gh_commits_json)
    #    #if os.getenv('LOG') == 'DEBUG':
    #    print('git_response_line:', changed_file_name)
    #    print('gh_commits_json_len:', gh_commits_json_len)
    #    print('gh_commits_json[0]["sha"]:', gh_commits_json[0]["sha"])
    #    #print('gh_commits_json[gh_commits_json_len - 1]["sha"]:', gh_commits_json[gh_commits_json_len - 1]["sha"])
    #commits[1] = gh_commits_json[0]["sha"]
    #commits.append(gh_commits_json[0]["sha"])
    #print('last_commit:', commits[1])

    return commits

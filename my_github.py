import os
import json
import requests

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
    headers = {
        'Authorization': 'Bearer ' + str(gh_token),
        'Accept': 'application / vnd.github + json',
        'X-GitHub-Api-Version': '2022-11-28'
            }
    print('get first commit')
    commits_url_first_page = commits_url + "?per_page=1&page=1"
    print('commits_url_first_page:', commits_url_first_page)
    gh_commits = requests.get(commits_url_first_page, headers=headers)
    print('gh_commits_json:', gh_commits)
    gh_commits_json = gh_commits.json()
    print('gh_commits_json:', gh_commits_json)
    commits.append(gh_commits_json[0]["sha"])
    print('first_commit:', commits[0])
    print('get last commit')
    commits_url_last_page = commits_url + "?per_page=1&page=" + str(commits_count)
    print('commits_url_last_page:', commits_url_last_page)
    gh_commits = requests.get(commits_url_last_page, headers=headers)
    print('gh_commits_json:', gh_commits)
    gh_commits_json = gh_commits.json()
    print('gh_commits_json:', gh_commits_json)
    commits.append(gh_commits_json[0]["sha"])
    print('last_commit:', commits[1])

    return commits

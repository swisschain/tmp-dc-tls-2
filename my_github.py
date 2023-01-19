import os
#import json
import requests

# Get commit hash id by number
def get_commit_hash_by_number(gh_token, gh_url, gh_pr_commit_number):
    headers = {
        'Authorization': 'Bearer ' + str(gh_token),
        'Accept': 'application / vnd.github + json',
        'X-GitHub-Api-Version': '2022-11-28'
            }
    gh_url_with_page = gh_url + "?per_page=1&page=" + str(gh_pr_commit_number)
    gh_response = requests.get(gh_url_with_page, headers=headers)
    gh_response_json = gh_response.json()
    if os.getenv('LOG') == 'DEBUG':
        print('gh_url_with_page:', gh_url_with_page)
        print('gh_response_json:', gh_response_json)

    return gh_response_json[0]["sha"]

def get_gh_pr_comment(gh_full_json):
    if os.getenv('LOG') == 'DEBUG':
        print('gh_full_json["event"]["pull_request"]["body"]:', gh_full_json["event"]["pull_request"]["body"])
    if gh_full_json["event"]["pull_request"]["body"] != None:
         gh_pr_comment = gh_full_json["event"]["pull_request"]["body"].split("\r\n")
         if os.getenv('LOG') == 'DEBUG':
             print('gh_full_json["event"]["pull_request"]["body"]:', gh_full_json["event"]["pull_request"]["body"])
         return gh_pr_comment

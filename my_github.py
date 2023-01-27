import os
import re
import requests

# Get commit hash id by number
def get_gh_commit_hash_by_number(gh_token, gh_url, gh_pr_commit_number):
    headers = {
        'Authorization': 'Bearer ' + str(gh_token),
        'Accept': 'application / vnd.github + json',
        'X-GitHub-Api-Version': '2022-11-28'
            }
    gh_url_with_page = gh_url + "?per_page=1&page=" + str(gh_pr_commit_number)
    gh_response = requests.get(gh_url_with_page, headers=headers)
    gh_response_json = gh_response.json()
    if os.getenv('LOG') == 'DEBUG':
        print('get_gh_commit_hash_by_number gh_url_with_page:', gh_url_with_page)
        print('get_gh_commit_hash_by_number gh_response_json:', gh_response_json)

    return gh_response_json[0]["sha"]

# Get commit hash id by number
def add_gh_pr_comment(gh_token, gh_url, gh_comment_body):
    headers = {
        'Authorization': 'Bearer ' + str(gh_token),
        'Accept': 'application / vnd.github + json',
        'X-GitHub-Api-Version': '2022-11-28'
            }
    gh_comment = '{"body": "' + gh_comment_body + '"}'
    gh_response = requests.post(gh_url, data=gh_comment, headers=headers)
    gh_response_json = gh_response.json()
    if os.getenv('LOG') == 'DEBUG':
        print('add_gh_pr_comment gh_response_json:', gh_response_json)

# Get commit comment message by pool request number
def get_gh_pr_comment_by_pr_id(gh_token, gh_url, gh_pr_number):
    headers = {
        'Authorization': 'Bearer ' + str(gh_token),
        'Accept': 'application / vnd.github + json',
        'X-GitHub-Api-Version': '2022-11-28'
            }
    gh_url_array = gh_url.split("/")
    gh_url_protocol = gh_url_array[0]
    gh_url_server = gh_url_array[2]
    gh_url_owner = gh_url_array[4]
    gh_url_repo = gh_url_array[5]
    #gh_comments_url = gh_url_protocol + "//" + gh_url_server + '/repos/' + gh_url_owner + '/' + gh_url_repo \
    #                  + '/issues/' + str(gh_pr_number) + '/comments'
    gh_comments_url = gh_url_protocol + "//" + gh_url_server + '/repos/' + gh_url_owner + '/' + gh_url_repo \
                      + '/pulls/' + str(gh_pr_number)
    gh_response = requests.get(gh_comments_url, headers=headers)
    gh_response_json = gh_response.json()
    if os.getenv('LOG') == 'DEBUG':
        print('gh_url:', gh_url)
        print('gh_url_array:', gh_url_array)
        print('gh_url_protocol:', gh_url_protocol)
        print('gh_url_server:', gh_url_server)
        print('gh_url_owner:', gh_url_owner)
        print('gh_url_repo:', gh_url_repo)
        print('gh_comments_url:', gh_comments_url)
        print('gh_response:', gh_response)
        print('gh_response_json:', gh_response_json)

    return gh_response_json

#
def get_gh_pr_comment(gh_token, gh_full_json):
    gh_pr_comment = ''
    event_name = gh_full_json["event_name"]
    if event_name == "pull_request":
        if os.getenv('LOG') == 'DEBUG':
            print('get_gh_pr_comment gh_full_json["event"]["pull_request"]["body"]:',
                  gh_full_json["event"]["pull_request"]["body"])
        if gh_full_json["event"]["pull_request"]["body"] != None:
            gh_pr_comment = gh_full_json["event"]["pull_request"]["body"].split("\r\n")
    if event_name == "push":
        gh_event_message_regexp = re.search('^Merge pull request #([0-9]+) from .*',
                                            gh_full_json["event"]["head_commit"]["message"])
        if os.getenv('LOG') == 'DEBUG':
            print('gh_event_message_regexp:', gh_event_message_regexp)
        gh_pr_number = gh_event_message_regexp.group(1)
        print('gh_pr_number:', gh_pr_number)
        gh_url = gh_full_json["event"]["repository"]["issues_url"]
        gh_pr_comment_json = get_gh_pr_comment_by_pr_id(gh_token, gh_url, gh_pr_number)
        if gh_pr_comment_json["body"] != None:
            gh_pr_comment = gh_pr_comment_json["body"].split("\r\n")

    return gh_pr_comment

#
def get_order_list_from_comment(gh_pr_comment):
    order_list = {}
    found_order_list = 0
    count = 0
    for pr_comment_line in gh_pr_comment:
        if os.getenv('LOG') == 'DEBUG':
            print('get_order_list_from_comment pr_comment_line:', pr_comment_line)
        if pr_comment_line == '' and found_order_list == 1:
            if os.getenv('LOG') == 'DEBUG':
                print("get_order_list_from_comment empty string found...")
            break
        if "```" in str(pr_comment_line) and found_order_list == 1:
            if os.getenv('LOG') == 'DEBUG':
                print("get_order_list_from_comment end of comment string found...")
            break
        if found_order_list == 1:
            if "group:" in str(pr_comment_line):
                order_list[pr_comment_line] = count
                count += 1
            else:
                if os.getenv('LOG') == 'DEBUG':
                    print('get_order_list_from_comment not valid pr_comment_line:', pr_comment_line)
            if os.getenv('LOG') == 'DEBUG':
                print('get_order_list_from_comment count:', count)
                print('get_order_list_from_comment pr_comment_line:', pr_comment_line)
                #print('order_list[pr_comment_line]:', order_list[pr_comment_line])
        if "~deployment-order" in str(pr_comment_line):
            print("deployment-order detected...")
            found_order_list = 1
    if found_order_list:
        return order_list

def get_order_list_from_file(deployment_order_file):
    order_list = {}
    count = 0
    deployment_order = open(deployment_order_file, 'r')
    deployment_order_strings = deployment_order.readlines()
    for group_file_line in deployment_order_strings:
        if "group:" in str(group_file_line.strip()):
            order_list[group_file_line.strip()] = count
            count += 1
        else:
            if os.getenv('LOG') == 'DEBUG':
                print('get_order_list_from_file not valit group_file_line.strip():', group_file_line.strip())
        if os.getenv('LOG') == 'DEBUG':
            print('get_order_list_from_file count:', count)
            print('get_order_list_from_file group_file_line.strip():', group_file_line.strip())
            print('get_order_list_from_file order_list[group_file_line.strip()]:', order_list[group_file_line.strip()])
    return order_list

def convert_order_list(deployment_order_names):
    if os.getenv('LOG') == 'DEBUG':
        print('convert_order_list len(deployment_order_names):', len(deployment_order_names))
    converted_array = [None] * len(deployment_order_names)
    for deployment_order_name_key, deployment_order_name_value in deployment_order_names.items():
        if os.getenv('LOG') == 'DEBUG':
            print('convert_order_list deployment_order_name_key:', deployment_order_name_key)
            print('convert_order_list deployment_order_name_value:', deployment_order_name_value)
        converted_array[deployment_order_name_value] = deployment_order_name_key
    return converted_array


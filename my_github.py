import os
import requests

# Get commit hash id by number
def get_git_commit_hash_by_number(gh_token, gh_url, gh_pr_commit_number):
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
    #if os.getenv('LOG') == 'DEBUG':
    print('gh_response_json:', gh_response_json)


def get_gh_pr_comment(gh_full_json):
    if os.getenv('LOG') == 'DEBUG':
        print('gh_full_json["event"]["pull_request"]["body"]:', gh_full_json["event"]["pull_request"]["body"])
    if gh_full_json["event"]["pull_request"]["body"] != None:
         gh_pr_comment = gh_full_json["event"]["pull_request"]["body"].split("\r\n")
         if os.getenv('LOG') == 'DEBUG':
             print('gh_full_json["event"]["pull_request"]["body"]:', gh_full_json["event"]["pull_request"]["body"])
         return gh_pr_comment

def get_order_list_from_comment(gh_pr_comment):
    order_list = {}
    found_order_list = 0
    count = 0
    for pr_comment_line in gh_pr_comment:
        if os.getenv('LOG') == 'DEBUG':
            print('pr_comment_line:', pr_comment_line)
        if pr_comment_line == '' and found_order_list == 1:
            if os.getenv('LOG') == 'DEBUG':
                print("empty string found...")
            break
        if "```" in str(pr_comment_line) and found_order_list == 1:
            if os.getenv('LOG') == 'DEBUG':
                print("end of comment string found...")
            break
        if found_order_list == 1:
            if "group:" in str(pr_comment_line):
                order_list[pr_comment_line] = count
                count += 1
            else:
                if os.getenv('LOG') == 'DEBUG':
                    print('not valid pr_comment_line:', pr_comment_line)
            if os.getenv('LOG') == 'DEBUG':
                print('count:', count)
                print('pr_comment_line:', pr_comment_line)
                print('order_list[pr_comment_line]:', order_list[pr_comment_line])
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
                print('not valit group_file_line.strip():', group_file_line.strip())
        if os.getenv('LOG') == 'DEBUG':
            print('count:', count)
            print('group_file_line.strip():', group_file_line.strip())
            print('order_list[group_file_line.strip()]:', order_list[group_file_line.strip()])
    return order_list

def convert_order_list(deployment_order_names):
    if os.getenv('LOG') == 'DEBUG':
        print('len(deployment_order_names):', len(deployment_order_names))
    converted_array = [None] * len(deployment_order_names)
    for deployment_order_name_key, deployment_order_name_value in deployment_order_names.items():
        if os.getenv('LOG') == 'DEBUG':
            print('deployment_order_name_key:', deployment_order_name_key)
            print('deployment_order_name_value:', deployment_order_name_value)
        converted_array[deployment_order_name_value] = deployment_order_name_key
    return converted_array


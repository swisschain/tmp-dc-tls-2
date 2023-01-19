import os
import subprocess

# Set right git directory permissions
def git_safe_directory():
    git_cmd_safe_directory = "git config --global --add safe.directory /github/workspace"
    responce_code = os.system(git_cmd_safe_directory)
    return responce_code

# Get changed files list
def get_git_diff_files_list(prev_commit, last_commit):
    git_cmd_diff = "git diff --name-only " + prev_commit + " " + last_commit
    print("git_cmd_diff:", git_cmd_diff)
    cmd_pipe = subprocess.Popen(git_cmd_diff, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    files_list = []
    for git_response_line in cmd_pipe.stdout.readlines():
        print('git_response_line.strip():', git_response_line.strip())
        files_list.append(git_response_line.strip())
    return files_list

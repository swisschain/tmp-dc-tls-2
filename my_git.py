import os
import subprocess
from my_common import to_str
from my_common import run_shell_command

# Set right git directory permissions
def git_safe_directory():
    git_cmd_safe_directory = "git config --global --add safe.directory /github/workspace"
    responce_code = os.system(git_cmd_safe_directory)
    return responce_code

# Switch (checkout) to commit
def get_git_switch_to_commit(commit):
    run_shell_command('git checkout ' + commit, 'Output=True')

# Get changed files list
def get_git_diff_files_list(prev_commit, last_commit, operations_type, event_name):
    git_diff_filter = {
        "Added": "A",
        "Modified": "M",
        "Deleted": "D",
        "Renamed": "R",
        "All": "ALL"
    }
    if git_diff_filter[operations_type] == 'ALL':
        if event_name == "pull_request":
            # Use '^' at the end of commit to include files from this commit
            git_cmd_diff = "git diff --name-only " + prev_commit + "^ " + last_commit
        if event_name == "push":
            git_cmd_diff = "git diff --name-only " + prev_commit + " " + last_commit
    else:
        if event_name == "pull_request":
            # Use '^' at the end of commit to include files from this commit
            git_cmd_diff = "git diff --diff-filter=" + git_diff_filter[operations_type] + " --name-only " + prev_commit + "^ " + last_commit
        if event_name == "push":
            git_cmd_diff = "git diff --diff-filter=" + git_diff_filter[operations_type] + " --name-only " + prev_commit + " " + last_commit
    if os.getenv('LOG') == 'DEBUG':
        print("get_git_diff_files_list git_cmd_diff:", git_cmd_diff)
    cmd_pipe = subprocess.Popen(git_cmd_diff, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    files_list = []
    for git_response_line in cmd_pipe.stdout.readlines():
        if os.getenv('LOG') == 'DEBUG':
            print('get_git_diff_files_list add file:', git_response_line.strip())
        files_list.append(git_response_line.strip())
    print('Files list ' + operations_type + ':', files_list)
    return files_list

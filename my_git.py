import os
import subprocess

# Set right git directory permissions
def git_safe_directory():
    git_cmd_safe_directory = "git config --global --add safe.directory /github/workspace"
    responce_code = os.system(git_cmd_safe_directory)
    return responce_code

# Get changed files list
def get_git_diff_files_list(prev_commit, last_commit):
    allowed_extensions = ['yaml', 'yml']
    git_cmd_diff = "git diff --name-only " + prev_commit + " " + last_commit
    if os.getenv('LOG') == 'DEBUG':
        print("git_cmd_diff:", git_cmd_diff)
    cmd_pipe = subprocess.Popen(git_cmd_diff, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    files_list = []
    for git_response_line in cmd_pipe.stdout.readlines():
        found_extension = 0
        for allowed_extension in allowed_extensions:
            if str(allowed_extension.lower()) in str(git_response_line.strip().lower()):
                if os.getenv('LOG') == 'DEBUG':
                    print('add file:', git_response_line.strip())
                files_list.append(git_response_line.strip())
                found_extension = 1
                break
        if os.getenv('LOG') == 'DEBUG':
            if found_extension == 0:
                print('skip file - not fount in allowed_extensions list:', git_response_line.strip())
    return files_list

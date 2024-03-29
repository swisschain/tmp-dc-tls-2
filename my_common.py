import os
import re
import subprocess


# Run Shell command
def run_shell_command(command, output_flag):
    if os.getenv('LOG') == 'DEBUG':
        print('run_shell_command SHELL run command:', command)
    if output_flag == "Output=False":
        command_returned_value = os.system(command)
        if os.getenv('LOG') == 'DEBUG':
            print('run_shell_command command_returned_value:', command_returned_value)
    else:
        cmd_pipe = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        command_returned_value = cmd_pipe.returncode
        for command_response_line in cmd_pipe.stdout.readlines():
            print('run_shell_command SHELL:', to_str(command_response_line))
        if os.getenv('LOG') == 'DEBUG':
            print('run_shell_command command_returned_value:', command_returned_value)
    return command_returned_value


# Convert from byte string to character Unicode string
def to_str(byte_string):
    encoding = 'utf-8'
    decoded_string = str(byte_string, encoding).strip()
    return decoded_string


# Print two dimensional array
def check_2d_array(array):
    for array_1d in array:
        for array_2d in array_1d:
            # print('array_1d:', array_1d)
            print('file:', array_2d)


# Initialize two dimensional array to assigning random index values
def initialize_array(elements_cont):
    new_array = []
    for element in range(elements_cont):
        new_array.append([])
    return new_array


# Append string to file
def add_string_to_file(file, string):
    with open(file, "a") as myfile:
        myfile.write(string)


# Replace text in file
def replace_text_in_file(file, search_text, replace_text):
    with open(file, 'r') as ro:
        data = ro.read()
        data = data.replace(search_text, replace_text)
    with open(file, 'w') as rw:
        rw.write(data)


# Check if file extension allowed
def is_extension_allowed(file_name, allowed_extensions):
    #allowed_extensions = ['.yaml', '.yml']
    if os.getenv('LOG') == 'DEBUG':
        print('is_extension_allowed check file: ', file_name, ' for: ', allowed_extensions)
    for extension_item in allowed_extensions:
        extension = extension_item.lower()
        file_name_string = to_str(file_name).lower()
        if file_name_string.endswith(extension):
            if os.getenv('LOG') == 'DEBUG':
                print('is_extension_allowed found extension:', extension)
            return True
    return False


# Check if file path allowed
def is_path_allowed(file_name):
    allowed_paths = [r'kubernetes/.*', r'helm/.*/settings/']
    for path_item in allowed_paths:
        if re.search(path_item, to_str(file_name)):
            return True

    return False

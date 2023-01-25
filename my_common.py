import os
import subprocess

# Run Shell command
def run_shell_command(command, output_flag):
    if output_flag == "Output=False":
        command_returned_value = os.system(command)
        if os.getenv('LOG') == 'DEBUG':
            print('command_returned_value:', command_returned_value)
        return command_returned_value
    else:
        cmd_pipe = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if os.getenv('LOG') == 'DEBUG':
            print('SHELL run command:', command)
        for command_response_line in cmd_pipe.stdout.readlines():
            print('SHELL:', to_str(command_response_line))

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

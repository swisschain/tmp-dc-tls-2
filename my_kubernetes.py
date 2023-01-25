import os
import subprocess
from my_common import to_str
from my_common import run_shell_command

# Create kubernetes config
def set_up_kube_config():
    run_shell_command('[ -d ~/.kube ] || mkdir ~/.kube', 'Output=False')
    run_shell_command('echo $KUBE_CONFIG_DATA | base64 -d > ~/.kube/config', 'Output=False')
    if os.getenv('LOG') == 'DEBUG':
        run_shell_command('cat ~/.kube/config', 'Output=True')

# Print kubernetes nodes
def get_kube_nodes():
    run_shell_command('kubectl get nodes', 'Output=True')

# Check kubernetes Kind type function
def is_kube_object_type_valid(file_yaml, kind_types):
    for yaml_key, yaml_value in file_yaml.items():
        if os.getenv('LOG') == 'DEBUG':
            print('yaml_key:', yaml_key)
        if "kind" in str(yaml_key).lower():
            if os.getenv('LOG') == 'DEBUG':
                print('Found Kind Key with yaml_value:', yaml_value)
            for kind_type in kind_types:
                if os.getenv('LOG') == 'DEBUG':
                    print('kind_type:', kind_type)
                if kind_type.lower() == yaml_value.lower():
                    return True

    return False

def kube_apply_files_list(deployment_order_numbers, files_list_deployment_order):
    gh_comment_body_part = ''
    for order_number in range(len(deployment_order_numbers)):
        print('APPLY:', str(deployment_order_numbers[order_number]))
        for file_item in files_list_deployment_order[order_number]:
            print('FILE:', to_str(file_item))
            run_shell_command("kubectl apply --dry-run='client' -f " + to_str(file_item), 'Output=True')
            run_shell_command("kubectl apply --dry-run='server' -f " + to_str(file_item), 'Output=True')
            if os.getenv('DRY_RUN') == 'False':
                run_shell_command("kubectl apply -f " + to_str(file_item), 'Output=True')
            gh_comment_body_part = gh_comment_body_part + to_str(file_item) + ' (' + str(deployment_order_numbers[order_number]) + ')<br>'
    return gh_comment_body_part
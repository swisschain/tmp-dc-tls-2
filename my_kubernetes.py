import os
import subprocess
from my_yaml import yaml_load
from my_yaml import get_yaml_path_key
from my_common import to_str
from my_common import run_shell_command
from my_common import initialize_array
from my_common import is_path_allowed
from my_common import is_extension_allowed
from my_common import replace_text_in_file

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
            print('is_kube_object_type_valid yaml_key:', yaml_key)
        if "kind" in str(yaml_key).lower():
            if os.getenv('LOG') == 'DEBUG':
                print('is_kube_object_type_valid Found Kind Key with yaml_value:', yaml_value)
            for kind_type in kind_types:
                if os.getenv('LOG') == 'DEBUG':
                    print('is_kube_object_type_valid kind_type:', kind_type)
                if kind_type.lower() == yaml_value.lower():
                    return True

    return False

# Sort kubernetes files
def get_valid_kube_files(deployment_order_names, files_list_git_changed, type):
    # type can be OTHER WITHGROUP WITHOUTGROUP DELETED KUBE_VALID NOTVALID
    # KUBE_VALID - only validate, without check order groups
    # NOTVALID - validate and add to not valid array
    #print('get_valid_kube_files')
    #print('deployment_order_names:', deployment_order_names)
    #print('files_list_git_changed:', files_list_git_changed)
    result_array = initialize_array(len(deployment_order_names))
    for changed_file_name in files_list_git_changed:
        if os.getenv('LOG') == 'DEBUG':
            print('get_valid_kube_files processing: ' + to_str(changed_file_name) + ' type: ' + type)
        if os.path.exists(changed_file_name):
            if is_path_allowed(changed_file_name):
                if is_extension_allowed(changed_file_name, ['.yaml', '.yml']):
                    changed_file_yaml = yaml_load(changed_file_name)
                    if changed_file_yaml == None:
                        print('trying to fix file - replacing tabs...')
                        replace_text_in_file(changed_file_name, '\t', ' ')
                        changed_file_yaml = yaml_load(changed_file_name)
                        if type == 'NOTVALID':
                            print('get_valid_kube_files not valid yaml file - NOTVALID (' + to_str(changed_file_name) + ')')
                            result_array[0].append(changed_file_name)
                    if changed_file_yaml:
                        if is_kube_object_type_valid(changed_file_yaml, ['Deployment']):
                            if os.getenv('LOG') == 'DEBUG':
                                print('get_valid_kube_files changed_file_name valid kube file:', changed_file_name)
                            if type == 'KUBE_VALID':
                                print('get_valid_kube_files deployment - KUBE_VALID (' + to_str(changed_file_name) + ')')
                                result_array[0].append(changed_file_name)
                            deployment_order_group = get_yaml_path_key(changed_file_yaml, 'metadata.labels.deployment-order-group')
                            if deployment_order_group:
                                deployment_order_group_index_key = 'group:' + deployment_order_group
                                if deployment_order_group_index_key in deployment_order_names:
                                    if os.getenv('LOG') == 'DEBUG':
                                        print('get_valid_kube_files fount deployment_order_group:', deployment_order_group)
                                        print('get_valid_kube_files deployment_order_group_index_key:', deployment_order_group_index_key)
                                        print('get_valid_kube_files index number deployment_order_names[deployment_order_group_index_key]:', deployment_order_names[deployment_order_group_index_key])
                                    if type == 'WITHGROUP':
                                        print('get_valid_kube_files deployment - WITHGROUP (array[' + str(deployment_order_names[deployment_order_group_index_key]) + '] = ' + to_str(changed_file_name) + ')')
                                        result_array[deployment_order_names[deployment_order_group_index_key]].append(changed_file_name)
                                    #if os.getenv('LOG') == 'DEBUG':
                                    #    check_2d_array(files_list_deployment_order)
                                else:
                                    if type == 'WITHGROUP':
                                        print('Warning: NOT fount deployment order group:', deployment_order_group)
                            else:
                                #if os.getenv('LOG') == 'DEBUG':
                                if type == 'WITHOUTGROUP':
                                    print('get_valid_kube_files deployment - WITHOUTGROUP (' + to_str(changed_file_name) + ')')
                                    result_array[0].append(changed_file_name)
                        elif is_kube_object_type_valid(changed_file_yaml, ['ConfigMap', 'Service', 'Secret']):
                            if type == 'OTHER':
                                print('get_valid_kube_files not deployment - OTHER (' + to_str(changed_file_name) + ')')
                                result_array[0].append(changed_file_name)
                            if type == 'KUBE_VALID':
                                print('get_valid_kube_files not deployment - KUBE_VALID (' + to_str(changed_file_name) + ')')
                                result_array[0].append(changed_file_name)
                        else:
                            if os.getenv('LOG') == 'DEBUG':
                                print('get_valid_kube_files not valid kube file - skip')
                    else:
                        if os.getenv('LOG') == 'DEBUG':
                            print('get_valid_kube_files yaml not valid - skip')
                else:
                    if os.getenv('LOG') == 'DEBUG':
                        print('get_valid_kube_files extensions not allowed - skip')
            else:
                if os.getenv('LOG') == 'DEBUG':
                    print('get_valid_kube_files path file begins from not allowed path - skip')
        else:
            if os.getenv('LOG') == 'DEBUG':
                print('get_valid_kube_files not exist')
            if type == 'DELETED':
                print('get_valid_kube_files not exist - DELETED (' + to_str(changed_file_name) + ')')
                result_array[0].append(changed_file_name)
    return result_array

# Apply kubernetes one file
def kube_apply_file(int_file_item):
    fail_check_flag = 0
    int_gh_comment_body_part = ''
    int_errors_dry_run_client = []
    int_errors_dry_run_server = []
    int_errors_apply = []
    print('kube_apply_files_list FILE:', to_str(int_file_item))
    int_gh_comment_body_part = int_gh_comment_body_part + to_str(int_file_item) + ' (' + str(
        deployment_order_numbers[order_number]) + ')'
    if run_shell_command("kubectl delete --dry-run='server' -f " + to_str(int_file_item), 'Output=False'):
        kubectl_command = 'create'
        if os.getenv('LOG') == 'DEBUG':
            print(f'kubernetes object from file {file_name} not exist - will {kubectl_command}')
    else:
        kubectl_command = 'replace'
        if os.getenv('LOG') == 'DEBUG':
            print(f'kubernetes object from file {file_name} already exist - will {kubectl_command}')
    if run_shell_command(f'kubectl {kubectl_command} --dry-run=client -f {to_str(int_file_item)}', 'Output=False'):
        fail_check_flag = 1
        int_errors_dry_run_client.append(int_file_item)
        int_gh_comment_body_part = int_gh_comment_body_part + '(DRY RUN CLIENT ERROR)'
    if run_shell_command(f'kubectl {kubectl_command} --dry-run=server -f {to_str(int_file_item)}', 'Output=False'):
        fail_check_flag = 1
        int_errors_dry_run_server.append(int_file_item)
        int_gh_comment_body_part = int_gh_comment_body_part + '(DRY RUN SERVER ERROR)'
    if fail_check_flag:
        int_gh_comment_body_part = int_gh_comment_body_part + '(WILL NOT BE UPDATED)'
    if os.getenv('DRY_RUN').lower() == 'false':
        if fail_check_flag:
            print('kube_apply_files_list skip applying FILE:', to_str(int_file_item), 'due to fail dry-run checks')
            int_gh_comment_body_part = int_gh_comment_body_part + '(SKIP UPDATING)'
        else:
            if run_shell_command(f'kubectl apply -f {to_str(int_file_item)}', 'Output=True'):
                int_errors_apply.append(int_file_item)
                int_gh_comment_body_part = int_gh_comment_body_part + '(DEPLOY ERROR)'
    return (int_gh_comment_body_part, int_errors_dry_run_client, int_errors_dry_run_server, int_errors_apply)


# Apply kubernetes files
def kube_apply_files_list(deployment_order_numbers, files_list_deployment_order):
    result_gh_comment_body_part = ''
    result_errors_dry_run_client = []
    result_errors_dry_run_server = []
    result_errors_apply = []
    for order_number in range(len(deployment_order_numbers)):
        print('kube_apply_files_list APPLY:', str(deployment_order_numbers[order_number]))
        for file_item in files_list_deployment_order[order_number]:
            if 'worker' in to_str(file_item).lower():
                (gh_comment_body_part, errors_dry_run_client, errors_dry_run_server, errors_apply) = kube_apply_file(file_item)
                result_gh_comment_body_part = result_gh_comment_body_part + gh_comment_body_part
                result_errors_dry_run_client = result_errors_dry_run_client + errors_dry_run_client
                result_errors_dry_run_server = result_errors_dry_run_server + errors_dry_run_server
                result_errors_apply = result_errors_apply + errors_apply
        for file_item in files_list_deployment_order[order_number]:
            if 'worker' not in to_str(file_item).lower():
                (gh_comment_body_part, errors_dry_run_client, errors_dry_run_server, errors_apply) = kube_apply_file(file_item)
                result_gh_comment_body_part = result_gh_comment_body_part + gh_comment_body_part
                result_errors_dry_run_client = result_errors_dry_run_client + errors_dry_run_client
                result_errors_dry_run_server = result_errors_dry_run_server + errors_dry_run_server
                result_errors_apply = result_errors_apply + errors_apply

    return (result_gh_comment_body_part, result_errors_dry_run_client, result_errors_dry_run_server, result_errors_apply)
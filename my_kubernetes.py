import os
import subprocess

# Create kubernetes config
def set_up_kube_config():
    kube_cmd_dir = "mkdir ~/.kube"
    kube_cmd_dir_returned_value = os.system(kube_cmd_dir)
    print('kube_cmd_dir_returned_value:', kube_cmd_dir_returned_value)
    kube_cmd_config = "echo $KUBE_CONFIG_DATA | base64 -d > ~/.kube/config"
    kube_cmd_config_returned_value = os.system(kube_cmd_config)
    print('kube_cmd_config_returned_value:', kube_cmd_config_returned_value)
    if os.getenv('LOG') == 'DEBUG':
        kube_cmd_config_debug = "cat ~/.kube/config"
        cmd_pipe = subprocess.Popen(kube_cmd_config_debug, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for kubectl_response_line in cmd_pipe.stdout.readlines():
            print('kubectl_response_line:', kubectl_response_line)

# Print kubernetes nodes
def get_kube_nodes():
    kube_cmd_nodes = "kubectl get nodes"
    cmd_pipe = subprocess.Popen(kube_cmd_nodes, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for kubectl_response_line in cmd_pipe.stdout.readlines():
        print('kubectl_response_line:', kubectl_response_line)

# Check kubernetes Kind type function
def is_kube_yaml_valid(file_yaml):
    kind_types = ['Deployment', 'ConfigMap', 'Service', 'Secret']
    for yaml_key, yaml_value in file_yaml.items():
        print('yaml_key:', yaml_key)
        if "kind" in str(yaml_key).lower():
            print('Found Kind Key with yaml_value:', yaml_value)
            for kind_type in kind_types:
                print('kind_type:', kind_type)
                if kind_type.lower() == yaml_value.lower():
                    return True
      #if "kind" in key.lower():
      #  print('Kind key:', value)
    #for kind_type in kind_types:
    #    print('kind_type:', kind_type)

    return False

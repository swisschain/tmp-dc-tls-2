import os
import yaml

# Get yaml objects from file
def yaml_load(changed_file_name):
    with open(changed_file_name, 'r') as changed_file:
      try:
        changed_file_yaml = yaml.load(changed_file, Loader=yaml.SafeLoader)
      except yaml.YAMLError as exc:
        print('yaml file parse exception:', exc)
    if os.getenv('LOG') == 'DEBUG':
        print('type(changed_file_yaml):', type(changed_file_yaml))
        print('changed_file_yaml:', changed_file_yaml)
    #if isinstance(changed_file_yaml, dict):
    return changed_file_yaml

# Check if yaml path key exist
def get_yaml_path_key(yaml_file, yaml_path):
    yaml_path_array = yaml_path.split(".")
    yaml_path_array_len = len(yaml_path_array)
    print('yaml_path_array_len:', yaml_path_array_len)
    current_yaml_file_value = []
    count = 0
    #for yaml_path_key in yaml_path.split("."):
    for yaml_path_key in yaml_path_array:
        print('count:', count)
        print('yaml_path_key:', yaml_path_key)
        if current_yaml_file_value:
            for yaml_file_key, yaml_file_value in current_yaml_file_value.items():
                print('yaml_file_key:', yaml_file_key)
                if yaml_path_key in str(yaml_file_key).lower():
                    print('Found key:', yaml_path_key)
                    current_yaml_file_value = yaml_file_value
                    print('current_yaml_file_value:', current_yaml_file_value)
                    count += 1
        else:
            for yaml_file_key, yaml_file_value in yaml_file.items():
                print('yaml_file_key:', yaml_file_key)
                if yaml_path_key in str(yaml_file_key).lower():
                    print('Found first key:', yaml_path_key)
                    current_yaml_file_value = yaml_file_value
                    print('current_yaml_file_value:', current_yaml_file_value)
                    count += 1
    if yaml_path_array_len == count:
        #print('final count:', count)
        #print('current_yaml_file_value:', current_yaml_file_value)
        return current_yaml_file_value

import os
import yaml

# Get yaml objects from file
def yaml_load(changed_file_name):
    with open(changed_file_name, 'r') as changed_file:
      try:
          changed_file_yaml = yaml.load(changed_file, Loader=yaml.SafeLoader)
          if isinstance(changed_file_yaml, dict):
              return changed_file_yaml
      except yaml.YAMLError as exc:
          print('yaml file parse exception...')

# Check if yaml path key exist
def get_yaml_path_key(yaml_file, yaml_path):
    yaml_path_array = yaml_path.split(".")
    yaml_path_array_len = len(yaml_path_array)
    if os.getenv('LOG') == 'DEBUG':
        print('yaml_path_array_len:', yaml_path_array_len)
    current_yaml_file_value = []
    count = 0
    for yaml_path_key in yaml_path_array:
        if os.getenv('LOG') == 'DEBUG':
            print('count:', count)
            print('yaml_path_key:', yaml_path_key)
        if current_yaml_file_value:
            for yaml_file_key, yaml_file_value in current_yaml_file_value.items():
                if os.getenv('LOG') == 'DEBUG':
                    print('yaml_file_key:', yaml_file_key)
                if yaml_path_key in str(yaml_file_key).lower():
                    if os.getenv('LOG') == 'DEBUG':
                        print('Found key:', yaml_path_key)
                    current_yaml_file_value = yaml_file_value
                    if os.getenv('LOG') == 'DEBUG':
                        print('current_yaml_file_value:', current_yaml_file_value)
                    count += 1
                    break
        else:
            for yaml_file_key, yaml_file_value in yaml_file.items():
                if os.getenv('LOG') == 'DEBUG':
                    print('yaml_file_key:', yaml_file_key)
                if yaml_path_key in str(yaml_file_key).lower():
                    if os.getenv('LOG') == 'DEBUG':
                        print('Found first key:', yaml_path_key)
                    current_yaml_file_value = yaml_file_value
                    if os.getenv('LOG') == 'DEBUG':
                        print('current_yaml_file_value:', current_yaml_file_value)
                    count += 1
                    break
    if yaml_path_array_len == count:
        if os.getenv('LOG') == 'DEBUG':
            print('final count:', count)
            print('current_yaml_file_value:', current_yaml_file_value)
        return current_yaml_file_value

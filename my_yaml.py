import os
import yaml

LOG = os.getenv('LOG')

# Get yaml objects from file
def yaml_load(changed_file_name):
    with open(changed_file_name, 'r') as changed_file:
      try:
        changed_file_yaml = yaml.load(changed_file, Loader=yaml.SafeLoader)
      except yaml.YAMLError as exc:
        print('yaml file parse exception:', exc)
    if LOG == 'DEBUG':
        print('type(changed_file_yaml):', type(changed_file_yaml))
        print('changed_file_yaml:', changed_file_yaml)
    if isinstance(changed_file_yaml, dict):
        return changed_file_yaml

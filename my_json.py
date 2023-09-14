import os
import json
from my_common import to_str
from my_common import initialize_array
from my_common import is_extension_allowed

# Get json objects from file
def json_load(changed_file_name):
    with open(changed_file_name, 'r') as changed_file:
      try:
          changed_file_json = json.load(changed_file)
          if os.getenv('LOG') == 'DEBUG':
              print('changed_file_json:', changed_file_json)
              print('type(changed_file_json)', type(changed_file_json))
          if isinstance(changed_file_json, dict):
              return changed_file_json
      except json.JSONDecodeError as exc:
          print('json file parse exception ', exc)

def get_valid_json_files(deployment_order_names, files_list_git_changed, type):
    # type can be NOTVALID
    # NOTVALID - validate and add to not valid array
    result_array = initialize_array(len(deployment_order_names))
    for changed_file_name in files_list_git_changed:
        if os.getenv('LOG') == 'DEBUG':
            print('get_valid_json_files processing: ' + to_str(changed_file_name) + ' type: ' + type)
        if os.path.exists(changed_file_name):
            if is_extension_allowed(changed_file_name, ['.json']):
                changed_file_json = json_load(changed_file_name)
                if changed_file_json == None:
                    if type == 'NOTVALID':
                        print('get_valid_json_files not valid json file - NOTVALID (' + to_str(changed_file_name) + ')')
                        result_array[0].append(changed_file_name)
                else:
                    if os.getenv('LOG') == 'DEBUG':
                        print('get_valid_json_files json not valid - skip')
            else:
                if os.getenv('LOG') == 'DEBUG':
                    print('get_valid_json_files extensions not allowed - skip')
        else:
            if os.getenv('LOG') == 'DEBUG':
                print('get_valid_json_files not exist')
    return result_array
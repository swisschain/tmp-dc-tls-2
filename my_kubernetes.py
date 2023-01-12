# Check kubernetes Kind type function
def is_kube_yaml_valid(file_yaml, kind_types):
    for yaml_key, yaml_value in file_yaml.items():
        print('yaml_key:', yaml_key)
        if yaml_key.lower() in kind_types
            return True
      #if "kind" in key.lower():
      #  print('Kind key:', value)
    #for kind_type in kind_types:
    #    print('kind_type:', kind_type)

    return False

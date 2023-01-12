# Check kubernetes Kind type function
def is_kube_yaml_valid(file_yaml, kind_types):
    for yaml_key, yaml_value in file_yaml.items():
        print('yaml_key:', yaml_key)
        if "kind" in yaml_key.lower():
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

# Check kubernetes Kind type function
def is_kube_yaml_valid( file_yaml, kind_types ):
    for key, value in file_yaml.items():
      if "kind" in key.lower():
        print('Kind key:', value)
    for kind_type in kind_types:
        print('kind_type:', kind_type)
    return True 
    #return False 

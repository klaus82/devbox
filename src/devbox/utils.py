def read_json_file(file_path):
    import json
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

def find_devcontainer_config_folder():
    import os
    current_dir = os.getcwd()
    while True:
        devcontainer_dir = os.path.join(current_dir, '.devcontainer')
        if os.path.isdir(devcontainer_dir):
            return devcontainer_dir
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:
            break
        current_dir = parent_dir
    return None

def find_devcontainer_config(devcontainer_dir=None):
    import os
    if devcontainer_dir is None:
        devcontainer_dir = find_devcontainer_config_folder()
        if devcontainer_dir is None:
            return None
    config_path = os.path.join(devcontainer_dir, 'devcontainer.json')
    if os.path.isfile(config_path):
        return config_path
    return None
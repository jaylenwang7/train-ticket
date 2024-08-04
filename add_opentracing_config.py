import os
import yaml

# Configuration to be added
config_to_add = {
    'opentracing': {
        'jaeger': {
            'udp-sender': {
                'host': 'jaeger',
                'port': 6831
            }
        }
    }
}

def find_application_yaml_files(root_dir):
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file in ['application.yml', 'application.yaml'] and 'resources' in root.split(os.path.sep):
                yield os.path.join(root, file)

def update_yaml_file(file_path):
    try:
        with open(file_path, 'r') as file:
            try:
                existing_config = yaml.safe_load(file) or {}
            except yaml.YAMLError:
                print(f"Error parsing YAML in {file_path}. Skipping.")
                return False
    except IOError:
        print(f"Error reading file {file_path}. Skipping.")
        return False

    if 'opentracing' in existing_config:
        print(f"OpenTracing configuration already exists in {file_path}. Skipping.")
        return False

    existing_config.update(config_to_add)

    try:
        with open(file_path, 'w') as file:
            yaml.dump(existing_config, file, default_flow_style=False)
        print(f"Added OpenTracing configuration to {file_path}")
        return True
    except IOError:
        print(f"Error writing to file {file_path}")
        return False

def main():
    root_directory = '.'  # Current directory
    files_updated = 0

    for file_path in find_application_yaml_files(root_directory):
        if update_yaml_file(file_path):
            files_updated += 1

    print(f"Script completed. Updated {files_updated} file(s).")

if __name__ == "__main__":
    main()
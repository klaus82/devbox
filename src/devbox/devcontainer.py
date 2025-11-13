import docker




def read_json_file(file_path):
    import json
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data


def start_dev_container():
    devcjson = read_json_file('./src/testdata/devctest.json')
    image_name = devcjson.get("image", "mcr.microsoft.com/devcontainers/base:ubuntu")
    client = docker.from_env()
    try:
        container = client.containers.run(image_name, detach=True, tty=True)
        print(f"Started container with ID: {container.id}")
        return container
    except docker.errors.ImageNotFound:
        print(f"Image {image_name} not found. Please pull the image first.")


def stop_dev_container(container_id):
    try:
        client = docker.from_env()
        container = client.containers.get(container_id)
        container.stop()
        print(f"Stopped container with ID: {container.id}")
    except Exception as e:
        print(f"An error occurred while stopping the container: {e}")


def container_cli(container_id):
    import subprocess
    try:
        subprocess.run(['docker', 'exec', '-it', container_id, '/bin/bash'])
    except Exception as e:
        print(f"An error occurred while accessing the container CLI: {e}")


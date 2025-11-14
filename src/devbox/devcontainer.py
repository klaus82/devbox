import docker

from devbox.utils import read_json_file, find_devcontainer_config

def find_running_container_by_image(image_name):
    client = docker.from_env()
    for container in client.containers.list():
        try:
            c_image = container.attrs.get('Config', {}).get('Image', '') or ''
        except Exception:
            c_image = ''
        tags = container.image.tags or []
        if c_image == image_name or image_name in tags:
            return container
    return None

def find_image_from_devcontainer_file():
    devcjson_file =find_devcontainer_config()
    if devcjson_file is None:
        print("devcontainer.json not found.")
        return None
    devcjson = read_json_file(devcjson_file)
    return devcjson.get("image", None)

def start_dev_container():
    image_name = find_image_from_devcontainer_file()
    if image_name is None:
        print("No image specified in devcontainer.json.")
        return None
    client = docker.from_env()
    try:
        # Look for an existing container that was created from the same image
        existing = find_running_container_by_image(image_name)

        if existing:
            if existing.status == 'running':
                print(f"Found running container with same image: {existing.id}")
                return existing
            else:
                try:
                    existing.start()
                    print(f"Started existing container with ID: {existing.id}")
                    return existing
                except Exception as e:
                    print(f"Failed to start existing container {existing.id}: {e}")
                    # fall through to attempt creating a new one

        # No existing container found (or starting it failed) -> run a new container
        container = client.containers.run(image_name, detach=True, tty=True)
        print(f"Started new container with ID: {container.id}")
        return container
    except docker.errors.ImageNotFound:
        print(f"Image {image_name} not found. Please pull the image first.")
    except Exception as e:
        print(f"An error occurred while starting the container: {e}")


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


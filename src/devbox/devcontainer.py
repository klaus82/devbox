import docker

from devbox.utils import read_json_file

def start_dev_container():
    devcjson = read_json_file('./src/testdata/devctest.json')
    image_name = devcjson.get("image", "mcr.microsoft.com/devcontainers/base:ubuntu")
    client = docker.from_env()
    try:
        # Look for an existing container that was created from the same image
        existing = None
        for c in client.containers.list(all=True):
            try:
                c_image = c.attrs.get('Config', {}).get('Image', '') or ''
            except Exception:
                c_image = ''
            tags = c.image.tags or []
            if c_image == image_name or image_name in tags:
                existing = c
                break

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


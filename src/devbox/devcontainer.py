import os
import json
from typing import List, Optional, Dict, Any
try:
    import docker
    from docker.types import Mount
except ImportError:
    docker = None
    Mount = object  # Fallback to allow type hints without docker installed

from devbox.utils import read_json_file, find_devcontainer_config


def generate_random_name(image: bool = False) -> str:
    """
    Generate a name for a container or image.
    - For images: deterministic based on current working directory path (stable across runs).
    - For containers: random suffix to avoid collisions.
    """
    import os
    import random
    import string
    import hashlib

    if image:
        cwd = os.getcwd()
        base = os.path.basename(cwd) or "devbox"
        # Sanitize folder name
        sanitized = "".join(c if c.isalnum() or c in "-_." else "-" for c in base.lower())
        # Short hash to differentiate identical folder names at different paths
        h = hashlib.sha256(cwd.encode("utf-8")).hexdigest()[:8]
        return f"devbox_image_{sanitized}_{h}"
    # Container names remain random to allow multiple instances
    return "devbox_" + "".join(random.choices(string.ascii_lowercase + string.digits, k=10))


def get_container_name(devcjson: Dict[str, Any]) -> str:
    """
    Return the container name from devcontainer.json or generate one.
    """
    return devcjson.get("name", generate_random_name())


def find_running_container_by_image(image_name: str):
    """
    If a container with a matching image reference (full image ref or tag) is running (or exists), return it.
    """
    if docker is None:
        print("docker SDK not available.")
        return None

    client = docker.from_env()
    for container in client.containers.list(all=True):
        try:
            config_image = container.attrs.get("Config", {}).get("Image", "") or ""
        except Exception:
            config_image = ""
        tags = container.image.tags or []
        if config_image == image_name or image_name in tags:
            return container
    return None


def get_devcontainer_json() -> Optional[Dict[str, Any]]:
    """
    Load devcontainer.json from discovered .devcontainer/ folder.
    """
    devcjson_file = find_devcontainer_config()
    if devcjson_file is None:
        print("devcontainer.json not found.")
        return None
    return read_json_file(devcjson_file)


def _parse_mount_string(mount_str: str):
    """
    Parse a devcontainer-style mount string:
      source=/host/path,target=/container/path,type=bind,consistency=cached,readonly=true,mode=ro

    Returns a docker.types.Mount or None.
    """
    if not mount_str or not isinstance(mount_str, str):
        return None

    segments = [seg.strip() for seg in mount_str.split(",") if seg.strip()]
    kv: Dict[str, str] = {}
    for seg in segments:
        if "=" in seg:
            k, v = seg.split("=", 1)
            kv[k.strip()] = v.strip()

    target = kv.get("target")
    source = kv.get("source")  # may be missing for anonymous volume
    mtype = kv.get("type", "bind")
    consistency = kv.get("consistency")
    readonly_flag = kv.get("readonly", "").lower() == "true"
    mode = kv.get("mode", "")
    read_only = readonly_flag or (mode.lower() == "ro")

    # devcontainer spec allows anonymous volume (no source=) if type=volume + target specified
    if mtype == "volume" and not source:
        # For anonymous volumes docker-py expects source to be volume name; leave blank -> may fail
        # We create a random volume name to simulate anonymous volume.
        source = generate_random_name(image=False) + "_vol"

    if not target:
        print(f"Mount string missing target: {mount_str}")
        return None

    if docker is None or Mount is object:
        print("docker SDK not available; cannot create Mount objects.")
        return None

    kwargs = {
        "target": target,
        "source": source,
        "type": mtype,
        "read_only": read_only
    }
    if consistency:
        kwargs["consistency"] = consistency

    try:
        return Mount(**kwargs)
    except Exception as e:
        print(f"Failed to construct Mount from '{mount_str}': {e}")
        return None


def _parse_mount_dict(entry: Dict[str, Any]):
    """
    Parse a dict entry from devcontainer.json mounts list:
      {"source": "...", "target": "...", "type": "bind", "read_only": true, "consistency": "cached"}
    """
    if not isinstance(entry, dict):
        return None

    source = entry.get("source")
    target = entry.get("target")
    if not target:
        print(f"Mount dict missing target: {entry}")
        return None

    mtype = entry.get("type", "bind")
    read_only = bool(entry.get("read_only") or entry.get("readonly") or False)
    consistency = entry.get("consistency")

    if mtype == "volume" and not source:
        source = generate_random_name(image=False) + "_vol"

    if docker is None or Mount is object:
        print("docker SDK not available; cannot create Mount objects.")
        return None

    kwargs = {
        "target": target,
        "source": source,
        "type": mtype,
        "read_only": read_only
    }
    if consistency:
        kwargs["consistency"] = consistency

    try:
        return Mount(**kwargs)
    except Exception as e:
        print(f"Failed to construct Mount from dict {entry}: {e}")
        return None


def get_mounts(devcjson: Dict[str, Any]) -> List[Any]:
    """
    Convert devcontainer.json 'mounts' + 'workspaceMount' entries into a list of docker.types.Mount objects.

    Supported formats in devcontainer.json:
      "mounts": [
        "source=/Users/name/.aws,target=/root/.aws,type=bind,consistency=cached",
        {"source": "/opt/data", "target": "/data", "type": "bind", "read_only": false},
        "source=devbox_workspace,target=/workspace,type=volume"
      ],
      "workspaceMount": "source=/absolute/workspace,target=/workspaces/project,type=bind"

    Returns:
        List of Mount objects (empty list if none or docker SDK unavailable).
    """
    mounts_raw = devcjson.get("mounts", [])
    result: List[Any] = []

    if not isinstance(mounts_raw, list):
        print("devcontainer.json 'mounts' field is not a list; ignoring.")
    else:
        for entry in mounts_raw:
            m = None
            if isinstance(entry, str):
                m = _parse_mount_string(entry)
            elif isinstance(entry, dict):
                m = _parse_mount_dict(entry)
            else:
                print(f"Unsupported mount entry type: {type(entry)}")
            if m is not None:
                result.append(m)

    workspace_mount = devcjson.get("workspaceMount")
    if isinstance(workspace_mount, str):
        wm = _parse_mount_string(workspace_mount)
        if wm:
            result.append(wm)
    elif workspace_mount and isinstance(workspace_mount, dict):
        wm = _parse_mount_dict(workspace_mount)
        if wm:
            result.append(wm)

    return result


def build_dev_container(dockerfile: Optional[str], image_name: str, mounts: List[Any]) -> None:
    """
    Build the dev container image and start a container with mounts.
    """
    if docker is None:
        print("docker SDK not available; cannot build container.")
        return

    client = docker.from_env()
    try:
        path = os.path.join(os.getcwd(), ".devcontainer/")
        dockerfile_path = dockerfile if dockerfile else "Dockerfile"
        print(f"Building image '{image_name}' from '{dockerfile_path}' in {path}")
        client.images.build(path=path, tag=image_name, dockerfile=dockerfile_path)
        print(f"Built image with name: {image_name}")
        container_name = generate_random_name()
        start_dev_container(image_name, container_name, mounts)
    except Exception as e:
        print(f"Failed to build image {image_name}: {e}")


def start_dev_container(image_name: str, container_name: str, mounts: Optional[List[Any]] = None):
    """
    Start (or reuse) a container from image_name applying given mounts when creating new container.
    """
    if docker is None:
        print("docker SDK not available; cannot start container.")
        return None

    client = docker.from_env()
    try:
        existing = find_running_container_by_image(image_name)
        if existing:
            if existing.status == "running":
                print(f"Found running container with same image: {existing.id} called {existing.name}")
                return existing
            else:
                try:
                    existing.start()
                    print(f"Started existing container called {existing.name}")
                    return existing
                except Exception as e:
                    print(f"Failed to start existing container {existing.id}: {e}")

        run_kwargs = {
            "image": image_name,
            "name": container_name,
            "detach": True,
            "tty": True
        }
        if mounts:
            run_kwargs["mounts"] = mounts

        container = client.containers.run(**run_kwargs)
        print(f"Started new container with ID: {container.id} called {container.name}")
        return container
    except docker.errors.ImageNotFound:
        print(f"Image {image_name} not found. Please build or pull the image first.")
    except Exception as e:
        print(f"An error occurred while starting the container: {e}")
    return None


def stop_dev_container(container_id: str) -> None:
    """
    Stop a container by ID.
    """
    if docker is None:
        print("docker SDK not available; cannot stop container.")
        return

    try:
        client = docker.from_env()
        container = client.containers.get(container_id)
        container.stop()
        print(f"Stopped container with ID: {container.id}")
    except Exception as e:
        print(f"An error occurred while stopping the container: {e}")


def container_cli(container_id: str) -> None:
    """
    Launch interactive shell in container.
    """
    import subprocess

    try:
        subprocess.run(["docker", "exec", "-it", container_id, "/bin/bash"])
    except Exception as e:
        print(f"An error occurred while accessing the container CLI: {e}")


def start() -> None:
    """
    Primary entry point: load devcontainer.json, build or start a container, applying mounts.
    """
    devcjson = get_devcontainer_json()
    if devcjson is None:
        return

    print("Loaded devcontainer.json:")
    print(json.dumps(devcjson, indent=2))

    mounts = get_mounts(devcjson)
    if mounts:
        print(f"Configured {len(mounts)} mount(s):")
        for m in mounts:
            # Mount object attributes differ depending on docker SDK version
            source = getattr(m, "source", None)
            target = getattr(m, "target", None)
            mtype = getattr(m, "type", None)
            read_only = getattr(m, "read_only", False)
            print(f"  - {source} -> {target} (type={mtype}, read_only={read_only})")
    else:
        print("No mounts configured.")

    build_config = devcjson.get("build")
    image_ref = devcjson.get("image")

    if build_config:
        dockerfile = build_config.get("dockerfile", "Dockerfile")
        image_name = image_ref or generate_random_name(image=True)
        print("Building dev container image...")
        build_dev_container(dockerfile, image_name, mounts)
    elif image_ref:
        print("Starting container from existing image...")
        start_dev_container(image_ref, generate_random_name(), mounts)
    else:
        print("Neither 'build' nor 'image' specified in devcontainer.json; nothing to start.")

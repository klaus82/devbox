import pytest
from unittest.mock import patch, MagicMock, mock_open

# from devbox.devcontainer import read_json_file
import docker


# class TestReadJsonFile:
#     """Test the read_json_file function"""

#     @patch("builtins.open", new_callable=mock_open, read_data='{"image": "test-image:latest"}')
#     def test_read_json_file_success(self, mock_file):
#         """Test successful JSON file reading"""
#         result = read_json_file('test.json')

#         assert result["image"] == "test-image:latest"
#         mock_file.assert_called_once_with('test.json', 'r')

#     @patch("builtins.open", new_callable=mock_open, read_data='{"key1": "value1", "key2": "value2"}')
#     def test_read_json_file_multiple_keys(self, mock_file):
#         """Test reading JSON file with multiple keys"""
#         result = read_json_file('config.json')

#         assert result["key1"] == "value1"
#         assert result["key2"] == "value2"


# class TestStartDevContainer:
#     """Test the start_dev_container function"""

#     @patch('devcontainer.read_json_file')
#     @patch('devcontainer.docker.from_env')
#     def test_start_dev_container_success(self, mock_from_env, mock_read_json):
#         """Test successful container start"""
#         mock_read_json.return_value = {"image": "test-image:latest"}
#         mock_client = MagicMock()
#         mock_container = MagicMock()
#         mock_container.id = "container123"
#         mock_client.containers.run.return_value = mock_container
#         mock_from_env.return_value = mock_client

#         result = start_dev_container()

#         assert result.id == "container123"
#         mock_client.containers.run.assert_called_once_with("test-image:latest", detach=True, tty=True)

#     @patch('devcontainer.read_json_file')
#     @patch('devcontainer.docker.from_env')
#     def test_start_dev_container_default_image(self, mock_from_env, mock_read_json):
#         """Test default image is used when not specified"""
#         mock_read_json.return_value = {}
#         mock_client = MagicMock()
#         mock_container = MagicMock()
#         mock_container.id = "container456"
#         mock_client.containers.run.return_value = mock_container
#         mock_from_env.return_value = mock_client

#         result = start_dev_container()

#         mock_client.containers.run.assert_called_once_with(
#             "mcr.microsoft.com/devcontainers/base:ubuntu",
#             detach=True,
#             tty=True
#         )
#         assert result.id == "container456"

#     @patch('devcontainer.read_json_file')
#     @patch('devcontainer.docker.from_env')
#     def test_start_dev_container_image_not_found(self, mock_from_env, mock_read_json):
#         """Test ImageNotFound exception handling"""
#         mock_read_json.return_value = {"image": "nonexistent-image"}
#         mock_client = MagicMock()
#         mock_client.containers.run.side_effect = docker.errors.ImageNotFound("Image not found")
#         mock_from_env.return_value = mock_client

#         result = start_dev_container()

#         assert result is None


# class TestStopDevContainer:
#     """Test the stop_dev_container function"""

#     @patch('devcontainer.docker.from_env')
#     def test_stop_dev_container_success(self, mock_from_env):
#         """Test successful container stop"""
#         mock_client = MagicMock()
#         mock_container = MagicMock()
#         mock_container.id = "container123"
#         mock_client.containers.get.return_value = mock_container
#         mock_from_env.return_value = mock_client

#         stop_dev_container("container123")

#         mock_client.containers.get.assert_called_once_with("container123")
#         mock_container.stop.assert_called_once()

#     @patch('devcontainer.docker.from_env')
#     def test_stop_dev_container_not_found(self, mock_from_env):
#         """Test stopping non-existent container"""
#         mock_client = MagicMock()
#         mock_client.containers.get.side_effect = Exception("Container not found")
#         mock_from_env.return_value = mock_client

#         stop_dev_container("nonexistent_id")


# class TestContainerCli:
#     """Test the container_cli function"""

#     @patch('devcontainer.subprocess.run')
#     def test_container_cli_success(self, mock_subprocess):
#         """Test successful container CLI access"""
#         container_cli("container123")
#         mock_subprocess.assert_called_once_with(['docker', 'exec', '-it', 'container123', '/bin/bash'])

#     @patch('devcontainer.subprocess.run')
#     def test_container_cli_error(self, mock_subprocess):
#         """Test container CLI error handling"""
#         mock_subprocess.side_effect = Exception("Docker exec failed")
#         container_cli("container123")

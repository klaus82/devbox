import pytest
from unittest.mock import patch, MagicMock, mock_open
from devbox.utils import read_json_file, find_devcontainer_config


class TestReadJsonFile:
    """Test the read_json_file function"""

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data='{"image": "test-image:latest"}',
    )
    def test_read_json_file_success(self, mock_file):
        """Test successful JSON file reading"""
        result = read_json_file("test.json")

        assert result["image"] == "test-image:latest"
        mock_file.assert_called_once_with("test.json", "r")

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data='{"key1": "value1", "key2": "value2"}',
    )
    def test_read_json_file_multiple_keys(self, mock_file):
        """Test reading JSON file with multiple keys"""
        result = read_json_file("config.json")

        assert result["key1"] == "value1"
        assert result["key2"] == "value2"


class TestFindDevcontainerConfig:
    """Test the find_devcontainer_config function"""

    @patch("os.path.isdir")
    @patch("os.path.isfile")
    @patch("os.path.join", side_effect=lambda *args: "/".join(args))
    @patch("os.getcwd", return_value="/home/user/project")
    def test_find_devcontainer_config_found(
        self, mock_getcwd, mock_join, mock_isfile, mock_isdir
    ):
        """Test finding devcontainer.json when it exists"""
        mock_isdir.side_effect = lambda path: path == "/home/user/project/.devcontainer"
        mock_isfile.side_effect = (
            lambda path: path == "/home/user/project/.devcontainer/devcontainer.json"
        )

        result = find_devcontainer_config()

        assert result == "/home/user/project/.devcontainer/devcontainer.json"

    @patch("os.path.isdir")
    @patch("os.path.isfile")
    @patch("os.path.join", side_effect=lambda *args: "/".join(args))
    @patch("os.getcwd", return_value="/home/user/project")
    def test_find_devcontainer_config_not_found(
        self, mock_getcwd, mock_join, mock_isfile, mock_isdir
    ):
        """Test not finding devcontainer.json"""
        mock_isdir.return_value = False
        mock_isfile.return_value = False

        result = find_devcontainer_config()

        assert result is None


# class TestFindDevcontainerConfigFolder:
#     """Test the find_devcontainer_config_folder function"""

#     @patch("os.path.isdir")
#     @patch("os.path.dirname", side_effect=lambda path: "/".join(path.split("/")[:-1]))
#     @patch("os.getcwd", return_value="/home/user/project/subdir")
#     def test_find_devcontainer_config_folder_found(self, mock_getcwd, mock_dirname, mock_isdir):
#         """Test finding .devcontainer folder"""
#         def isdir_side_effect(path):
#             return path in ["/home/user/project/.devcontainer"]

#         mock_isdir.side_effect = isdir_side_effect

#         result = find_devcontainer_config_folder()

#         assert result == "/home/user/project/.devcontainer"

#     @patch("os.path.isdir")
#     @patch("os.path.dirname", side_effect=lambda path: "/".join(path.split("/")[:-1]))
#     @patch("os.getcwd", return_value="/home/user/project/subdir")
#     def test_find_devcontainer_config_folder_not_found(self, mock_getcwd, mock_dirname, mock_isdir):
#         """Test not finding .devcontainer folder"""
#         mock_isdir.return_value = False

#         result = find_devcontainer_config_folder()

#         assert result is None

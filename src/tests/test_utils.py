import pytest
from unittest.mock import patch, MagicMock, mock_open
from devbox.utils import read_json_file


class TestReadJsonFile:
    """Test the read_json_file function"""
    
    @patch("builtins.open", new_callable=mock_open, read_data='{"image": "test-image:latest"}')
    def test_read_json_file_success(self, mock_file):
        """Test successful JSON file reading"""
        result = read_json_file('test.json')
        
        assert result["image"] == "test-image:latest"
        mock_file.assert_called_once_with('test.json', 'r')
    
    @patch("builtins.open", new_callable=mock_open, read_data='{"key1": "value1", "key2": "value2"}')
    def test_read_json_file_multiple_keys(self, mock_file):
        """Test reading JSON file with multiple keys"""
        result = read_json_file('config.json')
        
        assert result["key1"] == "value1"
        assert result["key2"] == "value2"
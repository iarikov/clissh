import unittest
from unittest.mock import patch, mock_open, MagicMock
import json
import sys
import os

from ssh_manager import manager

class TestSSHManager(unittest.TestCase):

    def setUp(self):
        # We don't want to actually write to ~/.ssh_manager.json during tests
        self.mock_config = {
            "test_server": {
                "user": "testuser",
                "host": "192.168.1.100",
                "port": 22
            }
        }

    @patch('ssh_manager.manager.os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='{"test_server": {"user": "testuser", "host": "192.168.1.100", "port": 22}}')
    def test_load_config_existing(self, mock_file, mock_exists):
        mock_exists.return_value = True
        config = manager._load_config()
        self.assertEqual(config, self.mock_config)
        mock_exists.assert_called_once_with(manager.CONFIG_FILE)

    @patch('ssh_manager.manager.os.path.exists')
    def test_load_config_not_existing(self, mock_exists):
        mock_exists.return_value = False
        config = manager._load_config()
        self.assertEqual(config, {})

    @patch('ssh_manager.manager._load_config')
    @patch('ssh_manager.manager._save_config')
    @patch('builtins.print')
    def test_add_server_success(self, mock_print, mock_save, mock_load):
        mock_load.return_value = {}
        manager.add_server("new_server", "user@host.com", 2222)
        mock_save.assert_called_once_with({"new_server": {"user": "user", "host": "host.com", "port": 2222}})
        mock_print.assert_called_once_with("Successfully added server 'new_server'.")

    @patch('ssh_manager.manager._load_config')
    @patch('builtins.print')
    def test_add_server_existing(self, mock_print, mock_load):
        mock_load.return_value = self.mock_config
        with self.assertRaises(SystemExit) as cm:
            manager.add_server("test_server", "user@host")
        self.assertEqual(cm.exception.code, 1)
        mock_print.assert_called_once_with("Error: Server with alias 'test_server' already exists.")

    @patch('ssh_manager.manager._load_config')
    @patch('builtins.print')
    def test_add_server_invalid_connection(self, mock_print, mock_load):
        mock_load.return_value = {}
        with self.assertRaises(SystemExit) as cm:
            manager.add_server("new_server", "invalid_connection_string")
        self.assertEqual(cm.exception.code, 1)
        mock_print.assert_called_once_with("Error: Connection string must be in format user@host")

    @patch('ssh_manager.manager._load_config')
    @patch('ssh_manager.manager._save_config')
    @patch('builtins.print')
    def test_remove_server_success(self, mock_print, mock_save, mock_load):
        mock_load.return_value = self.mock_config.copy()
        manager.remove_server("test_server")
        mock_save.assert_called_once_with({})
        mock_print.assert_called_once_with("Successfully removed server 'test_server'.")

    @patch('ssh_manager.manager._load_config')
    @patch('builtins.print')
    def test_remove_server_not_found(self, mock_print, mock_load):
        mock_load.return_value = {}
        with self.assertRaises(SystemExit) as cm:
            manager.remove_server("nonexistent")
        self.assertEqual(cm.exception.code, 1)
        mock_print.assert_called_once_with("Error: Server with alias 'nonexistent' not found.")

    @patch('ssh_manager.manager._load_config')
    @patch('ssh_manager.manager.subprocess.run')
    @patch('ssh_manager.manager.os.path.exists')
    @patch('builtins.print')
    def test_setup_keys_key_exists(self, mock_print, mock_exists, mock_run, mock_load):
        mock_load.return_value = self.mock_config
        # return True for key existence check
        mock_exists.return_value = True

        manager.setup_keys("test_server")

        mock_run.assert_called_once_with(['ssh-copy-id', '-p', '22', 'testuser@192.168.1.100'], check=True)
        # Should not generate key
        self.assertEqual(mock_run.call_count, 1)

    @patch('ssh_manager.manager._load_config')
    @patch('ssh_manager.manager.subprocess.run')
    @patch('ssh_manager.manager.os.path.exists')
    @patch('ssh_manager.manager.os.makedirs')
    @patch('builtins.print')
    def test_setup_keys_no_key(self, mock_print, mock_makedirs, mock_exists, mock_run, mock_load):
        mock_load.return_value = self.mock_config
        # First call: ssh key dir doesn't exist, Second call: key file doesn't exist
        mock_exists.side_effect = [False, False]

        manager.setup_keys("test_server")

        # Verify keygen was called
        self.assertEqual(mock_run.call_count, 2)
        keygen_call = mock_run.call_args_list[0]
        self.assertIn('ssh-keygen', keygen_call[0][0])

        # Verify copy-id was called
        copy_call = mock_run.call_args_list[1]
        self.assertEqual(copy_call[0][0], ['ssh-copy-id', '-p', '22', 'testuser@192.168.1.100'])

    @patch('ssh_manager.manager._load_config')
    @patch('ssh_manager.manager.os.execvp')
    @patch('builtins.print')
    def test_connect_server_success(self, mock_print, mock_execvp, mock_load):
        mock_load.return_value = self.mock_config
        manager.connect_server("test_server")
        mock_execvp.assert_called_once_with('ssh', ['ssh', '-p', '22', 'testuser@192.168.1.100'])

if __name__ == '__main__':
    unittest.main()

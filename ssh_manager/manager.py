import json
import os
import subprocess
import sys

CONFIG_FILE = os.path.expanduser('~/.ssh_manager.json')

def _load_config():
    if not os.path.exists(CONFIG_FILE):
        return {}
    with open(CONFIG_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def _save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def add_server(alias, connection_string, port=22):
    config = _load_config()
    if alias in config:
        print(f"Error: Server with alias '{alias}' already exists.")
        sys.exit(1)

    parts = connection_string.split('@')
    if len(parts) != 2:
        print("Error: Connection string must be in format user@host")
        sys.exit(1)

    user, host = parts
    config[alias] = {
        'user': user,
        'host': host,
        'port': port
    }
    _save_config(config)
    print(f"Successfully added server '{alias}'.")

def list_servers():
    config = _load_config()
    if not config:
        print("No servers configured.")
        return

    print(f"{'Alias':<15} | {'User':<15} | {'Host':<20} | {'Port':<5}")
    print("-" * 65)
    for alias, details in config.items():
        print(f"{alias:<15} | {details['user']:<15} | {details['host']:<20} | {details['port']:<5}")

def remove_server(alias):
    config = _load_config()
    if alias not in config:
        print(f"Error: Server with alias '{alias}' not found.")
        sys.exit(1)

    del config[alias]
    _save_config(config)
    print(f"Successfully removed server '{alias}'.")

def setup_keys(alias):
    config = _load_config()
    if alias not in config:
        print(f"Error: Server with alias '{alias}' not found.")
        sys.exit(1)

    server = config[alias]
    ssh_dir = os.path.expanduser('~/.ssh')
    key_path = os.path.join(ssh_dir, 'id_rsa')

    # Generate key if it doesn't exist
    if not os.path.exists(key_path):
        print("SSH key not found. Generating a new one...")
        if not os.path.exists(ssh_dir):
            os.makedirs(ssh_dir, mode=0o700)
        try:
            subprocess.run(['ssh-keygen', '-t', 'rsa', '-b', '4096', '-f', key_path, '-N', ''], check=True)
            print("SSH key generated successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error generating SSH key: {e}")
            sys.exit(1)

    # Copy key to server
    print(f"Setting up passwordless auth for {alias}...")
    port_str = str(server.get('port', 22))
    conn_str = f"{server['user']}@{server['host']}"

    try:
        subprocess.run(['ssh-copy-id', '-p', port_str, conn_str], check=True)
        print(f"Successfully set up keys for '{alias}'.")
    except subprocess.CalledProcessError as e:
        print(f"Error copying SSH key: {e}")
        sys.exit(1)

def connect_server(alias):
    config = _load_config()
    if alias not in config:
        print(f"Error: Server with alias '{alias}' not found.")
        sys.exit(1)

    server = config[alias]
    port_str = str(server.get('port', 22))
    conn_str = f"{server['user']}@{server['host']}"

    print(f"Connecting to {alias} ({conn_str})...")
    # Use os.execvp to replace the current process with the ssh process
    # This allows a truly interactive session that works smoothly with signals
    try:
        os.execvp('ssh', ['ssh', '-p', port_str, conn_str])
    except OSError as e:
        print(f"Error executing ssh: {e}")
        sys.exit(1)

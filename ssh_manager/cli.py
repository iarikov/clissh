import argparse
import sys
from . import manager

def main():
    parser = argparse.ArgumentParser(description="SSH Manager - Manage and connect to SSH servers easily.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Add command
    parser_add = subparsers.add_parser("add", help="Add a new SSH server")
    parser_add.add_argument("alias", help="Alias for the server (e.g., 'prod', 'db')")
    parser_add.add_argument("connection", help="Connection string in format user@host")
    parser_add.add_argument("-p", "--port", type=int, default=22, help="SSH port (default: 22)")

    # List command
    parser_list = subparsers.add_parser("list", help="List all configured SSH servers")

    # Remove command
    parser_remove = subparsers.add_parser("remove", help="Remove an SSH server")
    parser_remove.add_argument("alias", help="Alias of the server to remove")

    # Setup keys command
    parser_setup = subparsers.add_parser("setup-keys", help="Set up passwordless SSH authentication")
    parser_setup.add_argument("alias", help="Alias of the server to setup keys for")

    # Connect command
    parser_connect = subparsers.add_parser("connect", help="Connect to an SSH server")
    parser_connect.add_argument("alias", help="Alias of the server to connect to")

    args = parser.parse_args()

    if args.command == "add":
        manager.add_server(args.alias, args.connection, args.port)
    elif args.command == "list":
        manager.list_servers()
    elif args.command == "remove":
        manager.remove_server(args.alias)
    elif args.command == "setup-keys":
        manager.setup_keys(args.alias)
    elif args.command == "connect":
        manager.connect_server(args.alias)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()

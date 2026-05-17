# SSH Manager

A simple CLI tool for Ubuntu to manage SSH servers, set up passwordless authentication, and connect to them easily.

## Features

- Save SSH server details with aliases.
- List saved servers.
- Automatically setup SSH keys (using `ssh-keygen` and `ssh-copy-id`) for passwordless login.
- Connect to saved servers by alias.
- Remove saved servers.

## Installation

```bash
pip install -e .
```

## Usage

```bash
sshman add <alias> <user>@<host> [-p port]
sshman list
sshman setup-keys <alias>
sshman connect <alias>
sshman remove <alias>
```

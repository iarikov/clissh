from setuptools import setup, find_packages

setup(
    name='ssh-manager',
    version='0.1.0',
    description='A CLI tool to manage SSH servers, automatically set up keys, and connect to them.',
    author='Jules',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'sshm=ssh_manager.cli:main',
        ],
    },
    install_requires=[],
)

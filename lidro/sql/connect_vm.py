""" Connect VM via SSH
"""
import paramiko


def connect_to_vm(hostname, username, password):
    """
    Connect virtual machine via SSH

    Args:
        hostname (str): virtual machine name
        username (str): virtual machine username
        password (str): password for SSH authentication

    Returns:
        paramiko.SSHClient: SSH connection object.
    """
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, username=username, password=password)
    return ssh

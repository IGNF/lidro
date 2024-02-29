# import pytest

from lidro.sql.connect_vm import connect_to_vm

hostname = "metadonnee_prod"  # virtual machine name
username = "mdupays"  # virtual machine username
password = ""  # Password for SSH authentication.


def test_connect_vm():
    connect_to_vm(hostname, username, password)
    # assert ssh is not None

    # ssh.close()

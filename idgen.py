import socket, getpass

def get_uid():
    hostname = socket.gethostname()
    username = getpass.getuser()
    return f"{hostname}-{username}"

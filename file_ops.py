import os

def list_files(folder):
    return os.listdir(folder)

def file_exists(folder, filename):
    return os.path.isfile(os.path.join(folder, filename))

def get_file_path(folder, filename):
    return os.path.join(folder, filename)

import shutil
import os
import subprocess


def check_dependency(command: str, supposed_dependency):
    if shutil.which(command) is None:
        print('Command `{}` not found. '
              'Probably, you need to install {}.'.format(command, supposed_dependency))
        exit(3)


def list_of_files():
    accepted_extensions = ["jpg", "jpeg", "png", "JPG", "JPEG", "PNG"]
    filenames = [fn for fn in os.listdir() if fn.split(".")[-1] in accepted_extensions]
    return filenames


def execute(command: str, *args):
    try:
        subprocess.check_call(command.format(*args), shell=True)
        return 0
    except subprocess.CalledProcessError as e:
        print(e)
        return e.returncode

import os
import subprocess


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

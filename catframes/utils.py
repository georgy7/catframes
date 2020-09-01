import argparse
import os
import platform
import re
import shutil
import subprocess

__all__ = [
    'check_dependency',
    'list_of_files',
    'execute',
    'execute_quiet',
    'python_supports_allow_abbrev',
    'color_argument',
    'fps_argument'
]


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


def execute_quiet(command: str, *args):
    try:
        subprocess.check_call(command.format(*args),
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                              shell=True)
        return 0
    except subprocess.CalledProcessError as e:
        print(command)
        print(e)
        return e.returncode


def python_supports_allow_abbrev():
    v = platform.python_version_tuple()
    v0, v1 = int(v[0]), int(v[1])
    return (v0 > 3) or (v0 == 3 and v1 >= 5)


def color_argument(color: str):
    ERROR = "Color must have format #123 or #123456."
    pattern = re.compile('^#[0-9a-fA-F]{3}$|^#[0-9a-fA-F]{6}$')
    if not pattern.match(color):
        raise argparse.ArgumentTypeError(ERROR)
    elif 4 == len(color):
        r = color[0] + color[1] * 2 + color[2] * 2 + color[3] * 2
    else:
        r = color
    return r


def fps_argument(arg):
    try:
        i = int(arg)
    except ValueError as e:
        raise argparse.ArgumentTypeError(str(e))

    if i < 1:
        raise argparse.ArgumentTypeError("Frames per second must be greater than or equal 1.")
    elif i > 120:
        raise argparse.ArgumentTypeError("Frames per second must be less than or equal 120.")

    return i

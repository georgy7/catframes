#!/usr/bin/env python3
import argparse
import os
import sys

from catframes.utils import *
from catframes.version import version

USAGE = """
--------------------------

catframes_to_video [--help]
catframes_to_video --default
catframes_to_video [--delete-images] [-o pathToFile.mp4] [-r N]

It does not remove any frames by default.

It is in the lexicographical order by default:
        aa
        ab
        abc
        ac
        bbb
        z11
        z12
        z2

A sample usage:

    cd today_directory
    catframes_fix_resolution
    catframes_to_video -o "/backups/today.mp4"

THE FILE `list.txt` WILL BE OVERWRITTEN!
"""

LIST_FILE_NAME = "list.txt"


def print_error(msg):
    print("\n===============")
    print(msg)
    print("===============")


def check_dependencies():
    check_dependency('ffmpeg', 'FFmpeg')


DEFAULT_FPS = 1
DEFAULT_OUTPUT = 'output.mp4'


class ToVideoConverter:
    def __init__(self):
        check_dependencies()
        self.output = DEFAULT_OUTPUT
        self.delete_images = False
        self.fps = DEFAULT_FPS
        self.ready = False

    @staticmethod
    def save_list(filenames, fps):
        duration = 1 / fps
        with open(LIST_FILE_NAME, 'w') as file:
            for name in filenames:
                file.write("file '%s'\n" % name)
                file.write("duration %.10f\n" % duration)

    def make_file_list_lexicographical_order(self):
        filenames = sorted(list_of_files())
        self.save_list(filenames, self.fps)

    def parse_arguments(self):

        parser = argparse.ArgumentParser(
            description='Part of catframes v{}.'.format(version()),
            epilog=USAGE,
            formatter_class=argparse.RawDescriptionHelpFormatter
        )

        parser.add_argument('-d', '-default', '--default', action='store_true',
                            help='Run with the default settings.')

        parser.add_argument('-o', '--output', default=DEFAULT_OUTPUT,
                            help='Output filename. Default: {}.'.format(DEFAULT_OUTPUT))

        parser.add_argument('--delete-images', action='store_true',
                            help='Delete images after making video.')

        parser.add_argument('-r', '--fps', type=fps_argument, default=DEFAULT_FPS,
                            help='Frames per second (1-120). Default: {}.'.format(DEFAULT_FPS))

        namespace = parser.parse_args(sys.argv[1:])

        if len(sys.argv) < 2:
            parser.print_help()
            sys.exit(0)

        if namespace.default:
            if len(sys.argv) > 2:
                print("\n`--default` is only allowed as a single parameter.\n")
                sys.exit(1)
            else:
                print("\nUsing the default settings...\n")
                self.ready = True
        else:
            self.output = namespace.output
            self.delete_images = namespace.delete_images
            self.fps = namespace.fps
            self.ready = True

    def process(self):
        if os.path.exists(LIST_FILE_NAME):
            os.remove(LIST_FILE_NAME)

        # Lexicographical (default) order is the best for surveillance data.
        # There is no choice yet.
        self.make_file_list_lexicographical_order()

        command = 'ffmpeg -f concat -safe 0 -i {} -pix_fmt yuv420p -c:v libx264 -preset slow -tune fastdecode -crf 35 -r {} {}'
        return_code = execute(command, LIST_FILE_NAME, self.fps, self.output)

        if return_code == 0:
            if self.delete_images:
                for image in list_of_files():
                    os.remove(image)
        else:
            print_error("FFmpeg error %s" % return_code)
            sys.exit(return_code)


def run():
    converter = ToVideoConverter()
    converter.parse_arguments()
    if converter.ready:
        converter.process()

#!/usr/bin/env python3

import sys
from catframes.utils import *

HELP_ARGUMENTS = ["help", "h", "-help", "--help", "-h", "usage", "u", "-usage", "--usage", "-u"]
DEFAULT_ARGUMENTS = ["default", "-default", "--default"]

USAGE = ("\n"
         "    catframes_to_video [--help]\n"
         "    catframes_to_video --default\n"
         "    catframes_to_video [--delete-images] [-o pathToFile.mp4] [-r|--fps N]\n"
         "\n"
         "      * Default output file is \"output.mp4\" in the current folder.\n"
         "      * It does not remove any frames by default.\n"
         "      * It is the lexicographical order by default:\n"
         "            aa\n"
         "            ab\n"
         "            abc\n"
         "            ac\n"
         "            bbb\n"
         "            z11\n"
         "            z12\n"
         "            z2\n"
         "\n"
         "    A sample usage:\n"
         "\n"
         "        cd today_directory\n"
         "        catframes_fix_resolution\n"
         "        catframes_to_video -o \"/backups/today.mp4\"\n"
         "\n"
         "    THE FILE `list.txt` WILL BE OVERWRITTEN!\n"
         "\n"
         )

LIST_FILE_NAME = "list.txt"


def print_error(msg):
    print("\n===============")
    print(msg)
    print("===============")


def usage_exit(code):
    print(USAGE)
    sys.exit(code)


def check_dependencies():
    check_dependency('ffmpeg', 'FFmpeg')


class ToVideoConverter:
    def __init__(self):
        check_dependencies()
        self.output = "output.mp4"
        self.delete_images = False
        self.fps = 1

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

    def parse_output_argument(self, value_position):
        if len(sys.argv) > value_position:
            self.output = sys.argv[value_position]
        else:
            print_error("There is must be a path after the \"-o\" parameter.")
            usage_exit(1)

    def parse_arguments(self):
        if len(sys.argv) < 2:
            print()
            usage_exit(0)

        if (len(sys.argv) == 2) and (sys.argv[1] in DEFAULT_ARGUMENTS):
            print("\nUsing the default settings...")
        else:
            i = 1
            while len(sys.argv) > i:
                if sys.argv[i] == "-o":
                    self.parse_output_argument(i + 1)
                    i = i + 2
                elif (sys.argv[i] == "-r") or (sys.argv[i] == "--fps"):
                    self.fps = int(sys.argv[i + 1])
                    i = i + 2
                elif sys.argv[i] == "--delete-images":
                    self.delete_images = True
                    i = i + 1
                elif sys.argv[i] in HELP_ARGUMENTS:
                    print()
                    usage_exit(0)
                else:
                    if sys.argv[i] in DEFAULT_ARGUMENTS:
                        print_error("'%s' is only allowed as a single parameter." % (sys.argv[i]))
                    else:
                        print_error("Unknown parameter '%s'." % (sys.argv[i]))
                    usage_exit(1)

        if self.output.startswith('-'):
            print_error(
                "The output file name '%s' starts with a hyphen. What are you trying to do exactly?" % self.output)
            usage_exit(2)

    def process(self):
        if os.path.exists(LIST_FILE_NAME):
            os.remove(LIST_FILE_NAME)

        # Lexicographical (default) order is the best for surveillance data.
        # There is no choice yet.
        self.make_file_list_lexicographical_order()

        command = 'ffmpeg -f concat -safe 0 -i {} -c:v libx264 -preset slow -tune fastdecode -crf 35 -r {} {}'
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
    converter.process()

import sys
import os.path

from catframes.fix_resolution import process
from catframes.to_video import ToVideoConverter
from catframes.version import version

usage = """
Catframes can resize all images in the current directory
to the same size and then concatenate them to a video file (mp4).

MAKE SURE YOU KNOW WHAT YOU ARE DOING!
THIS IS DANGEROUS FOR YOUR DATA.
THIS SCRIPT WILL MODIFY OR DELETE IMAGES IN THE CURRENT DIRECTORY.
PLEASE, MAKE A BACKUP IF THIS IS YOUR FIRST TRY.

NO WARRANTY! USE IT AT YOUR OWN RISK!

You have two options.
The first one:

    catframes --rewrite-images [-o pathToFile.mp4] [-r|--fps N]

And the second:

    catframes --rewrite-and-then-remove-images [-o pathToFile.mp4] [-r|--fps N]

"""

def set_output(converter, file_name):

    if (not file_name.endswith('.mp4')) or (len(file_name) <= 4):
        print('I do not recommend other formats than mp4 for slideshow-like things. So, I blocked this.')
        exit(1)

    if os.path.exists(file_name):
        print('File already exists: ' + file_name)
        exit(1)

    converter.output = file_name

def fps_parameter(s):
    return (s == '-r') or (s == '--fps')

def parse_output(converter):
    if len(sys.argv) >= 3:
        if (len(sys.argv) == 4) and (sys.argv[2] == '-o'):
            set_output(converter, sys.argv[3])

        elif (len(sys.argv) == 4) and fps_parameter(sys.argv[2]):
            converter.fps = int(sys.argv[3])

        elif (len(sys.argv) == 6) and fps_parameter(sys.argv[2]) and (sys.argv[4] == '-o'):
            converter.fps = int(sys.argv[3])
            set_output(converter, sys.argv[5])

        elif (len(sys.argv) == 6) and fps_parameter(sys.argv[4]) and (sys.argv[2] == '-o'):
            set_output(converter, sys.argv[3])
            converter.fps = int(sys.argv[5])

        else:
            print(usage)
            exit(1)


def just_rewrite_and_concatenate():
    converter = ToVideoConverter()
    parse_output(converter)
    process()
    converter.process()


def rewrite_concatenate_and_remove_images():
    converter = ToVideoConverter()
    parse_output(converter)
    process()
    converter.delete_images = True
    converter.process()


def run():
    if len(sys.argv) >= 2:
        if sys.argv[1] in ['--version', '-version', '-v']:
            print(version())
        elif sys.argv[1] == '--rewrite-images':
            just_rewrite_and_concatenate()
        elif sys.argv[1] in ['--rewrite-and-then-remove-images', '--rewrite-and-then-delete-images']:
            rewrite_concatenate_and_remove_images()
        else:
            print(usage)
    else:
        print(usage)


# For testing.
if __name__ == "__main__":
    run()

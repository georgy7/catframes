#!/usr/bin/env python3 

import sys
import os
import subprocess
import time
from multiprocessing import Pool
from catframes.most_common_image_resolution_in_the_folder import most_common_image_resolution_in_the_folder

expected_parameter = '--yes-rewrite-images'

warning = """



!!!!!!!!!!!!!!!!!!!!!!
The canvas size of all images in the current directory
may be changed, their content may be resized.
They may also be renamed and be converted to another format.
Be sure, that you have a copy of the folder before
running this command.

Expected behaviour:
The slightly larger images will be cropped (to the left-top
corner). The images, that are much larger, will be resized down.
And the smaller images will be expanded with a green color (from
the left-top).

The result image resolution are resolved automatically
as the most common resolution in the folder.

I MAKE NO REPRESENTATIONS OR
WARRANTIES OF ANY KIND CONCERNING THE SOFTWARE, EXPRESS, IMPLIED,
STATUTORY OR OTHERWISE, INCLUDING WITHOUT LIMITATION WARRANTIES OF
TITLE, MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, NON
INFRINGEMENT, OR THE ABSENCE OF LATENT OR OTHER DEFECTS, ACCURACY, OR
THE PRESENT OR ABSENCE OF ERRORS, WHETHER OR NOT DISCOVERABLE, ALL TO
THE GREATEST EXTENT PERMISSIBLE UNDER APPLICABLE LAW.

If you are agree, run this command
with the flag "{}".
!!!!!!!!!!!!!!!!!!!!!!


"""


def list_of_files():
    accepted_extensions = ["jpg", "jpeg", "png", "JPG", "JPEG", "PNG"]
    filenames = [fn for fn in os.listdir() if fn.split(".")[-1] in accepted_extensions]
    return filenames


def process():
    start_time = time.time()
    print('Resolving the most common resolution in the folder...')

    target_resolution_string = most_common_image_resolution_in_the_folder()
    target_size = target_resolution_string.split('x')

    print("Got it.", target_resolution_string)
    print('Stage 1 completed in {} seconds.\n'.format(time.time() - start_time))

    if len(target_size) < 2:
        print('Bad resolution.')
        sys.exit(1);

    start_stage_2_time = time.time()
    print('Mogrifying the images...')

    i = 0
    with Pool(processes=4) as pool:
        for r in pool.imap_unordered(FixImage(target_size), list_of_files()):
            print(r, end='')
            i = i + 1
            if i % 50 == 0:
                sys.stdout.flush()

    print('\nStage 2 completed in {} seconds.\n'.format(time.time() - start_stage_2_time))
    print('-------------\nCompleted in {} seconds.\n'.format(time.time() - start_time))


class FixImage(object):
    def __init__(self, target_size):
        self.target_size = target_size
        self.target_aspect_ratio = float(target_size[0]) / float(target_size[1])
        self.target_resolution_string = target_size[0] + 'x' + target_size[1]

    def __call__(self, f):
        image_resolution_string = os.popen("identify -format '%wx%h' \"{}\"".format(f)).read()
        if not image_resolution_string:
            return '\nCould not resolve size of \"{}\"\n'.format(f)

        image_resolution = image_resolution_string.split('x')
        if len(image_resolution) < 2:
            return '\nCould not resolve size of \"{}\"\n'.format(f)

        if (image_resolution[0] == self.target_size[0]) and (image_resolution[1] == self.target_size[1]):
            # Skipping.
            return ','

        elif (abs(int(image_resolution[0]) - int(self.target_size[0])) < 16) and \
                (abs(int(image_resolution[1]) - int(self.target_size[1])) < 16):
            comand = 'mogrify -background "#00ff0d" -extent {} -gravity NorthWest -quality 98 "{}"'
            subprocess.check_call(comand.format(self.target_resolution_string, f), shell=True)
            return '.'
        else:
            image_aspect_ratio = float(image_resolution[0]) / float(image_resolution[1])
            if abs(image_aspect_ratio - self.target_aspect_ratio) < 0.45:
                comand = 'mogrify -resize {}! -gravity NorthWest -quality 98 "{}"'
                subprocess.check_call(comand.format(self.target_resolution_string, f), shell=True)
                return 's'
            else:
                comand = 'mogrify -background "#0590b0" -resize {} -extent {} -gravity Center -quality 98 "{}"'
                subprocess.check_call(comand.format(self.target_resolution_string, self.target_resolution_string, f),
                                      shell=True)
                return 'c'


def run():
    if (len(sys.argv) == 2) and (sys.argv[1] == expected_parameter):
        process()
    else:
        print(warning.format(expected_parameter))

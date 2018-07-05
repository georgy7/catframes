#!/usr/bin/env python3 

import sys
import os
import subprocess
import time

expected_parameter = '--yes-rewrite-images'

warning = """



!!!!!!!!!!!!!!!!!!!!!!
The canvas size of all images in the current directory
may be changed (without resizing their actual content).
They may also be renamed and be converted to another format.
Be sure, that you have a copy of the folder before
running this command.

Expected behaviour:
The larger images will be cropped (to the left-top corner).
The smaller images will be expanded (from the left-top).

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
with the flag "--yes-rewrite-images".
!!!!!!!!!!!!!!!!!!!!!!


"""

from most_common_image_resolution_in_the_folder import most_common_image_resolution_in_the_folder

def list_of_files():
    accepted_extensions = ["jpg", "jpeg", "png"]
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
    for f in list_of_files():

        i = i + 1
        if i % 100 == 0:
            sys.stdout.flush()

        image_resolution_string = os.popen("identify -format '%wx%h' \"{}\"".format(f)).read()
        if not image_resolution_string:
            print('\nCould not resolve size of \"{}\"'.format(f))
            continue
        image_resolution = image_resolution_string.split('x')
        if len(image_resolution) < 2:
            print('\nCould not resolve size of \"{}\"'.format(f))
            continue

        if (float(image_resolution[0]) < (float(target_size[0]) * 1.2)) and \
                (float(image_resolution[1]) < (float(target_size[1]) * 1.2)):
            comand = 'mogrify -background "#00ff0d" -extent {} -gravity NorthWest -quality 98 "{}"'
            subprocess.check_call(comand.format(target_resolution_string, f), shell = True)
            print('.', end='')
        else:
            print('\n\"{}\" is a really big image ({}). Resizing.'.format(f, image_resolution_string))
            comand = 'mogrify -resize {}! -gravity NorthWest -quality 98 "{}"'
            subprocess.check_call(comand.format(target_resolution_string, f), shell = True)

    print('\nStage 2 completed in {} seconds.\n'.format(time.time() - start_stage_2_time))
    print('-------------\nCompleted in {} seconds.\n'.format(time.time() - start_time))


if __name__ == "__main__":
    if (len(sys.argv)==2) and (sys.argv[1]==expected_parameter):
        process()
    else:
        print(warning)

#!/usr/bin/env python3 

import sys
import os
import subprocess

expected_parameter = '--yes-rewrite-images'

warning = """



!!!!!!!!!!!!!!!!!!!!!!
The canvas size of all images in the current directory
may be changed (without resizing their actual content).
They may also be renamed and be converted to jpeg format.
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
    resolution = most_common_image_resolution_in_the_folder()
    print("Got it.", resolution)
    print('Stage 1 completed in {} seconds.\n'.format(time.time() - start_time))
    print('Mogrifying the images...')
    comand = 'mogrify -background "#00ff0d" -extent {} -gravity NorthWest -quality 98 "{}"'
    for f in list_of_files():
        subprocess.check_call(comand.format(resolution, f), shell = True)
    print('-------------\nCompleted in {} seconds.\n'.format(time.time() - start_time))


if __name__ == "__main__":
    if (len(sys.argv)==2) and (sys.argv[1]==expected_parameter):
        process()
    else:
        print(warning)

#!/usr/bin/env python3 

import sys
import os

expected_parameter = '--yes-rewrite-images'

warning = """



!!!!!!!!!!!!!!!!!!!!!!
The canvas size of all images in the current directory
may be changed (without resizing their actual content).
Be sure, that you have a copy of the folder before
running this command.

Expected behaviour:
The larger images will be cropped (to the left-top corner).
And the larger images will be expanded (from the left-top).

The result image resolution are resolved automatically
as the most common resolution in the folder.

I MAKES NO REPRESENTATIONS OR
WARRANTIES OF ANY KIND CONCERNING THE SOFTWARE, EXPRESS, IMPLIED,
STATUTORY OR OTHERWISE, INCLUDING WITHOUT LIMITATION WARRANTIES OF
TITLE, MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, NON
INFRINGEMENT, OR THE ABSENCE OF LATENT OR OTHER DEFECTS, ACCURACY, OR
THE PRESENT OR ABSENCE OF ERRORS, WHETHER OR NOT DISCOVERABLE, ALL TO
THE GREATEST EXTENT PERMISSIBLE UNDER APPLICABLE LAW.

If you are agree, run this command again
with the flag "--yes-rewrite-images".
!!!!!!!!!!!!!!!!!!!!!!


"""

from most_common_image_resolution_in_the_folder import most_common_image_resolution_in_the_folder

def process():
    resolution = most_common_image_resolution_in_the_folder()
    print('res =')
    print(resolution)



if __name__ == "__main__":
    if (len(sys.argv)==2) and (sys.argv[1]==expected_parameter):
        process()
    else:
        print(warning)

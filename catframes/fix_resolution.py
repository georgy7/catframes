#!/usr/bin/env python3 

import argparse
import os
import sys
import time
from multiprocessing import Pool

from catframes.most_common_image_resolution_in_the_folder import \
    scan_resolutions, \
    DEFAULT_METHOD, \
    list_all_methods_and_exit, \
    find_method_or_fail, \
    check_dependencies as most_common_image_resolution_check_dependencies
from catframes.utils import *
from catframes.version import version

YES_REWRITE_IMAGES_PARAMETER = '--yes-rewrite-images'
YES_REWRITE_IMAGES_FAKE_PARAMETER = YES_REWRITE_IMAGES_PARAMETER[:-1] + 'z'

assert len(YES_REWRITE_IMAGES_PARAMETER) == len(YES_REWRITE_IMAGES_FAKE_PARAMETER)
assert YES_REWRITE_IMAGES_PARAMETER != YES_REWRITE_IMAGES_FAKE_PARAMETER
assert '--' == YES_REWRITE_IMAGES_FAKE_PARAMETER[0:2]

DESCRIPTION = """
Part of catframes v{}.

This script scans JPEG and PNG files in a folder based on the
filename extensions, not their signatures!

The result image resolution is resolved automatically
as the most common resolution in the folder.

The slightly larger images are supposed to be cropped (to the left-top
corner). The slightly smaller images are supposed to be expanded with
a first color (green by default). And the much larger images are
supposed to be resized down.

The slightly different aspect ratios are supposed to be changed.
Images with very different aspect ratio are supposed to be centered
with a second color padding (default, turquoise).
"""

WARNING = """
THE CANVAS SIZE OF ALL IMAGES IN THE CURRENT DIRECTORY MAY BE
CHANGED, THEIR CONTENT MAY BE RESIZED.

THEY MAY ALSO BE RENAMED AND/OR BE CONVERTED IN-PLACE
TO ANOTHER FORMAT.

BE SURE, THAT YOU HAVE A COPY OF THE FOLDER BEFORE
RUNNING THIS COMMAND!

I MAKE NO REPRESENTATIONS OR WARRANTIES OF ANY KIND CONCERNING THE
SOFTWARE, EXPRESS, IMPLIED, STATUTORY OR OTHERWISE, INCLUDING WITHOUT
LIMITATION WARRANTIES OF TITLE, MERCHANTABILITY, FITNESS FOR
A PARTICULAR PURPOSE, NON INFRINGEMENT, OR THE ABSENCE OF LATENT OR
OTHER DEFECTS, ACCURACY, OR THE PRESENT OR ABSENCE OF ERRORS, WHETHER
OR NOT DISCOVERABLE, ALL TO THE GREATEST EXTENT PERMISSIBLE UNDER
APPLICABLE LAW.

IF YOU ARE AGREE, RUN THIS COMMAND
WITH THE FLAG "{}".
"""


def check_dependencies():
    check_dependency('identify', 'ImageMagick')
    check_dependency('mogrify', 'ImageMagick')
    most_common_image_resolution_check_dependencies()


def process(color1, color2, never_change_aspect_ratio, resolution_method_name):
    check_dependencies()

    resolution_method = find_method_or_fail(resolution_method_name)

    start_time = time.time()
    print('Resolving the most common resolution in the folder...')

    resolutions = scan_resolutions(True)
    target_resolution_string = resolution_method(resolutions)
    target_size = target_resolution_string.split('x')

    print("Got it.", target_resolution_string)
    print('Stage 1 completed in {} seconds.\n'.format(time.time() - start_time))

    if len(target_size) < 2:
        print('Bad resolution.')
        sys.exit(1)

    start_stage_2_time = time.time()
    print('Mogrifying the images...')

    i = 0
    with Pool(processes=4) as pool:
        for r in pool.imap_unordered(FixImage(target_size, color1, color2,
                                              never_change_aspect_ratio), list_of_files()):
            print(r, end='')
            i = i + 1
            if i % 50 == 0:
                sys.stdout.flush()

    print('\nStage 2 completed in {} seconds.\n'.format(time.time() - start_stage_2_time))
    print('-------------\nCompleted in {} seconds.\n'.format(time.time() - start_time))


class FixImage:
    def __init__(self, target_size, color1, color2, never_change_aspect_ratio):
        self.target_size = target_size
        self.target_aspect_ratio = float(target_size[0]) / float(target_size[1])
        self.target_resolution_string = target_size[0] + 'x' + target_size[1]
        self.color1 = color1
        self.color2 = color2
        self.never_change_aspect_ratio = never_change_aspect_ratio

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
            command = 'mogrify -background "{}" -extent {} -gravity NorthWest -quality 98 "{}"'
            execute(command, self.color1, self.target_resolution_string, f)
            return '.'
        else:
            image_aspect_ratio = float(image_resolution[0]) / float(image_resolution[1])
            if (abs(image_aspect_ratio - self.target_aspect_ratio) < 0.45) \
                    and not self.never_change_aspect_ratio:
                command = 'mogrify -resize {}! -gravity NorthWest -quality 98 "{}"'
                execute(command, self.target_resolution_string, f)
                return 's'
            else:
                command = 'mogrify -background "{}" -resize {} -extent {} -gravity Center -quality 98 "{}"'
                execute(command, self.color2, self.target_resolution_string, self.target_resolution_string, f)
                return 'c'


def run():
    if python_supports_allow_abbrev():
        parser = argparse.ArgumentParser(
            description=DESCRIPTION.format(version()),
            epilog=WARNING.format(YES_REWRITE_IMAGES_PARAMETER),
            allow_abbrev=False,
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
    else:
        parser = argparse.ArgumentParser(
            description=DESCRIPTION.format(version()),
            epilog=WARNING.format(YES_REWRITE_IMAGES_PARAMETER),
            formatter_class=argparse.RawDescriptionHelpFormatter
        )

    parser.add_argument(YES_REWRITE_IMAGES_PARAMETER, action='store_true',
                        help='You accept the risk.')

    if not python_supports_allow_abbrev():
        parser.add_argument(YES_REWRITE_IMAGES_FAKE_PARAMETER, action='store_true',
                            help='Do nothing. Hack for python 3.4.')

    parser.add_argument('--color1', type=color_argument, default='#41c148',
                        help='Default, green (#41c148).')

    parser.add_argument('--color2', type=color_argument, default='#0590b0',
                        help='Default, turquoise (#0590b0).')

    parser.add_argument('--never-change-aspect-ratio', action='store_true',
                        help='Margins are used if necessary.')

    parser.add_argument('--methods', action='store_true',
                        help='List all methods.')

    parser.add_argument('-m', '--method', default=DEFAULT_METHOD.code,
                        help='Set resolution selection method.')

    namespace = parser.parse_args(sys.argv[1:])

    if namespace.methods:
        list_all_methods_and_exit(for_fix_resolution=True)

    if namespace.yes_rewrite_images:
        process(namespace.color1,
                namespace.color2,
                namespace.never_change_aspect_ratio,
                namespace.method)
    else:
        parser.print_help()

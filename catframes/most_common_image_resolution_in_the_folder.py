#!/usr/bin/env python3 

import sys
import operator
import time
from multiprocessing import Pool, cpu_count
from catframes.utils import *


def check_dependencies():
    check_dependency('identify', 'ImageMagick')


def get_resolution(f):
    if os.path.isdir(f):
        return None
    out = os.popen("identify -format '%wx%h' \"{}\"".format(f)).read()
    if not out:
        os.rename(f, f + '_corrupted')
        return None
    return out


def scan_resolutions(statistics=False):
    check_dependencies()

    filenames = list_of_files()
    frequencies = {}

    with Pool(processes=cpu_count()) as pool:
        for resolution in pool.imap_unordered(get_resolution, filenames):
            if resolution in frequencies:
                frequencies[resolution] = frequencies[resolution] + 1
            else:
                frequencies[resolution] = 1

    if statistics:
        return frequencies
    else:
        result = max(frequencies, key=lambda key: frequencies[key])
        return result


def run():
    usage = '\n    catframes_most_common_image_resolution_in_the_folder [--statistics|-s]\n'

    if (len(sys.argv) > 1) and (sys.argv[1] in ['--help', '-h']):
        print(usage)

    elif (len(sys.argv) > 1) and (sys.argv[1] in ['--statistics', '-s']):
        start_time = time.time()
        stat = scan_resolutions(statistics=True)
        print()
        for k, v in sorted(stat.items(), key=operator.itemgetter(1), reverse=True):
            print("{} => {}".format(k, v))
        print('-------------\nCompleted in {} seconds.\n'.format(time.time() - start_time))

    elif len(sys.argv) > 1:
        print('Bad argument.')
        print(usage)

    else:
        print(scan_resolutions(), end='')

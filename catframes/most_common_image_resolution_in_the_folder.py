#!/usr/bin/env python3 

import sys
import operator
import time
from multiprocessing import Pool, cpu_count
from catframes.utils import *


def get_resolution(f):
    if os.path.isdir(f):
        return None
    out = os.popen("identify -format '%wx%h' \"{}\"".format(f)).read()
    if not out:
        os.rename(f, f + '_corrupted')
        return None
    return out


def most_common_image_resolution_in_the_folder(statistics=False):
    filenames = list_of_files()
    frequencies_of_resolutions = {}

    with Pool(processes=cpu_count()) as pool:
        for out in pool.imap_unordered(get_resolution, filenames):
            if out in frequencies_of_resolutions:
                frequencies_of_resolutions[out] = frequencies_of_resolutions[out] + 1
            else:
                frequencies_of_resolutions[out] = 1

    if statistics:
        return frequencies_of_resolutions
    else:
        result = max(frequencies_of_resolutions, key=lambda key: frequencies_of_resolutions[key])
        return result


def run():
    usage = '\n    catframes_most_common_image_resolution_in_the_folder [--statistics|-s]\n'

    if (len(sys.argv) > 1) and ((sys.argv[1] == '--help') or (sys.argv[1] == '-h')):
        print(usage)

    elif (len(sys.argv) > 1) and ((sys.argv[1] == '--statistics') or (sys.argv[1] == '-s')):
        start_time = time.time()
        stat = most_common_image_resolution_in_the_folder(statistics=True)
        print()
        for k, v in sorted(stat.items(), key=operator.itemgetter(1), reverse=True):
            print("{} => {}".format(k, v))
        print('-------------\nCompleted in {} seconds.\n'.format(time.time() - start_time))

    elif len(sys.argv) > 1:
        print('Bad argument.')
        print(usage)

    else:
        print(most_common_image_resolution_in_the_folder(), end='')

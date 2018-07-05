#!/usr/bin/env python3 

import os
import sys
import operator
import time

def most_common_image_resolution_in_the_folder(statistics = False):
    accepted_extensions = ["jpg", "jpeg", "png"]
    filenames = [fn for fn in os.listdir() if fn.split(".")[-1] in accepted_extensions]

    frequences_of_resolutions = {}

    for f in filenames:
        if os.path.isdir(f):
            continue

        out = os.popen("identify -format '%wx%h' \"{}\"".format(f)).read()
        if not out:
            os.rename(f, f + '_corrupted')
            continue

        if out in frequences_of_resolutions:
            frequences_of_resolutions[out] = frequences_of_resolutions[out] + 1
        else:
            frequences_of_resolutions[out] = 1

    if statistics:
        return frequences_of_resolutions
    else:
        result = max(frequences_of_resolutions, key=lambda key: frequences_of_resolutions[key])
        return result


if __name__ == "__main__":
    usage = '\n    most_common_image_resolution_in_the_folder.py [--statistics|-s]\n'

    if (len(sys.argv) > 1) and ((sys.argv[1] == '--help') or (sys.argv[1] == '-h')):
        print(usage)

    elif (len(sys.argv) > 1) and ((sys.argv[1] == '--statistics') or (sys.argv[1] == '-s')):
        start_time = time.time()
        stat = most_common_image_resolution_in_the_folder(statistics = True)
        print()
        for k, v in sorted(stat.items(), key=operator.itemgetter(1), reverse=True):
            print("{} => {}".format(k, v))
        print('-------------\nCompleted in {} seconds.\n'.format(time.time() - start_time))

    elif len(sys.argv) > 1:
        print('Bad argument.')
        print(usage)

    else:
        print(most_common_image_resolution_in_the_folder(), end='')

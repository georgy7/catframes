#!/usr/bin/env python3 

import os

def most_common_image_resolution_in_the_folder():
    accepted_extensions = ["jpg", "jpeg", "png"]
    filenames = [fn for fn in os.listdir() if fn.split(".")[-1] in accepted_extensions]

    frequences_of_resolutions = {}

    for f in filenames:
        out = os.popen("identify -format '%wx%h' \"{}\"".format(f)).read()
        if out in frequences_of_resolutions:
            frequences_of_resolutions[out] = frequences_of_resolutions[out] + 1
        else:
            frequences_of_resolutions[out] = 1

    result = max(frequences_of_resolutions, key=lambda key: frequences_of_resolutions[key])
    return result


if __name__ == "__main__":
    print(most_common_image_resolution_in_the_folder(), end='')

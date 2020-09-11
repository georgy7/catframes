#!/usr/bin/env python3 

import argparse
import errno
import operator
import os
import sys
import textwrap
import time
from multiprocessing import Pool, cpu_count

from catframes.utils import *
from catframes.version import version


def check_dependencies():
    check_dependency('identify', 'ImageMagick')


def get_resolution(f, rename_corrupted: bool):
    if os.path.isdir(f):
        return None
    out = os.popen("identify -format '%wx%h' \"{}\"".format(f)).read()
    if not out:
        if rename_corrupted:
            os.rename(f, f + '_corrupted')
        return None
    return out


def get_res_2(ab):
    a, b = ab
    return get_resolution(a, b)


def scan_resolutions(rename_corrupted: bool):
    check_dependencies()

    filenames = list_of_files()
    frequencies = {}

    packed_filenames = list(map(lambda a: (a, rename_corrupted), filenames))

    with Pool(processes=cpu_count()) as pool:
        for resolution in pool.imap_unordered(get_res_2, packed_filenames):
            if resolution in frequencies:
                frequencies[resolution] = frequencies[resolution] + 1
            else:
                frequencies[resolution] = 1

    return frequencies


class Method:
    def __init__(self, code, d1, d2, function):
        self.code = code
        self.description = d1
        self.description_fix_resolution = d2
        self.function = function

    def __call__(self, resolutions_and_frequencies_dict):
        return self.function(resolutions_and_frequencies_dict)

    def _print(self, text, indent_length):
        indent = ' ' * indent_length
        print(textwrap.fill(text,
                            width=70 - indent_length,
                            initial_indent=indent,
                            subsequent_indent=indent))

    def print_description(self, for_fix_resolution):
        print()
        self._print('"{}"'.format(self.code), 4)
        print()
        self._print(self.description, 8)
        if for_fix_resolution \
                and self.description_fix_resolution:
            print()
            self._print(self.description_fix_resolution, 8)
        print()


def filter_none_key(a: dict):
    return filter(lambda kv: kv[0], a.items())


def contain_object_keys(a: dict):
    return len(list(filter_none_key(a)))


def calc_weighted_average(xw_list: list):
    total_x = sum(map(lambda i: i[0] * i[1], xw_list))
    total_w = sum(map(lambda i: i[1], xw_list))
    return total_x / total_w


def x_from_gte_wa(xw_list: list):
    """
    Finds such X, which is greater than or equal to the weighted average X,
    and also has the maximum weight.

    If there is more than one result, it returns the maximum.

    :param xw_list:
    :return: X
    """
    weighted_average = calc_weighted_average(xw_list)
    xw_gte_wa = list(filter(lambda xw: xw[0] >= weighted_average, xw_list))
    max_weight = max(map(lambda xw: xw[1], xw_gte_wa))
    xw_with_max_weight = filter(lambda xw: max_weight == xw[1], xw_gte_wa)
    return max(map(lambda xw: xw[0], xw_with_max_weight))


def widths(resolutions: dict):
    return list(map(
        lambda t: (
            int(t[0].split('x')[0]), t[1]
        ),
        filter_none_key(resolutions)
    ))


def heights(resolutions: dict):
    return list(map(
        lambda t: (
            int(t[0].split('x')[1]), t[1]
        ),
        filter_none_key(resolutions)
    ))


METHOD_LIST = [
    Method(
        'mf',
        'Returns the most frequent resolution. Default method.',
        '',
        lambda resolutions: max(
            filter_none_key(resolutions),
            key=lambda kv: kv[1]
        )[0]
    ),
    Method(
        'gtewa',
        'Returns a combination of the most frequent values from the widths '
        'and heights, that are Greater Than or Equal to their Weighted '
        'Averages.',
        'This method may expand all frames in your folder if '
        'both portrait and landscape orientations exist. This may potentially '
        'run out of storage space. However, this method focuses on '
        'a reasonable trade-off between retaining detail in most frames and '
        'the size of the final video file.',
        lambda resolutions: '{}x{}'.format(
            x_from_gte_wa(widths(resolutions)),
            x_from_gte_wa(heights(resolutions))
        )
    ),
]

DEFAULT_METHOD = METHOD_LIST[0]


def find_method_or_fail(code):
    r = [x for x in METHOD_LIST if x.code == code]
    if r:
        return r[0]
    else:
        print('Unknown method code: {}.'.format(code), file=sys.stderr)
        exit(errno.EINVAL)


def run():
    parser = argparse.ArgumentParser(
        description='Part of catframes v{}.'.format(version()),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('-s', '--statistics', action='store_true',
                        help='Print all resolutions with file count in a table.')

    parser.add_argument('--methods', action='store_true',
                        help='List all methods.')

    parser.add_argument('-m', '--method', default=DEFAULT_METHOD.code,
                        help='Set resolution selection method.')

    namespace = parser.parse_args(sys.argv[1:])

    if namespace.methods:
        list_all_methods_and_exit(for_fix_resolution=False)

    start_time = time.time()
    resolutions = scan_resolutions(False)

    if namespace.statistics:
        print()
        for k, v in sorted(resolutions.items(), key=operator.itemgetter(1), reverse=True):
            print("{} => {}".format(k, v))
        print('-------------\nCompleted in {} seconds.\n'.format(time.time() - start_time))

        if contain_object_keys(resolutions):
            print('{} | {}'.format('Method'.rjust(25), 'Result'))
            print('{} | {}'.format(' ' + '-' * 24, '-' * 15))
            for m in METHOD_LIST:
                print('{} | {}'.format(m.code.rjust(25), m(resolutions)))
            print()

    elif contain_object_keys(resolutions):
        result = find_method_or_fail(namespace.method)(resolutions)
        print(result, end='')

    else:
        exit(errno.ENODATA)


def list_all_methods_and_exit(for_fix_resolution):
    print()
    for m in METHOD_LIST:
        m.print_description(for_fix_resolution)
    print()
    exit(0)

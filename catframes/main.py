import argparse
import os.path
import sys
from multiprocessing import Pool

from catframes.fix_resolution import process as process_fix_resolution, \
    check_dependencies as fix_resolution_check_dependencies
from catframes.to_video import ToVideoConverter, check_dependencies as to_video_check_dependencies
from catframes.utils import *
from catframes.version import version

SHORT_DESCRIPTION = """
Catframes v{}.

Catframes is a frame concatenation tool.
"""

USAGE = """
-------------------------

Catframes can resize all images in the current directory
to the same size and then concatenate them to a video file (mp4).

MAKE SURE YOU KNOW WHAT YOU ARE DOING!
THIS IS DANGEROUS FOR YOUR DATA.
THIS SCRIPT WILL MODIFY OR DELETE IMAGES IN THE CURRENT DIRECTORY.

PLEASE, MAKE A BACKUP IF THIS IS YOUR FIRST TRY!

NO WARRANTY! USE IT AT YOUR OWN RISK!

You have two options.
The first one:

    catframes --rewrite-images <OTHER PARAMETERS>

And the second:

    catframes --rewrite-and-then-remove-images  <OTHER PARAMETERS>

-------------------------
"""

DEFAULT_FPS = 1
DEFAULT_OUTPUT = 'output.mp4'


def output_argument(arg):
    if (not arg.endswith('.mp4')) or (len(arg) <= 4):
        raise argparse.ArgumentTypeError('I do not recommend other formats than mp4 for slideshow-like things. So, I blocked this.')

    if os.path.exists(arg):
        raise argparse.ArgumentTypeError('File already exists: ' + arg)

    return arg


def parse_arguments(converter, namespace):
    converter.output = namespace.output
    converter.fps = namespace.fps
    return namespace.draw_file_names


def check_common_dependencies():
    fix_resolution_check_dependencies()
    to_video_check_dependencies()


def check_annotate_frames_dependencies():
    check_dependency('convert', 'ImageMagick')
    check_dependency('mogrify', 'ImageMagick')


def select_font():
    prefix = 'Font: '
    prlen = len(prefix)
    out = os.popen("convert -list font").read()
    fonts = [str.strip(line)[prlen:] for line in str.splitlines(out) if prefix in line]

    default = 'DejaVu-Sans'
    if default in fonts:
        return default

    families = [
        'DejaVu',
        'Helvetica',
        'Ubuntu',
        'Arial',
        'Liberation',
        'Nimbus'
    ]

    for family in families:
        candidates = list(filter(lambda s: (family in s) and not ('Bold' in s) and not ('Italic' in s), fonts))
        candidates_mono = list(filter(lambda s: ('Mono' in s), candidates))

        if len(candidates_mono) > 0:
            return candidates_mono[0]
        elif len(candidates) > 0:
            return candidates[0]

        candidates = list(filter(lambda s: (family in s) and not ('Italic' in s), fonts))
        if len(candidates) > 0:
            return candidates[0]

    if len(fonts) > 0:
        return fonts[0]

    print('Could not select font.')
    exit(1)


def font_file_names(font, file_names):
    return list(map(lambda x: (font, x), file_names))


def draw_file_name(a):
    font = a[0]
    filename = a[1]
    command = 'mogrify -gravity North -fill white -font {} -verbose -undercolor \'#00000080\' -annotate +0+5 "{}" -quality 98 "{}"'
    execute(command, font, filename, filename)


def draw_file_names(font):
    print('Drawing the file names...')
    with Pool(processes=4) as pool:
        for _ in pool.imap_unordered(draw_file_name, font_file_names(font, list_of_files())):
            print('.', end='')
    print()
    print()


def just_rewrite_and_concatenate(namespace):
    check_common_dependencies()
    converter = ToVideoConverter()
    annotate_frames = parse_arguments(converter, namespace)

    if annotate_frames:
        check_annotate_frames_dependencies()
        font = select_font()
        print('Font: ' + font)

    process_fix_resolution(namespace.color1, namespace.color2)

    if annotate_frames:
        draw_file_names(font)

    converter.ready = True
    converter.process()


def rewrite_concatenate_and_remove_images(namespace):
    check_common_dependencies()
    converter = ToVideoConverter()
    annotate_frames = parse_arguments(converter, namespace)

    if annotate_frames:
        check_annotate_frames_dependencies()
        font = select_font()
        print('Font: ' + font)

    process_fix_resolution(namespace.color1, namespace.color2)

    if annotate_frames:
        draw_file_names(font)

    converter.delete_images = True
    converter.ready = True
    converter.process()


def run():
    if python_supports_allow_abbrev():
        parser = argparse.ArgumentParser(
            description=SHORT_DESCRIPTION.format(version()),
            epilog=USAGE,
            allow_abbrev=False,
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
    else:
        parser = argparse.ArgumentParser(
            description=SHORT_DESCRIPTION.format(version()),
            epilog=USAGE,
            formatter_class=argparse.RawDescriptionHelpFormatter
        )

    parser.add_argument('--version', '-version', action='store_true',
                        help='Show version.')

    parser.add_argument('--rewrite-images', action='store_true',
                        help='Make video and then remove source images.')

    parser.add_argument('--rewrite-and-then-remove-images', action='store_true',
                        help='Make video and then remove source images.')

    parser.add_argument('--rewrite-and-then-delete-images', action='store_true',
                        help='Make video and then remove source images. Alias for --rewrite-and-then-remove-images.')

    parser.add_argument('-o', '--output', type=output_argument, default=DEFAULT_OUTPUT,
                        help='Output filename. Default: {}.'.format(DEFAULT_OUTPUT))

    parser.add_argument('-r', '--fps', type=fps_argument, default=DEFAULT_FPS,
                        help='Frames per second (1-120). Default: {}.'.format(DEFAULT_FPS))

    parser.add_argument('--draw-file-names', action='store_true',
                        help='Draw filenames on the frames.')

    parser.add_argument('--color1', type=color_argument, default='#41c148',
                        help='Default, green (#41c148).')

    parser.add_argument('--color2', type=color_argument, default='#0590b0',
                        help='Default, turquoise (#0590b0).')

    namespace = parser.parse_args(sys.argv[1:])

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(0)

    if namespace.version:
        print(version())
        sys.exit(0)
    elif namespace.rewrite_and_then_remove_images or namespace.rewrite_and_then_delete_images:
        rewrite_concatenate_and_remove_images(namespace)
    elif namespace.rewrite_images:
        just_rewrite_and_concatenate(namespace)
    else:
        parser.print_help()
        sys.exit(1)


# For testing.
if __name__ == "__main__":
    run()

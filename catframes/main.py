import sys
import os.path

from catframes.fix_resolution import process
from catframes.to_video import ToVideoConverter
from catframes.version import version
from multiprocessing import Pool
from catframes.utils import *

usage = """
Catframes can resize all images in the current directory
to the same size and then concatenate them to a video file (mp4).

MAKE SURE YOU KNOW WHAT YOU ARE DOING!
THIS IS DANGEROUS FOR YOUR DATA.
THIS SCRIPT WILL MODIFY OR DELETE IMAGES IN THE CURRENT DIRECTORY.
PLEASE, MAKE A BACKUP IF THIS IS YOUR FIRST TRY.

NO WARRANTY! USE IT AT YOUR OWN RISK!

You have two options.
The first one:

    catframes --rewrite-images [-o pathToFile.mp4] [-r|--fps N] [--draw-file-names]

And the second:

    catframes --rewrite-and-then-remove-images [-o pathToFile.mp4] [-r|--fps N] [--draw-file-names]

"""

def set_output(converter, file_name):

    if (not file_name.endswith('.mp4')) or (len(file_name) <= 4):
        print('I do not recommend other formats than mp4 for slideshow-like things. So, I blocked this.')
        exit(1)

    if os.path.exists(file_name):
        print('File already exists: ' + file_name)
        exit(1)

    converter.output = file_name

def fps_parameter(s):
    return (s == '-r') or (s == '--fps')

def parse_arguments(converter):
    annotate = False

    if len(sys.argv) >= 3:
        if (len(sys.argv) == 4) and (sys.argv[2] == '-o'):
            set_output(converter, sys.argv[3])

        elif (len(sys.argv) == 5) and (sys.argv[2] == '-o') and (sys.argv[4] == '--draw-file-names'):
            set_output(converter, sys.argv[3])
            annotate = True

        elif (len(sys.argv) == 5) and (sys.argv[3] == '-o') and (sys.argv[2] == '--draw-file-names'):
            set_output(converter, sys.argv[4])
            annotate = True

        elif (len(sys.argv) == 4) and fps_parameter(sys.argv[2]):
            converter.fps = int(sys.argv[3])

        elif (len(sys.argv) == 5) and fps_parameter(sys.argv[2]) and (sys.argv[4] == '--draw-file-names'):
            converter.fps = int(sys.argv[3])
            annotate = True

        elif (len(sys.argv) == 5) and fps_parameter(sys.argv[3]) and (sys.argv[2] == '--draw-file-names'):
            converter.fps = int(sys.argv[4])
            annotate = True

        elif (len(sys.argv) >= 6) and fps_parameter(sys.argv[2]) and (sys.argv[4] == '-o'):
            converter.fps = int(sys.argv[3])
            set_output(converter, sys.argv[5])

        elif (len(sys.argv) >= 6) and fps_parameter(sys.argv[4]) and (sys.argv[2] == '-o'):
            set_output(converter, sys.argv[3])
            converter.fps = int(sys.argv[5])

        else:
            print(usage)
            exit(1)

        # Too many permutations. Last parameter check is enough at the moment.
        if len(sys.argv) >= 7:
            if sys.argv[6] == '--draw-file-names':
                annotate = True
            else:
                print(usage)
                exit(1)

        return annotate


def select_font():
    prefix = 'Font: '
    prlen = len(prefix)
    out = os.popen("convert -list font").read()
    fonts = [ str.strip(line)[prlen:] for line in str.splitlines(out) if prefix in line]

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

def just_rewrite_and_concatenate():
    converter = ToVideoConverter()
    annotate_frames = parse_arguments(converter)

    if annotate_frames:
        font = select_font()
        print('Font: ' + font)

    process()

    if annotate_frames:
        draw_file_names(font)

    converter.process()


def rewrite_concatenate_and_remove_images():
    converter = ToVideoConverter()
    annotate_frames = parse_arguments(converter)

    if annotate_frames:
        font = select_font()
        print('Font: ' + font)

    process()

    if annotate_frames:
        draw_file_names(font)

    converter.delete_images = True
    converter.process()


def run():
    if len(sys.argv) >= 2:
        if sys.argv[1] in ['--version', '-version', '-v']:
            print(version())
        elif sys.argv[1] == '--rewrite-images':
            just_rewrite_and_concatenate()
        elif sys.argv[1] in ['--rewrite-and-then-remove-images', '--rewrite-and-then-delete-images']:
            rewrite_concatenate_and_remove_images()
        else:
            print(usage)
    else:
        print(usage)


# For testing.
if __name__ == "__main__":
    run()

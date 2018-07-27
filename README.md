# Features

## 1. Fixing unstable frame size

Some software for some reason may save a part of frames with negligible cropping (about 8 pixels).

![Feature 1, cropping](/ReadMe%20images/case1_1.png)

![Feature 1, extending](/ReadMe%20images/case1_2.png)

Even if this is not your case (it scales the image, for instance),
if a resolution was changed to very close one,
it's still better to use cropping/extending on video, than scaling, to prevent further quality loss.

The script `catframes_fix_resolution` aligns the frames to the left-top corner.

## 2. Fixing the case, one changes camera settings during a day

A video file has a static resolution, but a camera resolution may be changed.
If the change is small, this case will be indistinguishable from the previous one.
But the considerable changes can be processed another way.

### A change to approximately the same aspect ratio

![Feature 2.1](/ReadMe%20images/case2_1.png)

### A change to a very different aspect ratio

![Feature 2.2](/ReadMe%20images/case2_2.png)

# Requirements

1. Bash
2. Python 3
3. ImageMagick
4. FFmpeg

# Usage

1. `catframes_fix_resolution` ensures, that all images in the current directory have the same resolution.
    1. Finds out, what resolution is most common in this directory.
        1. Renames corrupted images to `{original_filename}_corrupted`.
    2. Converts all the pictures **in place** to this resolution.
2. `images_to_h264.sh [--delete-images] [-o pathToFile.mkv]` compresses them all
to a single video file with 1 frame per second.
Please, use `images_to_h264.sh [h|help|-h|-help|--help]` for more information.

# Installation

On Unix-like systems:

```
sudo python3 -m pip install --force-reinstall catframes
```

# Also

You can use the script separately.

It scans all JPEG and PNG files in a folder (based on the file name extensions, not [their headers](https://en.wikipedia.org/wiki/List_of_file_signatures)).

```
$ catframes_most_common_image_resolution_in_the_folder [--statistics|-s]

1280x720 => 3
800x800 => 2
-------------
Completed in 0.023589134216308594 seconds.
```

```
$ var1=`catframes_most_common_image_resolution_in_the_folder`
$ echo $var1
1280x720
```

# Disclaimer

*I make no representations or
warranties of any kind concerning the software, express, implied,
statutory or otherwise, including without limitation warranties of
title, merchantability, fitness for a particular purpose, non
infringement, or the absence of latent or other defects, accuracy, or
the present or absence of errors, whether or not discoverable, all to
the greatest extent permissible under applicable law.*

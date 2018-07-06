*These scripts are experimental, and I make no representations or
warranties of any kind concerning the software, express, implied,
statutory or otherwise, including without limitation warranties of
title, merchantability, fitness for a particular purpose, non
infringement, or the absence of latent or other defects, accuracy, or
the present or absence of errors, whether or not discoverable, all to
the greatest extent permissible under applicable law.*

## Requirements

1. Bash
2. Python 3
3. ImageMagick
4. FFmpeg

## Usage

1. `extent_override.py` ensures, that all images in the current directory have the same resolution.
    1. Finds out, what resolution is most common in this directory.
        1. Renames corrupted images to `{original_filename}_corrupted`.
    2. Converts all the pictures to this resolution.
        1. If a frame much bigger that the target resolution (more than 10% at width or height), it will be resized without preserving its aspect ratio. Because no one wants to lose a large portion of a frame on cctv.
        2. If a frame slightly larger, it will be cropped (that looks nicer, this avoids jitter).
        3. If a frame smaller, it will be extended (aligned to the left-top) with a green color.
2. `images_to_h264.sh [--delete-images]` compresses them all to a single video file with 1 frame per second.

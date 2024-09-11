Catframes
=========

It concatenates frames.

With this software, you can

* create a timelapse video
* turn an animation rendered in a PNG sequence into a video
* compress your selfies
* compress a sequence of frames from CCTV

The script takes folders with images and outputs MP4 or WebM.

It has GUI: `catmanager`


What exactly does it do
-----------------------

1. It takes the folders in the order you specify them.
2. It sorts images by name in natural order in each folder separately.
3. It checks the resolution of each image and counts their numbers.
4. It heuristically chooses the video resolution from the collected data.
5. It resizes each image (on the fly) to fit into that resolution, preserving the aspect ratio and aligning the images in the center.
6. It overlays various text information on the frames, if you specified this in the arguments.
7. It concatenates the frames, having a fairly high resistance to emergency.


Installation
------------

Do this as root for system-wide installation:

```
python3 -m pip install catframes
```

You can also copy `catframes.py` to `/usr/local/bin` manually.
But then you will also need to install [Pillow](https://pypi.org/project/Pillow/#files).

Dependencies that are not installable from PYPI:

1. FFmpeg
2. Monospaced fonts

Alpine: `apk add ffmpeg font-dejavu`

Debian/Ubuntu: `apt-get install ffmpeg fonts-dejavu`

Centos/RHEL: `yum install ffmpeg dejavu-sans-mono-fonts`

Windows: [FFmpeg builds](https://ffmpeg.org/download.html); Courier New included.


Usage
-----

If you are launching the program for the first time,
use `--limit` option to try different options on short video samples.

    catframes --limit=3 sourceFolder sample.mp4

The command to run it with default settings looks like this:

    catframes folderA folderB folderC result.webm

For automatic launches (through a CRON job, etc.), it's better to add `--force` and `--sure` options:

    catframes -sf folderA folderB folderC result.webm


Default settings
----------------

**Frame rate:** 30 frames per second.

You may change it with `-r` parameter.
Acceptable values are from 1 to 60.
All source frames will be included, so this parameter
determines speed of your video record.

**Compression quality:** medium.

You may change it with `-q` parameter.
Acceptable values are `poor`, `medium`, `high`.

**Margin (background) color:** black.

You may change it with `--margin-color`.
It takes values in formats `#rrggbb` and `#rgb` (hexadecimal digits; `#abc` means `#aabbcc`).


Text overlays
-------------

There is a 3 by 3 grid. You can place labels in all cells except the central one.

Please, use `--left`, `--right`, `--top`, `--left-top`, etc.

One of the cells may be reserved for important warnings.
It is set by `WARN` value (in any case). By default, this is the top cell.

You can use any constant text in the labels, including line feeds (`\n`).
You can also use a limited set of functions in curly brackets that output
information about the source image or about the system.

To prevent special characters from being interpreted, you should use
*single quotes in Unix Shell*, however,
you must use double quotes in the Windows command line.

Example (Bash):

```
catframes \
    -r=5 --limit=10 \
    --left-top='Frame {frame:video}' \
    --left-bottom='{dir}/{fn}\n\nModified: {mtime}' \
    --right-bottom='Compressed {vtime:%Y-%m-%d %H:%M}' \
    folder video.webm
```

Read more about these functions in the docs.


See also
--------

**[Documentation](https://itustinov.ru/cona/latest/docs/html/catframes.html)** (in Russian, outdated)

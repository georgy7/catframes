Catframes
=========

It concatenates frames.

With this software, you can, for example,

* create a timelapse video,
* turn an animation rendered in a PNG sequence into a video,
* compress your selfies,
* compress a sequence of frames from CCTV.

The script takes folders with JPEG, PNG, QOI and PCX files as input and outputs MP4 or WebM.

It has GUI: `catmanager`!

Installation
------------

### From PyPI

I recommend to do it as root.

```
python3 -m pip install catframes
```

Installing dependencies:

Alpine: `apk add ffmpeg font-dejavu`

Debian/Ubuntu: `apt-get install ffmpeg fonts-dejavu`

Centos/RHEL: `yum install ffmpeg dejavu-sans-mono-fonts`

Windows: [Get FFmpeg Windows builds](https://ffmpeg.org/download.html)


### From source (Linux, Unix-like)

Catframes is a script. Everything, including tests,
is contained in a single file that you can upload
to a system yourself.

```
cp catframes.py /usr/local/bin/
chmod 755       /usr/local/bin/catframes.py
ln -s /usr/local/bin/catframes.py /usr/local/bin/catframes
```

Installing dependencies: exactly the same, except for [Pillow](https://python-pillow.org/).

If you don't want to use pip, the library usually can be installed from operating system repository.

Alpine: `apk add py3-pillow`

Debian/Ubuntu: `apt-get install python3-pil`

Centos/RHEL: `yum install python3-pillow`

It is better to run tests as a regular user.

```
python3 -m unittest discover /usr/local/bin/ -p catframes.py
```


### From source (Windows)

0. You need Python3 to be available in `cmd` as `python3`.
1. Copy both `catframes.py` and `catframes.bat` to a folder (for instance, `C:\Program Files\MyScripts`).
2. Add this folder to `PATH` environment variable.
3. Install [FFmpeg](https://ffmpeg.org/download.html).
4. Add the folder, where `ffmpeg.exe` is installed, to the `PATH` environment variable.
5. Install Pillow.

You don't have to install fonts, because Windows already has Courier New.

You may install Pillow, using `pip`.

If you don't use `pip` for some reason, you may
[download Pillow `*.whl` file](https://pypi.org/project/Pillow/#files),
corresponding to your Python version, unpack it and put `PIL`
in your Python interpreter directory.
This usually works.
Files with `whl` extension are ordinary ZIP archives.

If everything is done, the following commands will work in any folder.

```
ffmpeg -version

catframes --help
```

You may run unit tests with the following line:

```
python3 -m unittest discover "C:\Program Files\MyScripts" -p catframes.py
```


Usage
-----

Video encoding is a long process. If you are launching the program for the first time,
a good way to try different options is to use `--limit` to make short video samples.

The command to run it with default settings looks like this:

    catframes folderA folderB folderC result.webm

For automatic launches (through a CRON job, etc.), I recommend to add these options:

    catframes -sf folderA folderB folderC result.webm

### Default settings

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

### Text overlays

There is a 3 by 3 grid. You can place labels in all cells except the central one.

Please, use `--left`, `--right`, `--top`, `--left-top`, etc.

**Important:** One of the cells must be reserved for important warnings.
It is set by `WARN` value (in any case). By default, this is the top cell.

You can use any constant text in the labels, including line feeds (`\n`).
You can also use a limited set of functions in curly brackets that output
information about the source image or about the system.

To prevent special characters from being interpreted, you should use
*single quotes in Unix Shell*, however,
you **must** use double quotes in the Windows command line.

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

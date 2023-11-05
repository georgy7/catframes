Catframes
=========

A script that concatenates frames. FFmpeg wrapper.


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


### From source (Linux, Unix-like)

Catframes is a script. Everything, including tests,
is contained in a single file that you can upload
to the system yourself.

```
cp catframes.py /usr/local/bin/
chmod 755       /usr/local/bin/catframes.py
ln -s /usr/local/bin/catframes.py /usr/local/bin/catframes
```

Installing dependencies: exactly the same, except for [Pillow](https://python-pillow.org/).
If you don't want to use pip, the library usually can be installed from the operating system repository.

Alpine: `apk add py3-pillow`

Debian/Ubuntu: `apt-get install python3-pil`

Centos/RHEL: `yum install python3-pillow`

It is better to run tests as a regular user.

```
python3 -m unittest discover /usr/local/bin/ -p catframes.py
```


### From source (Windows)

0. You need Python3 to be available in `cmd` as `python3`.
1. Copy both `catframes.py` and `catframes.bat` to a folder (for instance, `C:\Program Files\MyScripts`).
2. Add this folder to `PATH` environment variable.
3. Install [FFmpeg](https://ffmpeg.org/download.html).
4. Add the folder, where installed `ffmpeg.exe`, to the `PATH` environment variable.
5. Install Pillow.

You don't have to install fonts, because Windows already has Courier New.

You may install Pillow, using `pip`.

If you don't use `pip` for some reason, you can
[download Pillow `*.whl` file](https://pypi.org/project/Pillow/#files),
corresponding to your Python version, unpack it and put `PIL`
in your Python interpreter directory.
This usually works.
Files with the `whl` extension are ordinary ZIP archives.

If everything is done, the following commands will work in any folder.

```
ffmpeg --help

catframes --help
```

The command that runs tests:

```
python3 -m unittest discover "C:\Program Files\MyScripts" -p catframes.py
```


See also
--------

**[Documentation (in Russian)](https://itustinov.ru/cona/latest/docs/html/catframes.html)**

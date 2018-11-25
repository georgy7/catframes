Catframes
=========

 | |Python versions: 3.3 and above| |PyPI| |License: CC0-1.0|
 | |GitHub code size in bytes| |Code quality| |Code alerts|

Features
--------

1. Fixing unstable frame size
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Some software for some reason may save a part of frames with negligible
cropping (about 8 pixels).

.. figure:: https://github.com/georgy7/catframes/raw/master/ReadMe%20images/case1_1.png
   :alt: Feature 1, cropping

   Feature 1, cropping

.. figure:: https://github.com/georgy7/catframes/raw/master/ReadMe%20images/case1_2.png
   :alt: Feature 1, extending

   Feature 1, extending

Even if this is not your case (it scales the image, for instance), if a
resolution was changed to very close one, it's still better to use
cropping/extending on video, than scaling, to prevent further quality
loss.

The script aligns the frames to the
left-top corner.

2. Fixing the case, one changes camera settings during a day
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A video file has a static resolution, but a camera resolution may be
changed. If the change is small, this case will be indistinguishable
from the previous one. But the considerable changes can be processed
another way.

A change to approximately the same aspect ratio
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. figure:: https://github.com/georgy7/catframes/raw/master/ReadMe%20images/case2_1.png
   :alt: Feature 2.1

A change to a very different aspect ratio
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. figure:: https://github.com/georgy7/catframes/raw/master/ReadMe%20images/case2_2.png
   :alt: Feature 2.2

Requirements
------------

1. Python 3
2. ImageMagick
3. FFmpeg

Installation
------------

On Ubuntu 18.10 and most of Linux distributions:

::

    sudo python3 -m pip install --prefix /usr/local catframes

On Windows/ReactOS:

::

    pip install catframes

Usage
-----

|Usage video|

All these scripts scan JPEG and PNG files in a folder based on the file
name extensions, *not* `their
signatures <https://en.wikipedia.org/wiki/List_of_file_signatures>`__.

1. ``catframes_fix_resolution`` ensures, that all images in the current
   directory have the same resolution.

   1. Finds out, what resolution is most common in this directory.

      1. Renames corrupted images to ``{original_filename}_corrupted``.

   2. Converts all the pictures **in place** to this resolution.

2. ``catframes_to_video [--delete-images] [-o pathToFile.mp4]``
   compresses them all to a single video file with 1 frame per second.
   Please, use ``catframes_to_video [--help]`` for more information.

You can also use Catframes to detect common resolution in a folder.

::

    $ catframes_most_common_image_resolution_in_the_folder [--statistics|-s]

    1280x720 => 3
    800x800 => 2
    -------------
    Completed in 0.023589134216308594 seconds.

::

    $ var1=`catframes_most_common_image_resolution_in_the_folder`
    $ echo $var1
    1280x720

But this script renames corrupted images as well.

Disclaimer
----------

*I make no representations or warranties of any kind concerning the
software, express, implied, statutory or otherwise, including without
limitation warranties of title, merchantability, fitness for a
particular purpose, non infringement, or the absence of latent or other
defects, accuracy, or the present or absence of errors, whether or not
discoverable, all to the greatest extent permissible under applicable
law.*

.. |GitHub code size in bytes| image:: https://img.shields.io/github/languages/code-size/georgy7/catframes.svg
   :target: #
.. |License: CC0-1.0| image:: https://img.shields.io/badge/License-CC0%201.0-lightgrey.svg
   :target: http://creativecommons.org/publicdomain/zero/1.0/
.. |Python versions: 3.3 and above| image:: https://img.shields.io/pypi/pyversions/catframes.svg?style=flat
   :target: #
.. |PyPI| image:: https://img.shields.io/pypi/v/catframes.svg
   :target: https://pypi.org/project/catframes/
.. |Code quality| image:: https://img.shields.io/lgtm/grade/python/g/georgy7/catframes.svg?logo=lgtm&logoWidth=18
   :target: https://lgtm.com/projects/g/georgy7/catframes/context:python
.. |Code alerts| image:: https://img.shields.io/lgtm/alerts/g/georgy7/catframes.svg?logo=lgtm&logoWidth=18
   :target: https://lgtm.com/projects/g/georgy7/catframes/alerts

.. |Usage video| image:: https://github.com/georgy7/catframes/raw/master/ReadMe%20images/usage_webm_thumbnail.png
   :target: https://github.com/georgy7/catframes/raw/master/ReadMe%20images/usage.webm

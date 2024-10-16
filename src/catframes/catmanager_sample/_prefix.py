#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import threading
import platform
import random
import time
import signal
import sys
import os
import io
import re
import copy
import shutil
import base64
import configparser

# import requests

from tkinter import *
from tkinter import ttk, font, filedialog, colorchooser
from abc import ABC, abstractmethod
from typing import Optional, Tuple, Dict, List, Callable, Union
from PIL import Image, ImageTk


#  Если где-то не хватает импорта, не следует добавлять его в catmanager.py,
#  этот файл будет пересобран утилитой _code_assembler.py, и изменения удалятся.
#  Недостающие импорты следует указывать в _prefix.py, именно они пойдут в сборку.


USER_DIRECTORY = os.path.expanduser("~")
CONFIG_FILENAME = ".catmanager.ini"
PREVIEW_DIRNAME = ".cat_temp"
PREVIEW_FILENAME = ".preview.{ex}"

DEFAULT_CANVAS_COLOR = "#000000"  # цвет стандартного фона изображения

# Цвета для главного окна
MAIN_TOOLBAR_COLOR = "#E0E0E0"
MAIN_TASKLIST_COLOR = "#CDCDCD"
MAIN_TASKBAR_COLORS = {"Running": "#E0E0E0", "Error": "#FF9B9B", "Success": "#6AFB84"}

# константы имён ошибок
INTERNAL_ERROR = "internal"
NO_FFMPEG_ERROR = "noffmpeg"
NO_CATFRAMES_ERROR = "nocatframes"
START_FAILED_ERROR = "failed"

SYSTEM_PATH = "system_path"

FOLDER_ICON_BASE64 = """
iVBORw0KGgoAAAANSUhEUgAAABIAAAASCAYAAABWzo5XAAAABGdBTUEAALGPC/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA
6AAAdTAAAOpgAAA6mAAAF3CculE8AAAACXBIWXMAAA7AAAAOwAFq1okJAAAABmJLR0QA/wD/AP+gvaeTAAAAB3RJTUUH6AcU
DwU7nLh1ywAAACV0RVh0ZGF0ZTpjcmVhdGUAMjAyNC0wNy0yMFQxNTowNTo1OCswMDowMNM5N1wAAAAldEVYdGRhdGU6bW9k
aWZ5ADIwMjQtMDctMjBUMTU6MDU6NTgrMDA6MDCiZI/gAAAAVElEQVQ4T2OgFmAEEf8XMPwH87AAxgSIGkKAEZ8hMECMYRCD
tDSgXPIAo9kNRsb/pzQIuogYwASlKQajBhEGowYRBoPPIEgxQmF+A2VaKJNSwMAAALsJEQz8R0D5AAAAAElFTkSuQmCC
"""

PALETTE_ICON_BASE64 = """
iVBORw0KGgoAAAANSUhEUgAAABIAAAASCAYAAABWzo5XAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAA
DsEAAA7BAbiRa+0AAAJKSURBVDhPdZTLb01RFIfXKerZ1vtZ79DUSGIgJg0zj8Sgf4GhoaGRhH+AxNiQiH+gREJEECFhIhIi
IW5FEJVe1dbF8X377t3eeqzk22vvc/b97bXWWftWNRb/sqEq4h1eJhcz9Lepb+H/tq7sZ+00AidgEfNuSDtYpwWC1Uk458M5
NlfoEj9Yju+FpTAj5LAQloEv2VRdi2i2mLdtVmgEkR68exUxG4UMJm1zsQSKGPQ+wretLfSS3WvwazPOV4KC8yHmgQI+XAfr
s4fqM74I+XxjJtc0NsAqWABpcOGLLR30x2QSR2iU2MdIqaXINtgJuzPuNZs0bIdB2AMDMYZwg7q9YfWEhKr7ddRmbynF7M2s
q8HwAM7r9zOcgYPxHtGPzJownfkO1RWErKc5itUoZTXIgesMR0biXhxOLfUN/FY/4VfGRqwuIOSkPPwBnjABo3DZVIaexdG7
beHSFX6DcriBVKcQ8odTYJjjYOivkt/HeDHixoGIs6ROqjt4Yup2iqWwb/0U1TBChvsVjEKRRjpnLxwDOvkpsVxlehueR/RR
oNVMS1fp010bJLgvLCzgRCr3LlDoEByPeMH5XrGHgFC8hg+IUJM+pg28RxNB8DW6EbHJFBE/tw1GAp1ttDWzmSy4KdZRS0LN
VPfSieyITaCo51HWzsa289XPlP+OJKTVqbwroNxaf0k0NVvcZWVLUfJVG3+MzzYjpNVxk9EyerS7ubn2RBFSxCA5r2Zrj72Q
7b9/bFXcYaROLe7JJ6ZvgWLWw7790yJ+A6mSiwF9eeKxAAAAAElFTkSuQmCC
"""

PLAY_ICON_BASE64 = """
iVBORw0KGgoAAAANSUhEUgAAABIAAAASCAYAAABWzo5XAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAA
DsMAAA7DAcdvqGQAAABeSURBVDhPzdCxDcAgDERRZmEelmVCJ1eArJMJtinCk67B0i8o8qq9zWnW24orxO8Wd4hvLBTiuxYO
YZZUCGPpEKYdhbDhOITBPaHh/89mqZAlHFoJhb64Qzuu0J7IA1aJ3KICtYk1AAAAAElFTkSuQmCC
"""

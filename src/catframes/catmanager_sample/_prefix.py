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
import base64
# import requests

import tempfile
import logging
from logging.handlers import WatchedFileHandler
from pathlib import Path

from tkinter import *
from tkinter import ttk, font, filedialog, colorchooser, scrolledtext
from abc import ABC, abstractmethod
from typing import Optional, Tuple, Dict, List, Callable, Union
from PIL import Image, ImageTk

DEFAULT_CANVAS_COLOR = '#000000'  # цвет стандартного фона изображения

# Цвета для главного окна
MAIN_TOOLBAR_COLOR = '#E0E0E0'
MAIN_TASKLIST_COLOR = '#CDCDCD'
MAIN_TASKBAR_COLORS = {
    'Running': '#E0E0E0', 
    'Error': '#FF9B9B', 
    'Success': '#6AFB84'
}

# константы имён ошибок
INTERNAL_ERROR = 'internal'
NO_FFMPEG_ERROR = 'noffmpeg'
NO_CATFRAMES_ERROR = 'nocatframes'
START_FAILED_ERROR = 'failed'

#  Если где-то не хватает импорта, не следует добавлять его в catmanager.py,
#  этот файл будет пересобран утилитой _code_assembler.py, и изменения удалятся.
#  Недостающие импорты следует указывать в _prefix.py, именно они пойдут в сборку.

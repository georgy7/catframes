#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import threading
import random
import time
import signal
import sys
import os
import io
import re
# import requests

from tkinter import *
from tkinter import ttk, font, filedialog, colorchooser
from abc import ABC, abstractmethod
from typing import Optional, Tuple, Dict, List, Callable, Union
from PIL import Image, ImageTk

DEFAULT_COLOR = '#888888'  # цвет стандартного фона изображения

# константы имён ошибок
INTERNAL_ERROR = 'internal'
NO_FFMPEG_ERROR = 'noffmpeg'
NO_CATFRAMES_ERROR = 'nocatframes'
START_FAILED_ERROR = 'failed'

#  Если где-то не хватает импорта, не следует добавлять его в catmanager.py,
#  этот файл будет пересобран утилитой _code_assembler.py, и изменения удалятся.
#  Недостающие импорты следует указывать в _prefix.py, именно они пойдут в сборку.

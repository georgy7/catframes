#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import threading
import time
import os
import re
from os.path import isfile, join
import random
import subprocess
import requests
import signal

from tkinter import *
from tkinter import ttk, font, filedialog, colorchooser
from abc import ABC, abstractmethod
from typing import Optional, Tuple, Dict, List, Callable, Union
from PIL import Image, ImageTk

DEFAULT_COLOR = '#888888'  # цвет стандартного фона изображения

#  Если где-то не хватает импорта, не следует добавлять его в catmanager.py,
#  этот файл будет пересобран утилитой _code_assembler.py, и изменения удалятся.
#  Недостающие импорты следует указывать в _prefix.py, именно они пойдут в сборку.

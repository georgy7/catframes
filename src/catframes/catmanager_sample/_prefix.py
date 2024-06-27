#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
from tkinter import Tk, Toplevel, ttk, Canvas
from abc import ABC, abstractmethod
from typing import Optional, Tuple, Dict, Callable
import threading

#  Если где-то не хватает импорта, не следует добавлять его в catmanager.py,
#  этот файл будет пересобран утилитой _code_assembler.py, и изменения удалятся.
#  Недостающие импорты следует указывать в _prefix.py, именно они пойдут в сборку.
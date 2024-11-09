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
from unittest import TestCase
from abc import ABC, abstractmethod
from typing import Optional, Tuple, Dict, List, Callable, Union
try:
    from PIL import Image, ImageTk
    PIL_FOUND_FLAG = True
except:
    PIL_FOUND_FLAG = False


#  Если где-то не хватает импорта, не следует добавлять его в catmanager.py,
#  этот файл будет пересобран утилитой _code_assembler.py, и изменения удалятся.
#  Недостающие импорты следует указывать в _prefix.py, именно они пойдут в сборку.


# коэффициент масштабирования окна в линуксе
LINUX_SIZING = 1.1

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

ERROR_ICON_BASE64 = """
iVBORw0KGgoAAAANSUhEUgAAABYAAAAWCAYAAADEtGw7AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAA
Dr0AAA69AUf7kK0AAADPSURBVEhLtZTBDcIwDEUNI/TMkRnYgzM7MAw7cIU56C6wQhpbSVUSfzug5EtRo8R+cr/d7t6HY6AB
2qdnd31VPN3uaUf0uV7SzhbKWcEScD7Joeg5u3ArB1sRE7bVlKqghWyPAdyDitiKvMLjFVTF819ieFXjBquJ/onAXdkPdY6b
XjULNFn1WAJzhZYAlAWb58INKGvYlwfBrs/xThvFLBXc3DwDXoEhlP3WPEfw7VD3/EBWcGtCa6w9FWCkWuYcg5059eDjf/S9
ZXv8t4gWlzE1GW5peVYAAAAASUVORK5CYII=
"""

OK_ICON_BASE64 = """
iVBORw0KGgoAAAANSUhEUgAAABYAAAAWCAYAAADEtGw7AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAA
Dr0AAA69AUf7kK0AAAC5SURBVEhL1ZXbCYRADEXjVuC/f7ZgGws2sWVtExZiGf5vBy4XJpJ5JGYdhfXA4CB6c8gEbfrpudIF
PML1dKqN5+EVdkTD/A67SmOEtt24LVnkslYcDmZbjf8yLtl+lum8w7OIxk0bHYnHFmzG/AIvWYQp3dNQW6GFe2yB2WMZ/ost
yHqcGgFYAa8tiIzxEIdIEFgqaJG1QgtPsWxBscfecAv18KzwPVtgTkWNuetDn47ani242z+P6Atnwl4nWv9uvAAAAABJRU5E
rkJggg==
"""



    #  из файла sets_utils.py:

"""
Класс языковых настроек содержит большой словарь, 
в котором для каждого языка есть соответсвия названия
виджета, и текста, который в этом виджете расположен.

Добавление нового ключа в этот словарь должно быть с
добавлением всех внутренних ключей по аналогии с другими.

Если в процессе будет допущена ошибка, или gui запросит
текст для виджета, который не прописан, в качестве текста
вернётся строка из прочерков "-----" для быстрого обнаружения. 
"""


class Lang:
    """Класс языковых настроек.
    Позволяет хранить текущий язык,
    И извлекать его текстовики.

    При добавлении новых языков в словарь data,
    их названия будут сами подтягиваться в поле настроек.
    """

    data = {  # языковые теги (ключи) имеют вид: "область.виджет"
        "english": {
            "root.title": "CatFrames",
            "root.openSets": "Settings",
            "root.newTask": "Create",
            "bar.active": "processing",
            "bar.inactive": "complete",
            "bar.btInfo": "Info",
            "bar.btCancel": "Cancel",
            "bar.btDelete": "Delete",
            "bar.lbEmpty": "Your projects will appear here",
            "bar.error.noffmpeg": "Error! FFmpeg not found!",
            "bar.error.nocatframes": "Error! Catframes not found!",
            "bar.error.internal": "Internal process error!",
            "bar.error.failed": "Error! Process start failed!",
            "bar.lbQuality": "Quality:",
            "bar.lbFramerate": "Framerate:",
            "bar.lbColor": "Color:",
            "sets.title": "Settings",
            "sets.lbLang": "Language:",
            "sets.lbTheme": "Theme:",
            "sets.btApply": "Apply",
            "sets.btSave": "Save",
            "task.title": "New Task",
            "task.title.view": "Task settings view",
            "task.initText": "Add a directory\nof images",
            "task.lbColor": "Background:",
            "task.lbFramerate": "Framerate:",
            "task.lbQuality": "Quality:",
            "task.cmbQuality": ("high", "medium", "poor"),
            "task.lbResolution": "Render resolution:",
            "task.lbSaveAs": "Save as:",
            "task.btCreate": "Create",
            "task.btPathChoose": "choose",
            "task.lbCopy": "Copy cli:",
            "task.btCopyBash": "Bash",
            "task.btCopyWin": "Win",
            "task.cmbTime": ("1 sec", "2 sec", "3 sec", "4 sec", "5 sec"),
            "task.btPrevCancel": "Cancel",
            "task.lbPrevSign": "Processing preview...",
            "dirs.lbDirList": "List of source directories:",
            "dirs.btAddDir": "Add",
            "dirs.btRemDir": "Remove",
            "dirs.DirNotExists": "Doesn't exists. Removing...",
            "warn.exit.title": "Warning",
            "warn.exit.lbWarn": "Warning!",
            "warn.exit.lbText": "Incomplete tasks!",
            "warn.exit.btAccept": "Leave",
            "warn.exit.btDeny": "Back",
            "warn.cancel.title": "Warning",
            "warn.cancel.lbWarn": "Are you sure",
            "warn.cancel.lbText": "You want to cancel the task?",
            "warn.cancel.btAccept": "Yes",
            "warn.cancel.btDeny": "Back",
            "noti.title": "Error",
            "noti.lbWarn": "Invalid port range!",
            "noti.lbText": "The acceptable range is from 10240 to 65025",
            "noti.lbText2": "The number of ports is at least 100",
            "checker.title": "Necessary modules check",
        },
        "русский": {
            "root.title": "CatFrames",
            "root.openSets": "Настройки",
            "root.newTask": "Создать",
            "bar.lbActive": "обработка",
            "bar.lbInactive": "завершено",
            "bar.btInfo": "Инфо",
            "bar.btCancel": "Отмена",
            "bar.btDelete": "Удалить",
            "bar.lbEmpty": "Здесь появятся Ваши проекты",
            "bar.error.noffmpeg": "Ошибка! FFmpeg не найден!",
            "bar.error.nocatframes": "Ошибка! Catframes не найден!",
            "bar.error.internal": "Внутренняя ошибка процесса!",
            "bar.error.failed": "Ошибка при старте процесса!",
            "bar.lbQuality": "Качество:",
            "bar.lbFramerate": "Частота:",
            "bar.lbColor": "Цвет:",
            "sets.title": "Настройки",
            "sets.lbLang": "Язык:",
            "sets.lbTheme": "Тема:",
            "sets.btApply": "Применить",
            "sets.btSave": "Сохранить",
            "task.title": "Новая задача",
            "task.title.view": "Просмотр настроек задачи",
            "task.initText": "Добавьте папку\nс изображениями",
            "task.lbColor": "Цвет фона:",
            "task.lbFramerate": "Частота кадров:",
            "task.lbQuality": "Качество:",
            "task.cmbQuality": ("высокое", "среднее", "низкое"),
            "task.lbResolution": "Разрешение рендера:",
            "task.lbSaveAs": "Сохранить как:",
            "task.btCreate": "Создать",
            "task.btPathChoose": "выбрать",
            "task.lbCopy": "Копировать cli:",
            "task.btCopyBash": "Bash",
            "task.btCopyWin": "Win",
            "task.cmbTime": ("1 сек", "2 сек", "3 сек", "4 сек", "5 сек"),
            "task.btPrevCancel": "Отмена",
            "task.lbPrevSign": "Создание предпросмотра...",
            "dirs.lbDirList": "Список директорий источников:",
            "dirs.btAddDir": "Добавить",
            "dirs.btRemDir": "Удалить",
            "dirs.DirNotExists": "Не существует. Удаление...",
            "warn.exit.title": "Внимание",
            "warn.exit.lbWarn": "Внимание!",
            "warn.exit.lbText": "Задачи не завершены!",
            "warn.exit.btAccept": "Выйти",
            "warn.exit.btDeny": "Назад",
            "warn.cancel.title": "Внимание",
            "warn.cancel.lbWarn": "Вы уверены,",
            "warn.cancel.lbText": "Что хотите отменить задачу?",
            "warn.cancel.btAccept": "Да",
            "warn.cancel.btDeny": "Назад",
            "noti.title": "Ошибка",
            "noti.lbWarn": "Неверный диапазон портов!",
            "noti.lbText": "Допустимы значения от 10240 до 65025",
            "noti.lbText2": "Количество портов не менее 100",
            "checker.title": "Проверка необходимых модулей",
        },
    }

    def __init__(self):
        self.current_name = "english"
        self.current_index = 0

    # получение всех доступных языков
    def get_all(self) -> tuple:
        return tuple(self.data.keys())

    # установка языка по имени или индексу
    def set(self, name: str = None, index: int = None) -> None:

        if name and name in self.data:
            self.current_index = self.get_all().index(name)
            self.current_name = name

        elif isinstance(index, int) and 0 <= index < len(self.data):
            self.current_name = self.get_all()[index]
            self.current_index = index

    # получение текста по тегу
    def read(self, tag: str) -> Union[str, tuple]:
        try:
            return self.data[self.current_name][tag]
        except KeyError:  # если тег не найден
            return "-----"


class Theme:
    """Класс настроек ttk темы"""

    master: Tk
    style: ttk.Style
    data: tuple
    current_name: str
    current_index: int

    # вызывается после создания главного окна
    def lazy_init(self, master: Tk):
        self.master = master
        self.style = ttk.Style()
        self.data = self.style.theme_names()
        self.set()

    def set_name(self, name: str):
        self.current_name = name

    def get_all(self):
        return self.data

    def set(self, index: Optional[int] = None):
        if not hasattr(self, "master"):
            return

        if index == None:
            self.current_index = self.data.index(self.current_name)
        else:
            self.current_name = self.data[index]
            self.current_index = index

        self.style.theme_use(self.current_name)
        self.set_styles()

        _font = font.Font(size=12)
        self.style.configure(style=".", font=_font)  # шрифт текста в кнопке
        self.master.option_add("*Font", _font)  # шрифты остальных виджетов

    def set_styles(self):
        self.style.configure("Main.TaskList.TFrame", background=MAIN_TASKLIST_COLOR)
        self.style.configure("Main.ToolBar.TFrame", background=MAIN_TOOLBAR_COLOR)

        # создание стилей фона таскбара для разных состояний
        for status, color in MAIN_TASKBAR_COLORS.items():
            self.style.configure(f"{status}.Task.TFrame", background=color)
            self.style.configure(f"{status}.Task.TLabel", background=color)
            self.style.configure(
                f"{status}.Task.Horizontal.TProgressbar", background=color
            )

        self.style.map(
            "Create.Task.TButton",
            background=[("active", "blue"), ("!disabled", "blue")],
        )


class UtilityLocator:
    """Ищет утилиты в системе по имени"""

    use_system_path: bool

    ffmpeg_in_sys_path: bool
    catframes_in_sys_path: bool

    ffmpeg_full_path: str
    catframes_full_path: str

    def set_ffmpeg(self, is_in_sys_path: bool, full_path: str):
        self.ffmpeg_in_sys_path = is_in_sys_path
        self.ffmpeg_full_path = full_path

    def set_catframes(self, is_in_sys_path: bool, full_path: str):
        self.catframes_in_sys_path = is_in_sys_path
        self.catframes_full_path = full_path

    # метод для поиска ffmpeg в системе
    def find_ffmpeg(self) -> None:
        self.ffmpeg_in_sys_path = self.find_in_sys_path('ffmpeg')
        self.ffmpeg_full_path = self.find_full_path('ffmpeg', self.ffmpeg_in_sys_path)
        return self.ffmpeg_full_path

    # такой же, но для catframes
    def find_catframes(self) -> None:
        self.catframes_in_sys_path = self.find_in_sys_path('catframes')
        self.catframes_full_path = self.find_full_path('catframes', self.catframes_in_sys_path)
        return self.catframes_full_path

    # ищет полный путь для утилиты
    # если она есть в path, то ищет консолью
    @staticmethod
    def find_full_path(utility_name: str, is_in_sys_path: bool) -> Optional[str]:
        if is_in_sys_path:
            return UtilityLocator.find_by_console(utility_name)

        paths_to_check = UtilityLocator._get_paths(utility_name)
        for path in paths_to_check:
            if os.path.isfile(path):
                return path

    # ниходит полный путь утилиты при помощи консоли,
    # если она есть в системном path
    @staticmethod
    def find_by_console(utility_name) -> list:
        command = "where" if platform.system()== "Windows" else "which"
        result = subprocess.run(
            [command, utility_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        paths = result.stdout.decode()
        paths = map(lambda x: x.strip('\r '), paths.split('\n'))

        if platform.system() == "Windows":
            paths = filter(lambda x: x.endswith('.exe'), paths)

        paths = list(paths)
        return paths[0] if paths else None

    # возвращает пути, по которым может быть утилита, исходя из системы
    @staticmethod
    def _get_paths(utility_name: str) -> List[str]:
        system = platform.system()

        if system == "Windows":
            return [
                os.path.join(
                    os.environ.get("ProgramFiles", ""),
                    utility_name,
                    "bin",
                    f"{utility_name}.exe",
                ),
                os.path.join(
                    os.environ.get("ProgramFiles(x86)", ""),
                    utility_name,
                    "bin",
                    f"{utility_name}.exe",
                ),
            ]
        elif system == "Linux":
            return [
                "/usr/bin/" + utility_name,
                "/usr/local/bin/" + utility_name,
            ]
        elif system == "Darwin":
            return [
                "/usr/local/bin/" + utility_name,
                "/opt/homebrew/bin/" + utility_name,
            ]

    # проверка, есть ли утилита в системном path
    @staticmethod
    def find_in_sys_path(utility_name) -> bool:
        try:
            result = subprocess.run(
                [utility_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            output = ''
            for i in range(3):
                output += result.stderr.decode()
            if result.returncode == 0 or ("usage" in output):
                return True
        except FileNotFoundError:
            pass
        return False


class IniConfig:
    """Создание, чтение, и изменение внешнего файла конфига"""

    def __init__(self):
        self.file_path = os.path.join(os.path.expanduser("~"), CONFIG_FILENAME)
        self.file_exists = os.path.isfile(self.file_path)
        self.config = configparser.ConfigParser()

        if self.file_exists:
            self.config.read(self.file_path)
        else:
            self.set_default()

    # создание стандартного конфиг файла
    def set_default(self):
        self.config["Settings"] = {
            "Language": "english",
            "UseSystemPath": "yes",
            "TtkTheme": "vista" if platform.system() == "Windows" else "default",
        }
        self.config["AbsolutePath"] = {
            "FFmpeg": "",
            "Catframes": "",
        }
        self.config["SystemPath"] = {
            "FFmpeg": "",
            "Catframes": "",
        }

    # редактирование ключа в секции конфиг файла
    def update(self, section: str, key: str, value: Union[str, int]):
        if section in self.config:
            self.config[section][key] = value

    def save(self):
        with open(self.file_path, "w") as configfile:
            self.config.write(configfile)
        self.file_exists = True


class Settings:
    """Содержит объекты всех классов настроек"""

    lang = Lang()
    theme = Theme()
    util_locatior = UtilityLocator()
    conf = IniConfig()

    @classmethod
    def save(cls):
        cls.conf.update("Settings", "Language", cls.lang.current_name)
        cls.conf.update("Settings", "TtkTheme", cls.theme.current_name)
        cls.conf.save()

    @classmethod
    def restore(cls):
        cls.lang.set(cls.conf.config["Settings"]["Language"])
        cls.theme.set_name(cls.conf.config["Settings"]["TtkTheme"])
        cls.util_locatior.set_ffmpeg(
            is_in_sys_path=cls.conf.config["SystemPath"]["FFmpeg"]=='yes',
            full_path=cls.conf.config["AbsolutePath"]["FFmpeg"]
        )
        cls.util_locatior.set_catframes(
            is_in_sys_path=cls.conf.config["SystemPath"]["Catframes"]=='yes',
            full_path=cls.conf.config["AbsolutePath"]["Catframes"]
        )





    #  из файла task_flows.py:

"""
Слой задач полностью отделён от gui.

Задачи создаются с помощью TaskManager, который
выдаёт им уникальные номера, и регистрирует их статусы.

При создании задачи, ей передаюётся нужная конфигурация,
которая представляет собой объект класса TaskConfig.
Атрибутами этого объекта являются все возможные параметры,
которые есть у консольной версии приложения catframes.
Этот объект имеет метод конвертирования в консольную команду,
которая и будет запущена самим процессом задачи при старте.

Чтобы в процессе обработки, задача могла как-то делиться
своим статусом с интерфейсом, реализован паттерн "наблюдатель".
При старте задачи, ей передаётся объект класса GuiCallback.
При инициализации, объект коллбэка принимает внешние зависимости,
чтобы у задачи была возможность обновлять свои статусы в gui.
"""


class TaskConfig:
    """Настройка и хранение конфигурации задачи.
    Создаётся и настраивается на слое gui.
    Позволяет конвертировать в команду catframes."""

    overlays_names = [
        "--top-left",
        "--top",
        "--top-right",
        "--right",
        "--bottom-right",
        "--bottom",
        "--bottom-left",
        "--left",
    ]

    quality_names = ("high", "medium", "poor")

    def __init__(self) -> None:

        self._dirs: List[str] = []
        self._overlays: Dict[str, str] = {}
        self._color: str = DEFAULT_CANVAS_COLOR
        self._framerate: int = 30
        self._quality: str = "medium"
        self._quality_index: int = 1
        self._limit: Optional[int] = None
        self._filepath: str = ""
        self._rewrite: bool = False

    def set_dirs(self, dirs: List[str]) -> list:
        self._dirs = dirs

    def set_overlays(self, overlays_texts: List[str]):
        self._overlays = dict(zip(self.overlays_names, overlays_texts))

    def set_color(self, color: str):
        self._color = color

    def set_preview_params(self, limit: int, path: str):
        self._limit = limit
        self._filepath = path

    # установка частоты кадров, качества и лимита
    def set_specs(self, framerate: int, quality: int, limit: int = None):
        self._framerate = framerate
        self._quality_index = quality
        self._quality = self.quality_names[quality]
        self._limit = limit

    def set_filepath(self, filepath: str):
        self._filepath = filepath

    def get_filepath(self) -> str:
        return self._filepath

    def get_dirs(self) -> list:
        return self._dirs[:]

    def get_quality(self) -> int:
        return self._quality_index

    def get_framerate(self) -> int:
        return self._framerate

    def get_overlays(self) -> List[str]:
        return list(self._overlays.values())

    def get_color(self) -> str:
        return self._color

    @staticmethod
    def to_user_format(text: str, bash: bool) -> str:
        text = text.replace("\n", "\\n")
        text = text.replace("\r", "\\r")
        text = text.replace("\t", "\\t")
        return TaskConfig.wrap_quots(text, bash)
    
    @staticmethod
    def wrap_quots(text: str, bash: bool) -> str:
        q = "'" if bash else '"'
        return q + text + q

    # создание консольной команды в виде списка
    def convert_to_command(
        self, for_user: bool = False, bash: bool = True
    ) -> List[str]:
        command = ["catframes"]

        for position, text in self._overlays.items():
            if text:
                if for_user:
                    text = self.to_user_format(text, bash)
                    command.append(f"{position}={text}")
                else:
                    command.append(position)
                    command.append(text)

        color = self._color
        if for_user:
            color = self.wrap_quots(color, bash)
        command.append(f"--margin-color={color}")
        command.append(f"--frame-rate={self._framerate}")
        command.append(f"--quality={self._quality}")

        if os.path.isfile(self._filepath):  # флаг перезаписи, если файл уже есть
            command.append("--force")

        for dir in self._dirs:  # добавление директорий с изображениями
            if for_user:
                dir = self.to_user_format(dir, bash)
            command.append(dir)

        if for_user:
            # добавление полного пути файла в кавычках
            command.append(self.to_user_format(self._filepath, bash))  
        else:
            command.append(self._filepath)
            command.append("--live-preview")

        if self._limit:
            command.append(f"--limit={self._limit}")

        return command


class GuiCallback:
    """Интерфейс для инъекции внешних методов от gui.
    Позволяет из задачи обновлять статус на слое gui."""

    def __init__(
        self,
        update_function,
        finish_function,
        error_function,
        delete_function,
    ):
        self.update = update_function
        self.finish = finish_function
        self.set_error = error_function
        self.delete = delete_function

    @staticmethod  # метод из TaskBar
    def update(progress: float, base64_img: str = ""):
        """обновление полосы прогресса и превью в окне"""
        ...

    @staticmethod  # метод из RootWindow
    def finish(id: int):
        """сигнал о завершении задачи"""
        ...

    @staticmethod
    def set_error(id: int, error: str):
        """сигнал об ошибке в выполнении"""
        ...

    @staticmethod  # метод из RootWindow
    def delete(id: int):
        """сигнал об удалении задачи"""
        ...


class CatframesProcess:
    """Создаёт подпроцесс с запущенным catframes,
    создаёт отдельный поток для чтения порта api,
    чтобы не задерживать обработку gui программы.
    По запросу может сообщать данные о прогрессе.
    """

    def __init__(self, command):
        if sys.platform == "win32":
            # Обработка сигналов завершения в Windows выглядит как большой беспорядок.
            # Если убрать этот флаг, CTRL+C будет отправляться как в дочерний, так и в родительский процесс.
            # Если использовать этот флаг, CTRL+C не работает вообще, зато работает CTRL+Break.
            # Этот флаг обязателен к использованию также и согласно документации Python, если мы хотим
            # отправлять в подпроцесс эти два сигнала:
            # https://docs.python.org/3/library/subprocess.html#subprocess.Popen.send_signal
            os_issues = {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP}
        else:
            os_issues = {}

        self.process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, **os_issues
        )

        self.error: Optional[str] = None
        self._progress = 0.0
        self._image_base64 = ""
        threading.Thread(
            target=self._update_progress, daemon=True
        ).start()  # запуск потока обновления прогресса из вывода stdout

    def _update_progress(self):  # обновление прогресса, чтением вывода stdout
        progress_pattern = re.compile(r"Progress: +[0-9]+")
        image_base64_pattern = re.compile(r"Preview: [a-zA-Z0-9+=/]+")

        # читает строки вывода процесса
        for line in io.TextIOWrapper(self.process.stdout):
            if "FFmpeg not found" in line:
                self.error = NO_FFMPEG_ERROR

            # ищет в строке процент прогресса
            progress_data = re.search(progress_pattern, line)

            if progress_data:
                # если находит, забирает число
                progress_percent = int(progress_data.group().split()[1])

                # если процент 100 - предерживает его
                if self._progress != 100:
                    self._progress = progress_percent / 100

            image_data = re.search(image_base64_pattern, line)
            if image_data:
                self._image_base64 = image_data.group().split()[1]


        ret_code = self.process.poll()
        while None == ret_code:
            ret_code = self.process.poll()

        # если процесс завершился некорректно
        if ret_code != 0 and not self.error:
            self.error = INTERNAL_ERROR  # текст последней строки

        self._progress == 1.0

    def get_progress(self):
        return self._progress

    def get_image_base64(self):
        return self._image_base64

    # убивает процесс (для экстренной остановки)
    def kill(self):
        if sys.platform == "win32":
            # CTRL_C_EVENT is ignored for process groups
            # https://learn.microsoft.com/ru-ru/windows/win32/procthread/process-creation-flags
            os.kill(self.process.pid, signal.CTRL_BREAK_EVENT)
        else:
            os.kill(self.process.pid, signal.SIGTERM)

        # Раз уж удаление делается не через callback или Promise, нужно сделать это синхронно.
        # Мы не можем полагаться на удачу. Мы должны всегда получить одинаковое поведение
        # (удаление видео в случае отмены).
        while None == self.process.poll():
            time.sleep(0.1)


class Task:
    """Класс самой задачи, связывающейся с catframes"""

    def __init__(self, id: int, task_config: TaskConfig) -> None:
        self.config: TaskConfig = task_config
        self.command: list = task_config.convert_to_command()

        self._process_thread: CatframesProcess = None
        self.id: int = id

        self.done: bool = False  # флаг завершённости
        self.stop_flag: bool = False  # требование остановки

    # запуск задачи
    def start(self, gui_callback: GuiCallback):  # инъекция колбека
        self.gui_callback = gui_callback
        TaskManager.reg_start(self)

        try:  # запуск фонового процесса catframes
            self._process_thread = CatframesProcess(self.command)

        except FileNotFoundError:  # если catframes не найден
            return self.handle_error(NO_CATFRAMES_ERROR)

        except Exception as e:  # если возникла другая ошибка, обработает её
            return self.handle_error(START_FAILED_ERROR)

        # запуск потока слежения за прогрессом
        threading.Thread(target=self._progress_watcher, daemon=True).start()

    # спрашивает о прогрессе, обновляет прогрессбар, обрабатывает завершение
    def _progress_watcher(self):
        progress: float = 0.0

        while progress < 1.0 and not self.stop_flag:  # пока прогрес не завершён
            time.sleep(0.2)
            progress = self._process_thread.get_progress()
            image = self._process_thread.get_image_base64()

            self.gui_callback.update(progress, base64_img=image)

            if self._process_thread.error and not self.stop_flag:
                return self.handle_error(self._process_thread.error)

        self.finish()

    # обработка ошибки процесса
    def handle_error(self, error: str):
        TaskManager.reg_finish(self)
        self.gui_callback.set_error(self.id, error=error)

    # обработка финиша задачи
    def finish(self):
        self.done = True
        TaskManager.reg_finish(self)
        self.gui_callback.finish(self.id)

    # остановка задачи
    def cancel(self):
        self.stop_flag = True
        TaskManager.reg_finish(self)
        self._process_thread.kill()
        self.delete_file()
        self.gui_callback.delete(self.id)

    # удаляет файл в системе
    def delete_file(self):
        file = self.config.get_filepath()
        try:
            os.remove(file)
        except:
            # Just in case someone opened the video in a player
            # while it was being encoded or something.
            pass

    def delete(self):
        TaskManager.wipe(self)
        self.gui_callback.delete(self.id)


class TaskManager:
    """Менеджер задач.
    Позволяет регистрировать задачи,
    и управлять ими."""

    _last_id: int = 0  # последний номер задачи
    _all_tasks: dict = {}  # словарь всех задач
    _running_tasks: dict = {}  # словарь активных задач

    # фабричный метод, создания задачи с уникальным id
    @classmethod
    def create(cls, task_config: TaskConfig) -> Task:
        cls._last_id += 1
        unic_id = cls._last_id

        task = Task(unic_id, task_config)
        cls._reg(task)
        return task

    # регистрация задачи
    @classmethod
    def _reg(cls, task: Task) -> None:
        cls._all_tasks[task.id] = task

    # регистрация запуска задачи
    @classmethod
    def reg_start(cls, task: Task) -> None:
        cls._running_tasks[task.id] = task

    # удаление регистрации запуска задачи
    @classmethod
    def reg_finish(cls, task: Task) -> None:
        if task.id in cls._running_tasks:
            cls._running_tasks.pop(task.id)

    # получение списка активных задач
    @classmethod
    def running_list(cls) -> list:
        return list(cls._running_tasks.values())

    # удаление задачи
    @classmethod
    def wipe(cls, task: Task) -> None:
        cls.reg_finish(task)
        if task.id in cls._all_tasks:
            cls._all_tasks.pop(task.id)

    # получение списка всех задач
    @classmethod
    def all_list(cls) -> list:
        return list(cls._all_tasks.values())

    # проверка существования задачи
    @classmethod
    def check(cls, task_id: int) -> bool:
        return task_id in cls._all_tasks





    #  из файла windows_base.py:

"""
Управление окнами происходит локальным менеджером окон.

Любое открытие окна происходит именно через него.
если окно уже прописано в его локальном словаре, 
оно не будет открыто повторно, будет возвращён его объект.

Если где угодно в коде нужно открыть/закрыть/сфокусировать
любое другое окно, через LocalWM можно получить его объект.
Также, можно получить список всех окон, например, для итерации.

WindowMixin - это абстрактный класс, от которого наследуются
все классы окон. В нём прописана базовая логика поведения окна.
Также, в нём есть инициализация стилей окна, и должны быть методы,
касающиеся пользовательских настроек, чтобы итерацией по всем окнам,
и вызове метода обновления для каждого окна, они применились везде.
К примеру, метод "update_texts" обновляет текст на всех виджетах окна.
"""


class LocalWM:
    """Класс для работы с окнами.
    Позволяет регистрировать окна,
    И управлять ими."""

    _all_windows: dict = {}  # общий словарь регистрации для окон

    # проверка, зарегистрировано ли окно
    @classmethod
    def check(cls, name: str) -> bool:
        return name in cls._all_windows

    # открытие окна
    @classmethod  # принимает класс окна, имя окна
    def open(cls, window_cls, name: str, master: Optional[Tk] = None, **kwargs) -> Tk:

        # если корневого окна нет, то создаём и регистрируем
        if not cls.check("root"):
            return cls._reg(window_cls(), "root")

        if not master:
            master = cls.call("root")

        # если окно не зарегистрировано - создаёт его и регистрирует
        if not cls.check(name):
            window = window_cls(root=master, **kwargs)
            cls._reg(window, name)

        return cls.call(name)

    # регистрация окна
    @classmethod
    def _reg(cls, window: Tk, name: str = None) -> None:
        if not name:
            name = window.name
        if not cls.check(name):
            cls._all_windows[name] = window
        return window

    # получение окна
    @classmethod
    def call(cls, name: str) -> Optional[Tk]:
        if cls.check(name):
            return cls._all_windows[name]

    # удаление окна
    @classmethod
    def wipe(cls, name: str) -> None:
        if cls.check(name):
            cls._all_windows.pop(name)

    # получение списка всех окон
    @classmethod
    def all(cls) -> list:
        return list(cls._all_windows.values())

    # переключение фокуса на окно
    @classmethod
    def focus(cls, name: str) -> None:
        if cls.check(name):
            cls._all_windows[name].focus()

    # обновление открытых окон после завершения задачи
    @classmethod
    def update_on_task_finish(cls):
        if cls.check("warn") and not TaskManager.running_list():
            cls._all_windows["warn"].destroy()
            cls._all_windows.pop("warn")


class WindowMixin(ABC):
    """Абстрактный класс.
    Упрощает конструкторы окон."""

    title: Tk.wm_title  # эти атрибуты и методы объекта
    protocol: Tk.wm_protocol  # появятся автоматически при
    destroy: Tk.destroy  # наследовании от Tk или Toplevel

    size: Tuple[int, int]  # размеры (ширина, высота) окна
    name: str  # имя окна для словаря всех окон
    widgets: Dict[str, ttk.Widget]  # словарь виджетов окна

    # стандартная настройка окна, вызывается в конце конструктора
    def _default_set_up(self):
        self.protocol("WM_DELETE_WINDOW", self.close)  # что выполнять при закрытии

        if platform.system() == "Linux":
            self._set_linux_sizes()
        self._set_size()
        self._to_center()

        if self.name in ("root", "checker"):
            Settings.theme.lazy_init(master=self)
        self.after(1, self._init_widgets)
        self.after(2, self.update_texts)
        self.after(3, self._pack_widgets)

    # закрытие окна
    def close(self) -> None:
        LocalWM.wipe(self.name)
        self.destroy()

    # обновление текстов всех виджетов окна, исходя из языка
    def update_texts(self) -> None:
        self.title(Settings.lang.read(f"{self.name}.title"))

        for w_name, widget in self.widgets.items():

            # не применяется для виджетов, начинающихся с "_"
            if w_name.startswith("_"):
                continue

            new_text_data = Settings.lang.read(f"{self.name}.{w_name}")

            if w_name.startswith("cmb"):  # если виджет это комбобокс
                widget.config(values=new_text_data)
                widget.current(newindex=0)
                continue

            widget.config(text=new_text_data)

    # размещение окна в центре экрана (или родительского окна)
    def _to_center(self) -> None:

        screen_size: tuple = self.winfo_screenwidth(), self.winfo_screenheight()

        # если это не побочное окно, то размещаем по центру экрана
        if not isinstance(self, Toplevel):
            x = (screen_size[0] - self.size[0]) / 2
            y = (screen_size[1] - self.size[1]) / 2
            self.geometry(f"+{int(x)}+{int(y)}")
            return

        # далее для побочных окон:
        master_size = self.master.winfo_width(), self.master.winfo_height()
        master_coords = self.master.winfo_x(), self.master.winfo_y()

        x, y = self._calculate_coords(master_coords, master_size, self.size, screen_size)

        self.geometry(f"+{int(x)}+{int(y)}")

    @staticmethod
    def _calculate_coords(master_coords, master_size, window_size, screen_size) -> Tuple[int]:
        
        border_gap: int = 30  # минимальный отступ от края окна при открытии

        x = master_coords[0] + master_size[0] / 2 - window_size[0] / 2
        y = master_coords[1] + master_size[1] / 2 - window_size[1] / 2

        # далее описаны сценарии для случаев, когда новое окно,
        # при появлении, выходит за границы экрана

        if x < border_gap:
            x = border_gap

        if x + window_size[0] + border_gap > screen_size[0]:
            x = screen_size[0] - window_size[0] - border_gap

        if y < border_gap:
            y = border_gap

        # при выходе за нижнюю границу экрана, отсуп больше
        if y + window_size[1] + (border_gap * 3) > screen_size[1]:
            y = screen_size[1] - window_size[1] - (border_gap * 3)

        return int(x), int(y)
    
    def _set_linux_sizes(self):
        x, y = self.size
        self.size = int(x*LINUX_SIZING), int(y*LINUX_SIZING)

        if hasattr(self, "size_max"):
            x, y = self.size_max
            self.size_max = int(x*LINUX_SIZING), int(y*LINUX_SIZING)
            

    def _set_size(self):

        x, y = self.size
        self.geometry(f"{x}x{y}")
        self.minsize(x, y)

        if hasattr(self, "size_max"):
            self.maxsize(*self.size_max)

    # метод для создания и настройки виджетов
    @abstractmethod
    def _init_widgets(self) -> None: ...

    # метод для расположения виджетов
    @abstractmethod
    def _pack_widgets(self) -> None: ...





    #  из файла windows_utils.py:

"""
Прокручиваемый фрейм это сложная структура, основанная на
объекте "холста", к которому крепятся полоса прокрутки и фрейм.
Далее следует большое количество взаимных подвязок, на разные случаи.

- если фрейм переполнен:
    ^ любые прокрутки невозможны

- полоса может прокручивать объект холста,
- при наведении мыши на холст, привязка возможностей:
    ^ колесо мыши может прокручивать холст и полосу прокрутки

Объект бара задачи это фрейм, в котором разные виджеты, относящиеся 
к описанию параметров задачи (картинка, лейблы для пути и параметров),
бар прогресса выполнения задачи, и кнопку отмены/удаления.
"""


# возвращает список всех изображений в директории
def find_img_in_dir(dir: str, full_path: bool = False) -> List[str]:
    img_list = [f for f in os.listdir(dir) if f.endswith((".png", ".jpg"))]
    if full_path:
        img_list = list(
            map(lambda x: f"{dir}/{x}", img_list)
        )  # добавляет путь к названию
    return img_list


# переводчит base64 картинку в tk
def base64_to_tk(image_base64: str) -> ImageTk.PhotoImage:
    image_data = base64.b64decode(image_base64)
    image = Image.open(io.BytesIO(image_data))
    return ImageTk.PhotoImage(image)


# сокращает строку пути, расставляя многоточия внутри
def shrink_path(path: str, limit: int) -> str:
    if len(path) < limit:
        return path

    # вычисление разделителя, добавление вначало, если нужно
    s = "/" if "/" in path else "\\"
    dirs = path.split(s)
    if path.startswith(s):
        dirs.pop(0)
        dirs[0] = s + dirs[0]

    # список укороченного пути, первый и последний элементы
    shrink = [dirs.pop(0), dirs.pop()]
    while dirs and len(s.join(shrink) + dirs[-1]) + 4 < limit:
        shrink.insert(1, dirs.pop())  # добавить элемент с конца

    try:
        # вычисляет разницу символов от нужной длины,
        # добавит кусочек имени последней невлезшей директории
        addit = limit - len(f"{shrink[0]}{s}...{s}{s.join(shrink[1:])}")
        start = len(dirs[-1]) - addit
        shrink.insert(1, dirs[-1][start::])
    except:
        pass

    # сборка строки нового пути, передача её, если она короче изначальной
    new_path = f"{shrink[0]}{s}...{s.join(shrink[1:])}"
    return new_path if len(new_path) < len(path) else path


class GlobalStates:
    last_dir = "~"


class ScrollableFrame(ttk.Frame):
    """Прокручиваемый (умный) фрейм"""

    def __init__(self, root_window: Tk, *args, **kwargs):
        super().__init__(root_window, *args, **kwargs, style="Main.TFrame")

        self.root: Tk = root_window
        self.canvas = Canvas(self, highlightthickness=0)

        # если это не macos, добавить холсту цвет
        if not platform.system() == "Darwin":
            self.canvas.config(bg=MAIN_TASKLIST_COLOR)

        # привязываем обработку изменений холста
        self.canvas.bind("<Configure>", self._on_resize_window)

        self.scrollbar = ttk.Scrollbar(
            self,
            orient="vertical",
            command=self.canvas.yview,
        )
        self.scrollable_frame = ttk.Frame(  # фрейм для контента (внутренних виджетов)
            self.canvas, padding=[15, 0], style="Main.TaskList.TFrame"
        )

        # привязка обработки изменений фрейма
        self.scrollable_frame.bind("<Configure>", self._on_frame_update)

        # привязка холста к верхнему левому углу, получение id фрейма
        self.frame_id = self.canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw"
        )
        # передача управления полосы прокрутки, когда холст движется от колёсика
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # упаковка виджетов
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        # привязка и отвязка событий, когда курсор заходит на холст
        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)

        # первичное обновление полосы, чтобы сразу её не было видно
        self._update_scrollbar_visibility()

    # отрабатываывает при добавлении/удалении таскбаров в фрейм
    def _on_frame_update(self, event):
        self._update_scrollbar(event)

    # изменение размеров фрейма внутри холста
    def _on_resize_window(self, event):
        if event.width > 500:  # фильтруем нужные события
            self.canvas.itemconfig(self.frame_id, width=event.width)

    # обработка изменений полосы прокрутки
    def _update_scrollbar(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self._update_scrollbar_visibility()

    # проверяет, нужна ли полоса прокрутки, и показывает/скрывает её
    def _update_scrollbar_visibility(self):
        if self.scrollable_frame.winfo_height() > self.canvas.winfo_height():
            self.scrollbar.pack(side="right", fill="y")
        else:
            self.scrollbar.pack_forget()

    # попытка активировать прокрутку колёсиком (если пройдёт валидацию)
    def _bind_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._validate_mousewheel)

    # отвазать события прокрутки
    def _unbind_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")

    # возможность прокрутки только если полоса активна, и фрейм переполнен
    def _validate_mousewheel(self, event):
        if self.scrollable_frame.winfo_height() > self.canvas.winfo_height():
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


class TaskBar(ttk.Frame):
    """Класс баров задач в основном окне"""

    def __init__(self, master: ttk.Frame, task: Task, cancel_def: Callable, **kwargs):
        super().__init__(master, borderwidth=1, padding=5, style="Scroll.Task.TFrame")
        self.name = "bar"
        self.widgets: Dict[str, Widget] = {}
        self.task: Task = task
        self.cancel_def = cancel_def
        self.progress: float = 0
        self.image: Image
        self.length: int = 520
        self.error: str = None

        # достаёт ручку для открытия окна просмотра
        self.open_view: Callable = kwargs.get("view")

        self._init_widgets()
        self.update_texts()
        self._pack_widgets()
        self._update_labels()

    # установка стиля для прогрессбара
    def _set_style(self, style_id: int):
        styles = ["Running", "Success", "Error"]
        style = styles[style_id]

        for elem in (self, self.left_frame, self.mid_frame, self.right_frame):
            elem.config(style=f"{style}.Task.TFrame")
        self.widgets["_lbData"].config(style=f"{style}.Task.TLabel")
        self.widgets["_lbPath"].config(style=f"{style}.Task.TLabel")
        self.widgets["_progressBar"].config(
            style=f"{style}.Task.Horizontal.TProgressbar"
        )

    # создание и настройка виджетов
    def _init_widgets(self):
        self.left_frame = ttk.Frame(self, padding=5)

        # берёт первую картинку из первой директории
        img_dir = self.task.config.get_dirs()[0]
        img_path = find_img_in_dir(img_dir, full_path=True)[0]

        image = Image.open(img_path)
        image_size = (80, 60)
        image = image.resize(image_size, Image.ADAPTIVE)
        self.image_tk = ImageTk.PhotoImage(image)

        self.widgets["_picture"] = ttk.Label(self.left_frame, image=self.image_tk)

        # создании средней части бара
        self.mid_frame = ttk.Frame(self, padding=5)

        bigger_font = font.Font(size=16)

        # надпись в баре
        self.widgets["_lbPath"] = ttk.Label(
            self.mid_frame,
            font=bigger_font,
            padding=5,
            text=shrink_path(self.task.config.get_filepath(), 30),
        )

        self.widgets["_lbData"] = ttk.Label(
            self.mid_frame,
            font="14",
            padding=5,
        )

        # создание правой части бара
        self.right_frame = ttk.Frame(self, padding=5)

        # кнопка "отмена"
        self.widgets["btCancel"] = ttk.Button(
            self.right_frame, width=10, command=self.cancel_def
        )

        # полоса прогресса
        self.widgets["_progressBar"] = ttk.Progressbar(
            self.right_frame,
            # length=320,
            maximum=1,
            value=0,
        )

        self._set_style(0)

        # при растягивании фрейма
        def on_resize(event):
            self.length = event.width  # максимальная длина имени директории

            self._update_labels()

        self.bind("<Configure>", on_resize)

        # открытие окна просмотра задачи
        def open_view(event):
            self.open_view(task_config=self.task.config)

        # привязка ко всем элементам таскбара, кроме кнопок
        self.bind("<Button-1>", open_view)
        for w_name, w in self.widgets.items():
            if not "bt" in w_name:  #
                w.bind("<Button-1>", open_view)

    # обновление лейблов пути и информации на виджете
    def _update_labels(self):

        # вычисляем символьную длинну для лейбла пути,
        # ужимаем путь, присваиваем текст
        lb_path_length = int(self.length // 10) - 23
        lb_path_text = shrink_path(self.task.config.get_filepath(), lb_path_length)
        self.widgets["_lbPath"].configure(text=lb_path_text)

        # если есть ошибка, то лейбл информации заполняем текстом этой ошибки
        if self.error:
            text = Settings.lang.read(f"bar.error.{self.error}")
            self.widgets["_lbData"].configure(text=text)
            return

        # создаём локализованую строку "качество: высокое | частота кадров: 50"
        lb_data_list = []

        quality = Settings.lang.read("task.cmbQuality")[self.task.config.get_quality()]
        quality_text = f"{Settings.lang.read('bar.lbQuality')} {quality}"
        lb_data_list.append(quality_text)

        framerate_text = f"{Settings.lang.read('bar.lbFramerate')} {self.task.config.get_framerate()}"
        lb_data_list.append(framerate_text)

        # и если ширина фрейма больше 600, то и информацию про цвет
        if self.length > 600:
            color_text = (
                f"{Settings.lang.read('bar.lbColor')} {self.task.config.get_color()}"
            )
            lb_data_list.append(color_text)

        # присваиваем строку информации через резделитель ' | '
        self.widgets["_lbData"].configure(text=" | ".join(lb_data_list))

    # упаковка всех виджетов бара
    def _pack_widgets(self):
        self.widgets["_picture"].pack(side=LEFT)
        self.left_frame.pack(side=LEFT)

        self.widgets["_lbPath"].pack(side=TOP, fill=X, expand=True)
        self.widgets["_lbData"].pack(side=TOP, fill=X, expand=True)
        self.mid_frame.pack(side=LEFT, fill=X, expand=True)

        self.widgets["_progressBar"].pack(side=TOP, expand=True, fill=X)
        self.widgets["btCancel"].pack(side=BOTTOM, expand=True, fill=X)
        self.right_frame.pack(side=LEFT)

        self.pack(pady=[10, 0], fill=X, expand=True)

    # изменение бара на "завершённое" состояние
    def finish(self):
        # в словаре виджетов ключ кнопки переименовывается,
        # и меняется поведение кнопки переопределяется

        self._set_style(1)
        self.widgets["btDelete"] = self.widgets.pop("btCancel")
        self.widgets["btDelete"].config(command=lambda: self.task.delete())
        self.update_texts()

    # изменение бара на состояние "ошибки"
    def set_error(self, error: str):

        self._set_style(2)
        self.widgets["btDelete"] = self.widgets.pop("btCancel")
        self.widgets["btDelete"].config(command=lambda: self.task.delete())
        self.error = error
        self.update_texts()

    # обновление линии прогресса
    def update_progress(self, progress: float, base64_img: str = ""):
        self.progress = progress
        try:
            self.widgets["_progressBar"].config(value=self.progress)
        except:
            pass

        if base64_img:
            try:
                image_tk = base64_to_tk(base64_img)  # и заменить на баре
                self.widgets["_picture"].config(image=image_tk)
                self.image_tk = image_tk
            except:
                pass

    # удаление бара
    def delete(self):
        self.destroy()

    # обновление текстов виджетов
    def update_texts(self):
        for w_name, widget in self.widgets.items():
            if not w_name.startswith("_"):
                widget.config(text=Settings.lang.read(f"{self.name}.{w_name}"))
        self._update_labels()


class ResizingField(Text):
    """Поле, переводящее курсор по нажатию Enter,
    и изменяющее свой размер по количеству строк"""

    def __init__(self, master: Canvas, horizontal_pos: str, vertical_pos: str):
        super().__init__(
            master,
            width=10,
            font=("Arial", 14),
            wrap=NONE,
            undo=True,
            highlightthickness=2,
        )
        self.default_width: int = 10
        self.extra_width: int = 0
        self.num_lines: int = 0

        self.vertical_pos: str = vertical_pos
        self.horizontal_pos: str = horizontal_pos

        # смещения от начальных координат
        self.vertical_shift: int = 0
        self.horisontal_shift: int = 0

        self.id_on_canvas: Optional[int] = None
        self.default_coords: Optional[list] = None

        self.bind("<Escape>", self._on_escape)
        self.bind("<<Modified>>", self._on_text_change)

        # начальная высота 1 строка и перенос по словам
        self.configure(height=1, wrap="word")

    # получение всего текста в поле
    def get_text(self) -> str:
        try:
            return self.get("1.0", "end-1c").strip("\n ")
        except:
            return ""

    # установка текста в поле
    def set_text(self, text):
        self.delete("1.0", END)
        self.insert(END, text)

    # получение id себя на холсте
    def bind_self_id(self, id):
        self.id_on_canvas = id
        x, y = self.master.coords(id)
        self.default_coords = x, y - self.vertical_shift
        self._update_height()

    # фокусировка на объект холста, чтобы убрать это поле ввода
    def _on_escape(self, event):
        self.master.focus_set()

    def _on_text_change(self, event):
        self._update_width()
        self._update_height()
        self._update_coords()
        self.master.overlays.update()

        # сбрасываем статус изменения текста,
        # чтобы событие могло срабатывать повторно
        self.edit_modified(False)

    # обновление ширины, исходя из самой длинной строки
    def _update_width(self):
        lines = self.get_text().split("\n")
        longest = len(max(lines, key=lambda i: len(i)))

        self.extra_width = 0
        if longest >= self.default_width:
            self.extra_width = longest + 2 - self.default_width

        # рассчитывает модуль горизонтального смещения,
        # и устанавливает смещение в нужную сторону
        y_shift_abs = self.extra_width * 5
        if self.horizontal_pos == RIGHT:
            self.horisontal_shift = -y_shift_abs
        if self.horizontal_pos == LEFT:
            self.horisontal_shift = y_shift_abs

    # обновление высоты, исходя из количества строк
    def _update_height(self):
        self.num_lines = int(self.index("end-1c").split(".")[0])

        # рассчитывает модуль вертикального смещения,
        # и устанавливает смещение в нужную сторону
        x_shift_abs = (self.num_lines - 1) * 11
        if self.vertical_pos == BOTTOM:
            self.vertical_shift = -x_shift_abs
        if self.vertical_pos == TOP:
            self.vertical_shift = x_shift_abs

    # движение по вертикали при изменении количества строк
    def _update_coords(self):
        # если поле ввода ещё не размещено
        if not self.default_coords:
            return

        self.master.coords(
            self.id_on_canvas,
            self.default_coords[0] + self.horisontal_shift,
            self.default_coords[1] + self.vertical_shift,
        )
        self.config(width=self.default_width + self.extra_width, height=self.num_lines)


class Overlay:
    """Единичный оверлей на холсте, как сущность из
    прозрачного квадрата, лейбла, и поля ввода."""

    def __init__(
        self, master: Canvas, text: str, horizontal_pos: str, vertical_pos: str
    ):

        self.master = master
        self.view_mode: bool = master.view_mode
        self.horizontal_pos: str = horizontal_pos

        self.empty: bool = bool(text)

        # настройи прозрачного квадрата
        self.sq_size: int = 20
        sq_color = "#ffffff"
        sq_alpha = 0 if self.view_mode else 0.5

        # создание и добавление прозрачного квадрата
        self.alpha_square: PhotoImage = self._create_alpha_square(
            self.sq_size, sq_color, sq_alpha
        )
        self.square_id: int = self.master.create_image(
            0, 0, image=self.alpha_square, anchor="nw"
        )

        # добавление текста
        self.label_id: int = self.master.create_text(
            0, 0, text=text, font=("Arial", 24), justify=horizontal_pos
        )
        self.vertical_shift: int = 0
        self.horizontal_shift: int = 0

        # инициализация поля ввода
        self.entry: ResizingField = ResizingField(
            self.master, horizontal_pos, vertical_pos
        )
        self.entry_id: int = self.master.create_window(
            0, 0, window=self.entry, state="hidden", anchor=CENTER
        )
        self.entry.bind_self_id(self.entry_id)
        self.entry.set_text(text)

        # привязка события скрытия и показа поля ввода
        if not self.view_mode:
            self.master.tag_bind(self.label_id, "<Button-1>", self._show_entry)
            self.entry.bind("<FocusOut>", self._hide_entry)

    # обновление смещений текста
    def _update_shifts(self):
        self.vertical_shift = self.entry.vertical_shift

        # центральным полям смещение не нужно
        if self.horizontal_pos == CENTER:
            self.horizontal_shift = 0
            return

        # узнаём ширину лейбла на холсте
        bbox = self.master.bbox(self.label_id)
        text_object_width = bbox[2] - bbox[0]

        # при наличии текста, вычисляем смещение
        if self.entry.get_text():
            shift_abs = text_object_width // 2
            shift_abs -= self.sq_size / 2
            shift_abs -= self.master.width // 20
        else:
            shift_abs = 0

        # устанавливает смещение в нужную сторону
        if self.horizontal_pos == RIGHT:
            self.horizontal_shift = shift_abs
        if self.horizontal_pos == LEFT:
            self.horizontal_shift = -shift_abs

    # обновляет текст лейбла и видимость квадрата
    def update_label(self):
        text = "+"  # дефолтные значения, когда поле ввода пустое
        font = ("Arial", 24)
        square_state = "normal"
        label_color = "black"

        # при наличии текста в поле ввода, разместит его в лейбле,
        # проверит цвет фона, и выберет контрастный цвет, скроет квадрат
        if self.entry.get_text() or self.view_mode:
            text = self.entry.get_text()
            font = ("Arial", 16)
            square_state = "hidden"

            dark_background = self.master.is_dark_background(self.label_id)
            label_color = "white" if dark_background else "black"

        try:
            self.master.itemconfig(
                self.label_id, text=text, font=font, fill=label_color
            )
            self.master.itemconfig(self.square_id, state=square_state)
        except TclError:
            pass

    def get_text(self) -> str:
        return self.entry.get_text()

    # установка кординат для квадрата и лейбла
    def set_coords(self, coords: Tuple[int]):
        self._update_shifts()
        self.master.coords(
            self.square_id, coords[0] - self.sq_size / 2, coords[1] - self.sq_size / 2
        )
        self.master.coords(
            self.label_id,
            coords[0] - self.horizontal_shift,
            coords[1] + self.vertical_shift,
        )

    # создаёт картинку прозрачного квадрата
    def _create_alpha_square(self, size: int, fill: str, alpha: float):
        alpha = int(alpha * 255)
        fill = self.master.winfo_rgb(fill) + (alpha,)
        image = Image.new("RGBA", (size, size), fill)
        return ImageTk.PhotoImage(image)

    # отображает поле ввода
    def _show_entry(self, event):
        label_coords = self.master.coords(self.label_id)
        self.master.coords(self.entry_id, *label_coords)
        self.entry.bind_self_id(self.entry_id)
        self.master.itemconfig(self.entry_id, state="normal")  # скрывает поле ввода
        self.entry.focus_set()

    # прячет поле ввода, меняет текст в лейбле
    def _hide_entry(self, event):

        # стрипает текст в поле ввода
        text = self.entry.get_text()
        self.entry.set_text(text)

        self.master.itemconfig(self.entry_id, state="hidden")
        self.update_label()


class OverlaysUnion:
    """Группа из восьми оверлеев, расположенных на холсте.
    Этот класс занимается их инициализацией и агрегацией."""

    def __init__(self, master: Canvas, default_texts: Optional[List[str]]):
        self.master: Canvas = master
        self.view_mode: bool = master.view_mode
        self.default_texts: Optional[List] = default_texts

        self.overlays: list = []

        self._create_entries()
        self.update()

    # инициализация полей ввода
    def _create_entries(self):

        # выравнивания виджетов, относительно расположения
        c, l, r, t, b = CENTER, LEFT, RIGHT, TOP, BOTTOM
        horizontal_pos = (l, c, r, r, r, c, l, l)  # 8 позиций горизонтали
        vertical_pos = (t, t, t, c, b, b, b, c)  # 8 позиций вертикали

        # создание каждого оверлея
        for i in range(8):
            text = self.default_texts[i] if self.view_mode else ""
            overlay = Overlay(self.master, text, horizontal_pos[i], vertical_pos[i])
            self.overlays.append(overlay)

    # позиционирует и привязывает обработчики позиций
    def update(self):
        x_pad = int(self.master.width / 8)
        y_pad = int(self.master.height / 8)

        # расположение восьми позиций оверлеев
        # с верхнего левого по часовой стрелке
        positions = [
            (x_pad, y_pad),
            (self.master.width // 2, y_pad),
            (self.master.width - x_pad, y_pad),
            (self.master.width - x_pad, self.master.height // 2),
            (self.master.width - x_pad, self.master.height - y_pad),
            (self.master.width // 2, self.master.height - y_pad),
            (x_pad, self.master.height - y_pad),
            (x_pad, self.master.height // 2),
        ]

        try:  # позиционирует каждый виджет и обновляет текст
            for i, pos in enumerate(positions):
                self.overlays[i].set_coords(pos)
                self.overlays[i].update_label()
        except TclError:
            pass

    # получение текста из всех оверлеев
    def get_text(self) -> List[str]:
        entries_text = map(lambda overlay: overlay.get_text(), self.overlays)
        return list(entries_text)


class ImageComposite:
    """Класс для хранения картинки в разных видах, и состояниях"""

    def __init__(self, size: Tuple[int]):
        self.size: tuple = size
        self.stock: bool = True
        self.pil_orig: Image = None
        self.pil_sized: Image = None
        self.pil_fit: Image = None
        self.set_empty()

    def set_size(self, size):
        self.size = size

    # откроет картинку, либо создаст пустую
    def open(self, image_link: str):
        try:
            self.pil_orig = Image.open(image_link).convert("RGBA")
            self.update_size()
            self.stock = False
        except (FileNotFoundError, AttributeError):
            self.set_empty()

    def set_empty(self):
        self.pil_sized = self.pil_fit = self.pil_orig = Image.new(
            "RGBA", self.size, (0, 0, 0, 0)
        )

    # изменение размера картинки, подгонка под холст
    def update_size(self):

        # изменяем размер изображения, создаём прозрачную картинку
        self.pil_sized = self.pil_orig.copy()
        self.pil_sized.thumbnail(self.size, Image.Resampling.LANCZOS)
        self.pil_fit = Image.new("RGBA", self.size, (0, 0, 0, 0))

        # вставляем изображение в центр пустого изображения
        x_offset = (self.size[0] - self.pil_sized.width) // 2
        y_offset = (self.size[1] - self.pil_sized.height) // 2
        self.pil_fit.paste(self.pil_sized, (x_offset, y_offset))

    # получение изображения нужной прозрачности
    def get_alpha(self, alpha: float):
        if self.pil_fit.size != self.size:
            self.update_size()

        alpha_img = self.pil_fit.getchannel("A")
        alpha_img = alpha_img.point(lambda i: i * alpha)
        self.modified = self.pil_fit.copy()
        self.modified.putalpha(alpha_img)
        return self.modified


class ImageUnion:
    """Класс для хранения информации о двух картинках,
    их изменениях, и преобразованиях."""

    def __init__(self, master: Canvas):
        self.master: Canvas = master
        self.stock: bool = True
        self.size: tuple = master.width, master.height
        self.shown: Image = None
        self.transition_stage: tuple = 1, 0

        self.new = ImageComposite(self.size)
        self.old = ImageComposite(self.size)

        self.tk: ImageTk.PhotoImage = ImageTk.PhotoImage(
            Image.new("RGBA", self.size, (0, 0, 0, 0))
        )
        self.id: int = master.create_image(0, 0, anchor="nw", image=self.tk)

        # привязка фокусировки на холст при нажатие на изображение,
        # чтобы снять фокус с полей ввода
        self.master.tag_bind(
            self.id, "<Button-1>", lambda event: self.master.focus_set()
        )

    def set_new(self, image_link: str):
        self.old, self.new = self.new, self.old
        self.new.open(image_link)

    def update_size(self, size: Tuple[int]):
        if self.size == size:
            return
        self.size = size
        self.old.set_size(self.size)
        self.new.set_size(self.size)
        self.transit_delta(*self.transition_stage)

    def update_tk(self, image: Image):
        tk = ImageTk.PhotoImage(image)
        self.master.itemconfig(self.id, image=tk)
        self.tk = tk

    # меняет прозрачность для одного кадра
    def transit_delta(self, alpha_new: float, alpha_old: float):
        if alpha_new > 1:
            alpha_new = 1
        if alpha_old < 0:
            alpha_old = 0
        self.transition_stage = alpha_new, alpha_old
        try:
            new = self.new.get_alpha(alpha_new)
            old = self.old.get_alpha(alpha_old)
            self.shown = Image.alpha_composite(old, new)
            self.update_tk(self.shown)
        except:
            pass

    # расположение картинки на холсте по центру
    def update_coords(self):
        x = self.master.width // 2 - self.width // 2
        y = self.master.height // 2 - self.height // 2
        self.master.coords(self.id, x, y)


# проверка, тёмный цвет, или светлый
def is_dark_color(r: int, g: int, b: int) -> bool:

    # если палитра 16 бит, конвертирует в 8 бит
    if r > 256 or g > 256 or b > 256:
        r, g, b = r // 256, g // 256, b // 256

    # вычисление яркости пикселя по весам
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    return brightness < 128


class ImageCanvas(Canvas):
    """Объект холста с картинкой в окне создания задачи.
    на которой отображаются "умные" поля ввода.
    Если текст не введён - поле будет полупрозрачным."""

    def __init__(
        self,
        master: Tk,
        veiw_mode: bool,
        overlays: Optional[List[str]] = None,
        background: str = DEFAULT_CANVAS_COLOR,
    ):

        self.default_width = self.width = 800
        self.default_height = self.height = 400

        # создаёт объект холста
        super().__init__(
            master,
            width=self.width,
            height=self.height,
            highlightthickness=0,
            background=background,
        )
        self.pack()

        self.view_mode: bool = veiw_mode
        self.color: str = background

        # настройка плавности смены картинок
        self.frames: int = 30
        self.delay: float = 0.01

        self.init_text_id: Optional[int] = None
        self._create_init_text()
        if not veiw_mode:
            self._show_init_text()

        self.cleared: bool = True
        self.img: ImageUnion = ImageUnion(self)

        self.overlays = OverlaysUnion(self, overlays)

    # обновление изображения
    def transit_image(self):
        alpha_new, alpha_old = 0, 1
        for i in range(self.frames):
            time.sleep(self.delay)
            if i < self.frames / 3:
                alpha_new += (1 / self.frames) * 1.7
            elif i < self.frames / 1.5:
                alpha_new += (1 / self.frames) * 1.5
                alpha_old -= (1 / self.frames) * 1.5
            else:
                alpha_old -= (1 / self.frames) * 1.5
            self.img.transit_delta(alpha_new, alpha_old)

            if i == int(self.frames / 2):
                self.overlays.update()
        self.img.transit_delta(1, 0)
        self.overlays.update()

    # установка новой картинки
    def update_image(self, image_link: str):
        self.cleared = False
        self._hide_init_text()
        self.img.set_new(image_link)
        self.transit_image()

    # очистка холста от изображений (внешняя ручка)
    def clear_image(self):
        if self.cleared:
            return
        self._show_init_text()
        self.img.set_new("")
        self.transit_image()

    # создание объекта пригласительного текста
    def _create_init_text(self):
        self.init_text_id = self.create_text(
            self.width / 2,
            self.height / 2,
            font=("Arial", 24),
            justify=CENTER,
            state="hidden",
            fill="#cccccc",
        )
        self.update_texts()

    # показывает пригласительный текст
    def _show_init_text(self):
        self.itemconfig(self.init_text_id, state="normal")

    # прячет пригласительный текст
    def _hide_init_text(self):
        self.itemconfig(self.init_text_id, state="hidden")

    # проверка, тёмный ли фон на картинке за элементом канваса
    def is_dark_background(self, elem_id: int) -> bool:
        x, y = self.coords(elem_id)
        try:
            if x < 0 or y < 0:
                raise IndexError

            if self.cleared:
                raise Exception

            # цвет пикселя картинки на этих координатах
            color = self.img.shown.getpixel((x, y))
            r, g, b, a = color[0:4]

            # если пиксель на картинке, но прозрачный
            if a < 128:
                raise Exception

        # если pillow вернёт не ргб, а яркость пикселя
        except TypeError:
            return color < 128

        # если пиксель за пределами картинки, оценивается фон холста
        except Exception:
            r, g, b = self.winfo_rgb(self.color)
            r, g, b = r / 255, g / 255, b / 255

        return is_dark_color(r, g, b)

    # обновляет разрешение холста
    def update_resolution(self, width: int, height: int, resize_image: bool):

        self.width, self.height = width, height
        self.config(height=height, width=width)
        self.overlays.update()
        self.coords(self.init_text_id, self.width / 2, self.height / 2)

        if resize_image:
            self.img.update_size((width, height))

    # формирует список из восьми строк, введённых в полях
    def fetch_entries_text(self) -> list:
        return self.overlays.get_text()

    # обновляет цвета отступов холста
    def update_background_color(self, color: str):
        self.color = color
        self.config(background=color)
        self.overlays.update()

    def update_texts(self):
        if self.init_text_id:
            self.itemconfig(self.init_text_id, text=Settings.lang.read("task.initText"))


class DirectoryManager(ttk.Frame):
    """Менеджер директорий, поле со списком.
    Даёт возможность добавлять, удалять директории,
    и менять порядок кнопками и перетаскиванием"""

    def __init__(
        self,
        master: Union[Tk, ttk.Frame],
        veiw_mode: bool,
        dirs: list,
        on_change: Callable,
    ):
        super().__init__(master)
        self.name: str = "dirs"

        self.widgets: Dict[str, Widget] = {}
        self.drag_data: dict = {"start_index": None, "item": None}
        self.on_change: Callable = on_change

        self.veiw_mode: bool = veiw_mode
        self._init_widgets()
        self._pack_widgets()
        self.update_texts()

        self.dirs: list = dirs
        self._update_listbox(max_length=30)

    # возвращает список директорий
    def get_dirs(self) -> list:
        return self.dirs[:]

    # возвращает все картинки во всех директориях
    def get_all_imgs(self) -> list:
        images = []
        for dir in self.dirs:
            images += find_img_in_dir(dir, full_path=True)
        return images

    # меняет "ужатость" каждой директории в списке
    def _update_listbox(self, max_length):
        self.listbox.delete(0, END)
        for path in self.dirs:
            shrinked = shrink_path(path, max_length)
            self.listbox.insert(END, shrinked)

    def _init_widgets(self):

        self.top_frame = ttk.Frame(self)

        self.widgets["lbDirList"] = ttk.Label(self.top_frame)

        # при растягивании фрейма
        def on_resize(event):
            max_length = int(event.width // 8)
            self._update_listbox(max_length)

        # создание списка и полосы прокрутки
        self.listbox = Listbox(self.top_frame, selectmode=SINGLE, width=20, height=8)
        self.scrollbar = ttk.Scrollbar(
            self.top_frame, orient="vertical", command=self.listbox.yview
        )
        self.listbox.config(yscrollcommand=self.scrollbar.set)

        # в режиме просмотра не будет возможности
        # изменение порядка элементов в списке,
        # поэтому, привязка нажатия не произойдёт
        if not self.veiw_mode:
            self.listbox.bind("<Button-1>", self._start_drag)
            self.listbox.bind("<B1-Motion>", self._do_drag)

        self.top_frame.bind("<Configure>", on_resize)
        self.listbox.bind("<Double-Button-1>", self._on_double_click)

        self.button_frame = ttk.Frame(self)

        self.widgets["btAddDir"] = ttk.Button(
            self.button_frame, width=8, command=self._add_directory
        )
        self.widgets["btRemDir"] = ttk.Button(
            self.button_frame, width=8, command=self._remove_directory
        )

    def _pack_widgets(self):
        self.top_frame.pack(side=TOP, fill=BOTH, expand=True)
        self.widgets["lbDirList"].pack(side=TOP, anchor="w")
        self.listbox.pack(side=LEFT, fill=BOTH, expand=True)
        self.scrollbar.pack(side=LEFT, fill=Y)

        self.button_frame.pack(side=TOP, anchor="w", padx=(0, 15), pady=10, fill=X)

        if not self.veiw_mode:
            self.widgets["btAddDir"].pack(side=LEFT, anchor="e", padx=5, expand=True)
            self.widgets["btRemDir"].pack(side=RIGHT, anchor="w", padx=5, expand=True)

    # добавление директории
    def _add_directory(self):
        dir_name = filedialog.askdirectory(parent=self, initialdir=GlobalStates.last_dir)
        if not dir_name:
            return
        if not find_img_in_dir(dir_name):
            return
        GlobalStates.last_dir = os.path.dirname(dir_name)
        self.listbox.insert(END, shrink_path(dir_name, 25))
        self.dirs.append(dir_name)
        self.on_change(self.dirs[:])

    # удаление выбранной директории из списка
    def _remove_directory(self):
        selected = self.listbox.curselection()
        if selected:
            index = selected[0]
            self.listbox.delete(index)
            del self.dirs[index]
            self.on_change(self.dirs[:])

    # начало перетаскивания элемента
    def _start_drag(self, event):
        self.drag_data["start_index"] = self.listbox.nearest(event.y)
        self.drag_data["item"] = self.listbox.get(self.drag_data["start_index"])

    # меняет местами две директории в списке
    def _swap_dirs(self, index_old: int, index_new: int, text: str = None):
        if not text:
            text = self.listbox.get(index_old)

        self.listbox.delete(index_old)
        self.listbox.insert(index_new, text)

        self.dirs[index_old], self.dirs[index_new] = (
            self.dirs[index_new],
            self.dirs[index_old],
        )
        self.listbox.select_set(index_new)

    # процесс перетаскивания элемента
    def _do_drag(self, event):
        new_index = self.listbox.nearest(event.y)
        if new_index != self.drag_data["start_index"]:
            self._swap_dirs(
                self.drag_data["start_index"], new_index, self.drag_data["item"]
            )
            self.drag_data["start_index"] = new_index

    # открывает дитекторию по даблклику (если её не существует - удаляет)
    def _on_double_click(self, event):
        selected_index = self.listbox.curselection()
        if not selected_index:
            return

        index = selected_index[0]
        dir_to_open = self.dirs[index]
        try:
            if platform.system() == "Windows":
                os.startfile(dir_to_open)
            elif platform.system() == "Linux":
                os.system(f"xdg-open {dir_to_open}")
            else:
                os.system(f"open -- {dir_to_open}")
        except:
            self.listbox.delete(index)
            self.listbox.insert(index, Settings.lang.read("dirs.DirNotExists"))
            self.after(2000, self.listbox.delete, index)
            self._remove_directory()

    def update_texts(self):
        for w_name, widget in self.widgets.items():
            if not w_name.startswith("_"):
                widget.config(text=Settings.lang.read(f"{self.name}.{w_name}"))


class ToolTip:
    """Подсказка при наведении на виджет.
    Лейбл с текстом поверх всего,
    коорый появляется при наведении,
    и исчизает при уходе курсора"""

    def __init__(self, widget: Widget, get_text: Callable):
        self.tip_window: Optional[Toplevel] = None

        # функция, по которой получим текст подсказки,
        # и виджет, к которому привязывается подсказка
        self.get_text: Callable = get_text
        self.widget: Widget = widget
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    # показать "подсказку"
    def show_tip(self, event=None):
        text = self.get_text()
        if not text:
            return

        # вычисляем координаты окна
        x_shift = len(text) * 2
        x = self.widget.winfo_rootx() - x_shift
        y = self.widget.winfo_rooty() + 30

        # создание окна для подсказки
        # без системной рамки окна
        self.tip_window = Toplevel(self.widget)
        self.tip_window.wm_overrideredirect(True)
        self.tip_window.wm_geometry(f"+{x}+{y}")

        label = Label(self.tip_window, text=text, relief="solid", borderwidth=1)
        label.pack()

    # спрятать подсказку
    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None






    #  из файла windows.py:

"""
Любое окно наследуется от Tk/TopLevel и WindowMixin.
Именно в таком порядке, это важно. Если перепутать, 
объект инициализируется как WindowMixin.

Вначале конструктора должен быть вызван super().__init__(),
который инициализирует объект как сущность Tk/TopLevel.

Должны быть объявлены имя окна, и необходимые атрибуты из миксина,
а в конце должен быть вызван метод super()._default_set_up().
Интерпретатор не найдёт такой метод в Tk/TopLevel, и будет 
выполнен метод из миксина.

Также, должны быть имплементированы методы создания и упаковки виджетов,
они тоже вызываются миксином при стандартной настройке окна. 

Любые виджеты внутри окна должны добавляться в словарь виджетов,
а тексты для них прописываться в классе настроек Settings, в атрибуте lang.
Если появляется более сложная композиция, метод update_texts должен
быть расширен так, чтобы вызывать обновление текста во всех виджетах.
"""


class RootWindow(Tk, WindowMixin):
    """Основное окно"""

    def __init__(self):
        super().__init__()
        self.name: str = "root"

        self.widgets: Dict[str, ttk.Widget] = {}
        self.task_bars: Dict[int, TaskBar] = {}  # словарь регистрации баров задач

        self.size: Tuple[int] = 550, 450
        self.resizable(True, True)  # можно растягивать

        super()._default_set_up()

    # при закрытии окна
    def close(self):

        def accept_uncomlete_exit():
            for task in TaskManager.running_list():
                task.cancel()
            self.destroy()

        if TaskManager.running_list():  # если есть активные задачи
            # открытие окна с новой задачей (и/или переключение на него)
            return LocalWM.open(
                WarningWindow,
                name="warn",
                master=self,
                type="exit",
                accept_def=accept_uncomlete_exit,
            ).focus()
        self.destroy()

    # создание и настройка виджетов
    def _init_widgets(self):

        # открытие окна с новой задачей (и/или переключение на него)
        def open_new_task():
            LocalWM.open(NewTaskWindow, "task").focus()

        # открытие окна настроек (и/или переключение на него)
        def open_settings():
            LocalWM.open(SettingsWindow, "sets").focus()

        # создание фреймов
        self.upper_bar = upperBar = ttk.Frame(self, style="Main.ToolBar.TFrame")
        self.task_space = ScrollableFrame(self)
        self.taskList = self.task_space.scrollable_frame

        # создание виджетов, привязывание функций
        self.widgets["newTask"] = ttk.Button(upperBar, command=open_new_task)
        self.widgets["openSets"] = ttk.Button(upperBar, command=open_settings)

    # расположение виджетов
    def _pack_widgets(self):
        self.upper_bar.pack(fill=X)
        self.task_space.pack(fill=BOTH, expand=True)

        self.widgets["newTask"].pack(side=LEFT, padx=10, pady=10)
        self.widgets["openSets"].pack(side=RIGHT, padx=10, pady=10)

    # добавление строки задачи
    def add_task_bar(self, task: Task, **params) -> Callable:
        # сборка функции для открытия диалога при попытке отмены задачи
        cancel_def = lambda: LocalWM.open(
            WarningWindow, "warn", self, type="cancel", accept_def=task.cancel
        )
        task_bar = TaskBar(
            self.taskList, task, cancel_def=cancel_def, **params
        )  # создаёт бар задачи
        self.task_bars[task.id] = task_bar
        return task_bar.update_progress  # возвращает ручку полосы прогресса

    # удаление строки задачи
    def del_task_bar(self, task_id: int) -> None:
        if task_id in self.task_bars:
            self.task_bars[task_id].delete()
            del self.task_bars[task_id]

    # обработка ошибки процесса catframes
    def handle_error(self, task_id: int, error: str) -> None:
        if task_id in self.task_bars:
            self.task_bars[task_id].set_error(error)
        LocalWM.update_on_task_finish()

    # закрытие задачи, смена виджета
    def finish_task_bar(self, task_id: int) -> None:
        if task_id in self.task_bars:
            self.task_bars[task_id].finish()
        LocalWM.update_on_task_finish()

    # расширение метода обновления текстов
    def update_texts(self) -> None:
        super().update_texts()
        for bar in self.task_bars.values():
            bar.update_texts()


class SettingsWindow(Toplevel, WindowMixin):
    """Окно настроек"""

    def __init__(self, root: RootWindow):
        super().__init__(master=root)
        self.name: str = "sets"

        self.widgets: Dict[str, ttk.Widget] = {}

        self.size: Tuple[int] = 250, 120
        self.resizable(False, False)
        self.transient(root)

        self.bind("<FocusOut>", self._on_focus_out)

        super()._default_set_up()

    # при потере фокуса окна, проверяет, не в фокусе ли его виджеты
    def _on_focus_out(self, event):
        try:
            if not self.focus_get():
                return self.close()
        except:  # ловит ошибку, которая возникает при фокусе на комбобоксе
            pass

    # создание и настройка виджетов
    def _init_widgets(self):
        self.main_frame = ttk.Frame(self)
        self.content_frame = ttk.Frame(self.main_frame)

        # виджет и комбобокс языка
        self.widgets["lbLang"] = ttk.Label(self.content_frame)
        self.widgets["_cmbLang"] = ttk.Combobox(
            self.content_frame,
            values=Settings.lang.get_all(),  # вытягивает список языков
            state="readonly",
            width=9,
        )

        # виджет и комбобокс тем
        self.widgets["lbTheme"] = ttk.Label(self.content_frame)
        self.widgets["_cmbTheme"] = ttk.Combobox(
            self.content_frame,
            values=ttk.Style().theme_names(),
            state="readonly",
            width=9,
        )

        # применение настроек
        def apply_settings(event):
            current_theme = self.widgets["_cmbTheme"].current()
            Settings.theme.set(index=current_theme)
            current_lang = self.widgets["_cmbLang"].current()
            Settings.lang.set(index=current_lang)
            Settings.save()

            for window in LocalWM.all():
                window.update_texts()

        # привязка применения настроек к выбору нового значения в комбобоксах
        self.widgets["_cmbLang"].bind("<<ComboboxSelected>>", apply_settings)
        self.widgets["_cmbTheme"].bind("<<ComboboxSelected>>", apply_settings)

    # расположение виджетов
    def _pack_widgets(self):
        self.main_frame.pack(expand=True, fill=BOTH)
        self.content_frame.pack(padx=10, pady=30)

        self.widgets["lbLang"].grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.widgets["_cmbLang"].grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.widgets["_cmbLang"].current(
            newindex=Settings.lang.current_index
        )  # подставляем в ячейку текущий язык

        self.widgets["lbTheme"].grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.widgets["_cmbTheme"].grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        self.widgets["_cmbTheme"].current(newindex=Settings.theme.current_index)


class NewTaskWindow(Toplevel, WindowMixin):
    """Окно создания новой задачи"""

    def __init__(self, root: RootWindow, **kwargs):
        super().__init__(master=root)
        self.name: str = "task"
        self.widgets: Dict[str, Widget] = {}

        self.task_config: TaskConfig = TaskConfig()
        self.view_mode: bool = False

        # если передан конфиг, берёт его, устанавливает флаг просмотра
        if kwargs.get("task_config"):
            self.task_config = kwargs.get("task_config")
            self.view_mode = True

        self.size: Tuple[int] = 900, 500
        self.resizable(True, True)

        super()._default_set_up()
        threading.Thread(target=self.canvas_updater, daemon=True).start()

    def close(self):
        super().close()

        # удаляет директорию с превью рендерами
        dir_path = os.path.join(USER_DIRECTORY, PREVIEW_DIRNAME)
        if not os.path.exists(dir_path):
            return
        for i in range(10):
            try:
                shutil.rmtree(dir_path)
                break
            except:
                time.sleep(1)

    # поток, обновляющий картинку и размеры холста
    def canvas_updater(self):
        last_dirs = []
        images_to_show = []
        image_index = 0

        # проверяет, не поменялся ли список картинок
        def check_images_change():
            nonlocal images_to_show, last_dirs, image_index

            new_dirs = self.dir_manager.get_dirs()
            if last_dirs == new_dirs:
                return

            last_dirs = new_dirs
            all_images = self.dir_manager.get_all_imgs()

            # если картинок меньше 4, забираем все
            if len(all_images) < 4:
                images_to_show = all_images
                image_index = 0
            else:  # если их много - выбираем с нужным шагом
                step = len(all_images) // 4
                images_to_show = all_images[step::step]

        # попытка обновления картинки
        def update_image():
            nonlocal image_index

            if not images_to_show:
                self.image_canvas.clear_image()
                return

            self.image_canvas.update_image(images_to_show[image_index])
            image_index = (image_index + 1) % len(images_to_show)
            time.sleep(10)

        while True:
            try:
                check_images_change()
                update_image()
                time.sleep(1)
            except AttributeError:
                time.sleep(0.1)
            except TclError:  # это исключение появится, когда окно закроется
                return

    # сбор данных из виджетов, создание конфигурации
    def _collect_task_config(self):
        overlays_texts = self.image_canvas.fetch_entries_text()
        self.task_config.set_overlays(overlays_texts=overlays_texts)

        framerate = self.widgets["_spnFramerate"].get()
        quality = self.widgets["cmbQuality"].current()
        self.task_config.set_specs(framerate=framerate, quality=quality)

    # проверяет, указаны ли директории и путь сохранения файла
    # если нет - кнопки копирования, сохранения, предпросмотра будут недоступны
    def _validate_task_config(self):
        state = "disabled"
        if self.task_config.get_dirs() and self.task_config.get_filepath():
            state = "enabled"

        self.widgets["btCopyBash"].configure(state=state)
        self.widgets["btCopyWin"].configure(state=state)
        self.widgets["cmbTime"].configure(
            state=state if state == "disabled" else "readonly"
        )
        self.widgets["_btPreview"].configure(state=state)
        self.widgets["btCreate"].configure(state=state)

    # создание и запуск задачи
    def _create_task_instance(self):
        task: Task = TaskManager.create(self.task_config)

        # создание бара задачи, получение метода обновления прогресса
        update_progress: Callable = self.master.add_task_bar(
            task, view=NewTaskWindow.open_view
        )
        # передача всех методов в объект коббека,
        # и инъекция его при старте задачи
        gui_callback = GuiCallback(
            update_function=update_progress,
            finish_function=self.master.finish_task_bar,
            error_function=self.master.handle_error,
            delete_function=self.master.del_task_bar,
        )
        task.start(gui_callback)

    @staticmethod
    def _watch_preview(link: str):
        time.sleep(3)
        os.startfile(link)

    @staticmethod
    def _create_temp_dir():
        dir_path = os.path.join(USER_DIRECTORY, PREVIEW_DIRNAME)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

    # создаёт копию конфига, но с параметрами для превью
    def _create_preview_config(self) -> TaskConfig:
        preview_config = copy.deepcopy(self.task_config)
        self._create_temp_dir()
        extention = preview_config.get_filepath().split(".")[-1]
        preview_path = os.path.join(
            USER_DIRECTORY, PREVIEW_DIRNAME, PREVIEW_FILENAME.format(ex=extention)
        )
        limit = self.widgets["cmbTime"].current() + 1
        preview_config.set_preview_params(limit=limit, path=preview_path)
        return preview_config

    # создание и запуск задачи
    def _create_task_preview(self):
        # для создания задачи под рендеринг превью,
        # в коллбек передаются адапторы,
        # влияющие на полосу прогресса, и её отмену

        config: TaskConfig = self._create_preview_config()
        task: Task = TaskManager.create(config)
        self.widgets["btPrevCancel"].configure(command=task.cancel)

        def updating_adapter(progress: float, *args, **kwargs):
            try:
                self.widgets["_prevProgress"].config(value=progress)
            except:
                task.cancel()

        def deletion_adapter(*args, **kwargs):
            self._cancel_processing_screen()

        def finishing_adapter(*args, **kwargs):
            if not task.stop_flag:
                self._watch_preview(config.get_filepath())
            self._cancel_processing_screen()

        def handle_error(id, error):
            print(f"ошибка {error}")

        gui_callback = GuiCallback(
            update_function=updating_adapter,
            finish_function=finishing_adapter,
            error_function=handle_error,
            delete_function=deletion_adapter,
        )
        task.start(gui_callback)


    # Валидация для поля ввода цвета
    # Должна пропускать любые 16-р значения
    # до 6ти знаков, с "#" вначале и без.
    # Пустая строка допустима.  
    @staticmethod
    def validate_color(value: str) -> bool:
        if not value:
            return True
        if value.count("#") > 1:
            return False
        if value.count("#") == 1 and not value.startswith("#"):
            return False
        value = value.lstrip("#")
        if len(value) > 6:
            return False
        for v in value:
            if v.lower() not in "0123456789abcdef":
                return False
        return True
        
    # Валидация для поля ввода фпс.
    # Должна пропускать любые числа от 0 до 60.
    # Пустая строка так же допустима.
    @staticmethod
    def validate_fps(value) -> bool:
        if not value:
            return True
        if not value.isdigit():
            return False
        return 0 <= int(value) <= 60

    def _init_widgets(self):
        self.main_frame = Frame(self)
        self.main_pane = PanedWindow(
            self.main_frame,
            orient=HORIZONTAL,
            sashwidth=5,
            background="grey",
            sashrelief="flat",
            opaqueresize=True,
            proxybackground="grey",
            proxyborderwidth=5,
            proxyrelief="flat",
        )

        # создание холста с изображением
        self.canvas_frame = Frame(self.main_pane, background=DEFAULT_CANVAS_COLOR)
        self.main_pane.add(self.canvas_frame, stretch="always")
        self.main_pane.paneconfig(self.canvas_frame, minsize=300)
        self.canvas_frame.pack_propagate(False)
        self.canvas_frame.config(width=self.winfo_width() - 200)

        self.image_canvas = ImageCanvas(
            master=self.canvas_frame,
            veiw_mode=self.view_mode,
            overlays=self.task_config.get_overlays(),
            background=self.task_config.get_color(),
        )

        # создание табличного фрейма меню
        self.menu_frame = ttk.Frame(self.main_pane)
        self.main_pane.add(self.menu_frame, stretch="never")
        self.main_pane.paneconfig(self.menu_frame, minsize=250)

        self._bind_resize_events()

        # передача дитекротий в конфиг, валидация
        def set_dirs_to_task_config(dirs):
            self.task_config.set_dirs(dirs)
            self._validate_task_config()

        self.dir_manager = DirectoryManager(
            master=self.menu_frame,
            veiw_mode=self.view_mode,
            dirs=self.task_config.get_dirs(),
            on_change=set_dirs_to_task_config,  # передача ручки
        )
        self.settings_grid = ttk.Frame(self.menu_frame)

        # выбор пути для сохранения файла
        def ask_filepath():
            filetypes = [("mp4 file", ".mp4"), ("webm file", ".webm")]
            filepath = filedialog.asksaveasfilename(
                parent=self,
                filetypes=filetypes,
                defaultextension=".mp4",
                initialdir=GlobalStates.last_dir,
            )
            if filepath:
                GlobalStates.last_dir = os.path.dirname(filepath)
                self.task_config.set_filepath(filepath)
                self.widgets["_btPath"].configure(text=filepath.split("/")[-1])
                self._validate_task_config()

        # виджеты столбца описания кнопок
        self.widgets["lbColor"] = ttk.Label(self.settings_grid)
        self.widgets["lbFramerate"] = ttk.Label(self.settings_grid)
        self.widgets["lbQuality"] = ttk.Label(self.settings_grid)
        self.widgets["lbSaveAs"] = ttk.Label(self.settings_grid)

        # передача цвета в холст и конфиг
        def update_color(color: str):
            self.image_canvas.update_background_color(color)
            self.canvas_frame.config(background=color)
            self.task_config.set_color(color)

        # вызов системного окна по выбору цвета
        def ask_color():
            color = colorchooser.askcolor(parent=self)[-1]
            if not color:
                return
            self.widgets["_entColor"].delete(0, END)
            self.widgets["_entColor"].insert(0, color)
            update_color(color)

        self.color_frame = ttk.Frame(self.settings_grid)


        v_color = self.register(self.validate_color), "%P"

        self.widgets["_entColor"] = ttk.Entry(
            self.color_frame,
            validate="key",
            validatecommand=v_color,
            justify=CENTER,
            width=5,
        )
        self.widgets["_entColor"].insert(0, self.task_config.get_color())

        def check_empty_color(event):
            text: str = self.widgets["_entColor"].get()
            self.widgets["_entColor"].delete(0, END)

            if text.startswith("#"):
                text = text.lower().lstrip("#")
            if len(text) == 0:
                self.widgets["_entColor"].insert(0, DEFAULT_CANVAS_COLOR)
                return

            missing = 6 - len(text)
            color = "#" + text + "0" * missing
            self.widgets["_entColor"].insert(0, color)
            update_color(color)

        self.widgets["_entColor"].bind("<FocusOut>", check_empty_color)

        # виджеты правого столбца (кнопка цвета, комбобоксы и кнопка создания задачи)
        self.palette_icon = PhotoImage(data=base64.b64decode(PALETTE_ICON_BASE64))
        self.widgets["_btColor"] = ttk.Button(
            self.color_frame,
            command=ask_color,
            image=self.palette_icon,
            compound=CENTER,
            width=2,
        )


        v_fps = self.register(self.validate_fps), "%P"

        self.widgets["_spnFramerate"] = ttk.Spinbox(  # виджет выбора фреймрейта
            self.settings_grid,
            from_=1,
            to=60,
            validate="key",
            validatecommand=v_fps,
            justify=CENTER,
            width=8,
        )

        # проверяет, пустое ли поле ввода, и если да, вписывает минимальное значиние
        def check_empty_fps(event):
            value = self.widgets["_spnFramerate"].get()
            value = int(value) if value else 1
            value = value or 1
            self.widgets["_spnFramerate"].set(value)

        self.widgets["_spnFramerate"].bind("<FocusOut>", check_empty_fps)

        self.widgets[
            "_spnFramerate"
        ].set(  # установка начального значения в выборе фреймрейта
            self.task_config.get_framerate()
        )

        self.widgets["cmbQuality"] = ttk.Combobox(  # виджет выбора качества
            self.settings_grid,
            state="readonly",
            justify=CENTER,
            width=8,
        )

        path = self.task_config.get_filepath()
        file_name = (
            path.split("/")[-1] if path else Settings.lang.read("task.btPathChoose")
        )
        self.widgets["_btPath"] = ttk.Button(
            self.settings_grid, command=ask_filepath, text=file_name
        )
        ToolTip(self.widgets["_btPath"], self.task_config.get_filepath)

        # копирование команды в буфер обмена
        def copy_to_clip(bash: bool = True):
            self._collect_task_config()
            command = self.task_config.convert_to_command(for_user=True, bash=bash)
            command = " ".join(command)
            self.clipboard_clear()
            self.clipboard_append(command)

        # лейбл и кнопка копирования команды
        self.widgets["lbCopy"] = ttk.Label(self.settings_grid)
        self.copy_frame = ttk.Frame(self.settings_grid)
        self.widgets["btCopyBash"] = ttk.Button(
            self.copy_frame, command=copy_to_clip, width=3
        )
        self.widgets["btCopyWin"] = ttk.Button(
            self.copy_frame, command=lambda: copy_to_clip(bash=False), width=3
        )

        # если это режим просмотра, все виджеты, кроме копирования будут недоступны
        if self.view_mode:
            for w_name, w in self.widgets.items():
                if "lb" in w_name or "Copy" in w_name:
                    continue
                w.configure(state="disabled")

        self.create_frame = ttk.Frame(self.settings_grid)

        self.widgets["cmbTime"] = ttk.Combobox(
            self.create_frame,
            state="readonly",
            values=Settings.lang.read("task.cmbTime"),
            justify=CENTER,
            width=6,
        )
        self.play_icon = PhotoImage(data=base64.b64decode(PLAY_ICON_BASE64))
        self.widgets["_btPreview"] = ttk.Button(
            self.create_frame,
            command=self._show_processing_screen,
            image=self.play_icon,
            compound=CENTER,
            width=2,
        )

        def add_task():
            self._collect_task_config()
            self._create_task_instance()
            self.close()

        self.widgets["btCreate"] = ttk.Button(
            self.create_frame, command=add_task, style="Create.Task.TButton", width=8
        )

        # далее объявляются виджеты экрана рендера предпросмотра
        self.preview_outer_frame = ttk.Frame(self)
        self.preview_inner_frame = ttk.Frame(self.preview_outer_frame)

        self.widgets["lbPrevSign"] = ttk.Label(
            self.preview_inner_frame,
            font=font.Font(size=14),
        )
        self.widgets["_prevProgress"] = ttk.Progressbar(
            self.preview_inner_frame,
            length=320,
            maximum=1,
            value=0,
        )
        self.widgets["btPrevCancel"] = ttk.Button(
            self.preview_inner_frame,
            command=self._cancel_processing_screen,
            text="cancel",
        )

    def _show_processing_screen(self):
        try:
            self.main_frame.pack_forget()
            self.preview_outer_frame.pack(expand=True, fill=BOTH)
            self._collect_task_config()
            self._create_task_preview()
        except TclError:
            pass

    def _cancel_processing_screen(self):
        try:
            self.main_frame.pack(expand=True, fill=BOTH)
            self.preview_outer_frame.pack_forget()
        except TclError:
            pass

    # привязка событий изменений размеров
    def _bind_resize_events(self):
        """ресайз картинки - это долгий процесс, PIL задерживает поток,
        поэтому, во избежание лагов окна - логика следующая:

        если пользователь всё ещё тянет окно/шторку -
            холст меняет расположение оверлеев

        но если события изменения не было уже 100мс -
            холст обновляет размер всего, в том числе - картинки"""

        resize_delay = 100  # задержка перед вызовом обновления
        resize_timer = None  # идентификатор таймера окна

        def trigger_update(resize_image: bool):
            new_width = self.canvas_frame.winfo_width()
            new_height = self.canvas_frame.winfo_height()
            self.image_canvas.update_resolution(new_width, new_height, resize_image)

        # вызов при любом любом изменении размера
        def on_resize(event):

            # если событие - изменение размера окна,
            # но ширина или высота меньше минимальных,
            # то его обрабатывать не нужно
            if event.type == 22:
                if event.width < self.size[0] or event.height < self.size[1]:
                    return

            nonlocal resize_timer
            trigger_update(resize_image=False)

            if resize_timer:
                self.after_cancel(resize_timer)

            # новый таймер, который вызовет обновление через заданное время
            resize_timer = self.after(resize_delay, trigger_update, True)

        # привязка обработчика к событиям
        # изменения размеров окна и перетягиания шторки
        self.bind("<Configure>", on_resize)
        self.main_pane.bind("<Configure>", on_resize)

    # расположение виджетов
    def _pack_widgets(self):
        self.main_frame.pack(expand=True, fill=BOTH)
        self.main_pane.pack(expand=True, fill=BOTH)

        self.dir_manager.pack(expand=True, fill=BOTH, padx=(15, 0), pady=(20, 0))
        self.settings_grid.pack(fill=X, pady=10, padx=10)

        self.settings_grid.columnconfigure(0, weight=0)
        self.settings_grid.columnconfigure(1, weight=1)

        self.widgets["lbColor"].grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.color_frame.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.widgets["_entColor"].pack(side=LEFT, fill=X, expand=True)
        self.widgets["_btColor"].pack(side=LEFT)

        self.widgets["lbFramerate"].grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.widgets["_spnFramerate"].grid(
            row=1, column=1, sticky="sewn", padx=5, pady=5
        )

        self.widgets["lbQuality"].grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.widgets["cmbQuality"].grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        self.widgets["lbSaveAs"].grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.widgets["_btPath"].grid(row=3, column=1, sticky="ew", padx=5, pady=5)

        self.widgets["lbCopy"].grid(row=4, column=0, sticky="e", padx=5, pady=5)
        self.copy_frame.grid(row=4, column=1, padx=5, pady=5, sticky="ew")
        self.widgets["btCopyBash"].pack(side=LEFT, fill=BOTH, expand=True)
        self.widgets["btCopyWin"].pack(side=LEFT, fill=BOTH, expand=True)

        if not self.view_mode:
            self.create_frame.grid(
                columnspan=2, row=5, column=0, sticky="e", padx=5, pady=(15, 5)
            )
            self.widgets["btCreate"].pack(padx=(10, 0), side=RIGHT)
            self.widgets["_btPreview"].pack(side=RIGHT)
            self.widgets["cmbTime"].pack(side=RIGHT)

        self._validate_task_config()

        # далее пакуются виджеты экрана рендера предпросмотра
        self.preview_outer_frame.grid_columnconfigure(0, weight=1)
        self.preview_outer_frame.grid_rowconfigure(0, weight=1)

        self.preview_inner_frame.grid(row=0, column=0, sticky="")
        self.widgets["lbPrevSign"].pack(anchor="nw")
        self.widgets["_prevProgress"].pack(pady=10)
        self.widgets["btPrevCancel"].pack(anchor="se")

    def update_texts(self) -> None:
        super().update_texts()
        self.dir_manager.update_texts()
        self.image_canvas.update_texts()

        # установка начального значения в выборе качества
        self.widgets["cmbQuality"].current(newindex=self.task_config.get_quality())
        if self.view_mode:
            self.title(Settings.lang.read(f"task.title.view"))
        if not self.task_config.get_filepath():
            self.widgets["_btPath"].configure(
                text=Settings.lang.read("task.btPathChoose")
            )

    # открытие окна в режиме просмотра
    @staticmethod
    def open_view(task_config: TaskConfig):
        LocalWM.open(NewTaskWindow, "task", task_config=task_config)


class WarningWindow(Toplevel, WindowMixin):
    """Окно предупреждения при выходе"""

    def __init__(self, root: RootWindow, **kwargs):
        super().__init__(master=root)
        self.name = "warn"
        self.type: str = kwargs.get("type")
        self.accept_def: Callable = kwargs.get("accept_def")

        self.widgets: Dict[str, Widget] = {}
        self.size = 260, 150
        self.resizable(False, False)

        super()._default_set_up()

    def _init_widgets(self):
        self.main_frame = ttk.Frame(self)

        # два лейбла предупреждения (с крупным текстом, и обычным)
        self.widgets["lbWarn"] = ttk.Label(
            self.main_frame, padding=[0, 20, 0, 5], font=font.Font(size=16)
        )
        self.widgets["lbText"] = ttk.Label(self.main_frame, padding=0)

        # кнопки "назад" и "выйти"
        self.choise_frame = ttk.Frame(self.main_frame)

        def accept():
            self.accept_def()
            self.close()

        self.widgets["btAccept"] = ttk.Button(self.choise_frame, command=accept)
        self.widgets["btDeny"] = ttk.Button(self.choise_frame, command=self.close)

    def _pack_widgets(self):
        self.main_frame.pack(expand=True, fill=BOTH)

        self.widgets["lbWarn"].pack(side=TOP)
        self.widgets["lbText"].pack(side=TOP)

        self.widgets["btAccept"].pack(side=LEFT, anchor="w", padx=5)
        self.widgets["btDeny"].pack(side=LEFT, anchor="w", padx=5)
        self.choise_frame.pack(side=BOTTOM, pady=10)

    def update_texts(self):
        for w_name, widget in self.widgets.items():
            new_text_data = Settings.lang.read(f"{self.name}.{self.type}.{w_name}")
            widget.config(text=new_text_data)


class NotifyWindow(Toplevel, WindowMixin):
    """Окно предупреждения о портах в настройках"""

    def __init__(self, root: Toplevel):
        super().__init__(master=root)
        self.name: str = "noti"
        self.widgets: Dict[str, Widget] = {}

        self.size: Tuple[int] = 350, 160
        self.resizable(False, False)

        super()._default_set_up()

    def _init_widgets(self):

        _font = font.Font(size=16)

        self.widgets["lbWarn"] = ttk.Label(self, padding=[0, 20, 0, 5], font=_font)
        self.widgets["lbText"] = ttk.Label(self, padding=0)
        self.widgets["lbText2"] = ttk.Label(self, padding=0)

        self.frame = ttk.Frame(self)
        self.widgets["_btOk"] = ttk.Button(self.frame, text="OK", command=self.close)

    def _pack_widgets(self):
        self.widgets["lbWarn"].pack(side=TOP)
        self.widgets["lbText"].pack(side=TOP)
        self.widgets["lbText2"].pack(side=TOP)

        self.widgets["_btOk"].pack(anchor="w", padx=5)
        self.frame.pack(side=BOTTOM, pady=10)





    #  из файла util_checker.py:

class SingleCheck(ttk.Frame):
    """Проверка для конкретной утилиты.
    Представляет собой "бар" с названием утилиты,
    информацией по статусу поиска, и значком.
    При инициализации принимает инъекцией метод
    для поиска утилиты в системе"""

    def __init__(self, master: ttk.Frame, util_name: str, search_method: Callable):
        super().__init__(master)
        self.widgets: Dict[str, ttk.Widget] = {}
        self.util_name = util_name
        self.search_method = search_method
        self._init_widgets()
        self._pack_widgets()

    @abstractmethod
    def search_method() -> str:
        ...

    def _init_widgets(self):
        big_font = font.Font(size=20)
        mid_font = font.Font(size=12)
        self.top_frame = ttk.Frame()
        self.bottom_frame = ttk.Frame()

        self.widgets["main_label"] = ttk.Label(
            self.top_frame, font=big_font, text=f"{self.util_name}"
        )
        self.widgets["status_image"] = ttk.Label(self.top_frame)
        self.widgets["bottom_label"] = ttk.Label(
            self.bottom_frame, font=mid_font, text = f"searching..."
        )

        self.ok_image = base64_to_tk(OK_ICON_BASE64)
        self.err_image = base64_to_tk(ERROR_ICON_BASE64)

    def _pack_widgets(self):
        self.top_frame.pack(expand=True, fill=X, pady=(50, 0))
        self.bottom_frame.pack(expand=True, fill=X, pady=(0, 10))
        self.widgets["main_label"].pack(side=LEFT, padx=20)
        self.widgets["status_image"].pack(side=RIGHT, padx=20)
        self.widgets["bottom_label"].pack(side=LEFT, padx=20)

    def check(self):
        self.found: str = self.search_method()

        text = "Not found"
        status_image = self.err_image
        if self.found:
            try:
                text = shrink_path(self.found, 45)
            except:
                text = self.found
            status_image = self.ok_image
        
        
        self.widgets["bottom_label"].configure(text=text)
        self.widgets["status_image"].configure(image=status_image)


class UtilChecker(Tk, WindowMixin):
    """Окно, в котором происходит первичная проверка необходимых утилит"""

    def __init__(self):
        super().__init__()
        self.name: str = "checker"

        self.widgets: Dict[str, ttk.Widget] = {}

        self.size: Tuple[int] = 400, 400
        self.resizable(False, False)

        self.all_checked = False
        super()._default_set_up()

        self.check_thread = threading.Thread(target=self.start_check, daemon=True)
        self.after(1000, self.check_thread.start)

    def _init_widgets(self): 
        self.main_frame = ttk.Frame(self)
        
        def pil_search():
            if PIL_FOUND_FLAG:
                return "Installed in the current environment."
            
        self.pil = SingleCheck(self.main_frame, "Pillow", pil_search)
        self.ffmpeg = SingleCheck(
            self.main_frame, "FFmpeg", Settings.util_locatior.find_ffmpeg
        )
        self.catframes = SingleCheck(
            self.main_frame, "Catframes", Settings.util_locatior.find_catframes
        )

    def _pack_widgets(self):
        self.main_frame.pack(expand=True, padx=50, pady=100)
        self.pil.pack(expand=True)
        self.ffmpeg.pack(expand=True)
        self.catframes.pack(expand=True)

    def start_check(self):
        self.pil.check()
        self.ffmpeg.check()
        self.catframes.check()
        self.all_checked = \
                    self.pil.found \
                    and self.ffmpeg.found \
                    and self.catframes.found
        if self.all_checked:
            self.save_settings()
            self.after(3000, self.destroy)

    def save_settings(self):
            Settings.conf.update(
                "AbsolutePath", "FFmpeg", Settings.util_locatior.ffmpeg_full_path
            )
            Settings.conf.update(
                "SystemPath", "FFmpeg", "yes" if Settings.util_locatior.ffmpeg_in_sys_path else "no"
            )
            Settings.conf.update(
                "AbsolutePath", "Catframes", Settings.util_locatior.catframes_full_path
            )
            Settings.conf.update(
                "SystemPath", "Catframes", "yes" if Settings.util_locatior.catframes_in_sys_path else "no"
            )
            Settings.save()

    def close(self):
        if self.all_checked:
            self.destroy()
        else:
            exit()





    #  из файла tests.py:

class _TestUtils(TestCase):

    def test_shrink_path(self):
        path = r"C:\Users\Test\AppData\Local\Microsoft\WindowsApps"
        shrinked = shrink_path(path, 20)
        self.assertEqual(shrinked, r"C:\...ft\WindowsApps")

        path = r"/home/test/.config/"
        shrinked = shrink_path(path, 30)
        self.assertEqual(shrinked, path)

        path = r"/home/test/.config/gnome_shell"
        shrinked = shrink_path(path, 10)
        self.assertEqual(shrinked, r"/home/.../gnome_shell")

    def test_is_dark_color(self):
        self.assertTrue(is_dark_color(0, 0, 0))

        self.assertTrue(is_dark_color(0, 0, 255))
        self.assertTrue(is_dark_color(255, 0, 0))
        self.assertTrue(is_dark_color(255, 0, 255))

        self.assertFalse(is_dark_color(0, 255, 0))
        self.assertFalse(is_dark_color(0, 255, 255))
        self.assertFalse(is_dark_color(255, 255, 0))

        self.assertFalse(is_dark_color(255, 255, 255))
    

class _TestWindowPosition(TestCase):

    def test_coords_calculation(self):
        x, y = WindowMixin._calculate_coords((1005, 495), (550, 450), (250, 150), (2560, 1440))
        self.assertTrue((x, y) == (1155, 645)) 
        x, y = WindowMixin._calculate_coords((285, 304), (550, 450), (900, 500), (2560, 1440))
        self.assertTrue((x, y) == (110, 279)) 
        x, y = WindowMixin._calculate_coords((2240, 224), (550, 450), (900, 500), (2560, 1440))
        self.assertTrue((x, y) == (1630, 199)) 
        x, y = WindowMixin._calculate_coords((912, 1147) ,(550, 450) ,(900, 500), (2560, 1440))
        self.assertTrue((x, y) == (737, 850)) 


class _TestTaskConfig(TestCase):

    def test_task_assembling(self):
        task_config = TaskConfig()
        task_config.set_specs(30, 2)
        task_config.set_filepath("/test.webm")
        task_config.set_dirs(["/pic/test1"])

        self.assertFalse("--live-preview" in task_config.convert_to_command(True))
        self.assertTrue("--live-preview" in task_config.convert_to_command(False))

    def test_user_format_converting(self):
        test_string = '\ttest\ntest\rtest'

        res_win = TaskConfig.to_user_format(test_string, bash=False)
        self.assertTrue(res_win.startswith('"') and res_win.endswith('"'))
        self.assertTrue(r"\ttest\ntest\rtest" in res_win)

        res_bash = TaskConfig.to_user_format(test_string, bash=True)
        self.assertTrue(res_bash.startswith("'") and res_bash.endswith("'"))
        self.assertTrue(r"\ttest\ntest\rtest" in res_bash)


class _TestFieldsValidators(TestCase):

    def test_color_validator(self):
        self.assertTrue(NewTaskWindow.validate_color(""))
        self.assertTrue(NewTaskWindow.validate_color("#00ff00"))
        self.assertTrue(NewTaskWindow.validate_color("#00"))
        self.assertTrue(NewTaskWindow.validate_color("face00"))
        self.assertTrue(NewTaskWindow.validate_color("ffff"))

        self.assertFalse(NewTaskWindow.validate_color("#0000000"))
        self.assertFalse(NewTaskWindow.validate_color("##000000"))
        self.assertFalse(NewTaskWindow.validate_color("#asjmi"))
        self.assertFalse(NewTaskWindow.validate_color("000#"))

    def test_fps_validator(self):
        self.assertTrue(NewTaskWindow.validate_fps(""))
        self.assertTrue(NewTaskWindow.validate_fps("0"))
        self.assertTrue(NewTaskWindow.validate_fps("1"))
        self.assertTrue(NewTaskWindow.validate_fps("60"))

        self.assertFalse(NewTaskWindow.validate_fps(" "))
        self.assertFalse(NewTaskWindow.validate_fps("-1"))
        self.assertFalse(NewTaskWindow.validate_fps("61"))
        self.assertFalse(NewTaskWindow.validate_fps("a"))
        self.assertFalse(NewTaskWindow.validate_fps("$"))





    #  из файла main.py:

def check_utils():
    checker = UtilChecker()
    checker.mainloop()


def start_catmanager():
    root = LocalWM.open(RootWindow, "root")  # открываем главное окно
    root.mainloop()


def main():
    Settings.restore()
    if not Settings.conf.file_exists:
        check_utils()
    start_catmanager()


if __name__ == "__main__":
    main()



#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Catframes

© Георгий Устинов, 2022–2024
© Евгений Окатьев, 2024

Данное програмное обеспечение предоставляется «как есть», без каких-либо явных или подразумеваемых
гарантий. Ни в каком случае авторы не несут ответственность за любые убытки, возникшие в результате
использования данного программного обеспечения.

Неограниченному кругу лиц предоставляется разрешение на любое использование этого программного
обеспечения для любых целей, включая коммерческие приложения, а также на изменение и свободное
распространение при условии соблюдения следующих ограничений:

1. Происхождение данного программного обеспечения не должно быть искажено; вы не должны утверждать,
   что вы написали данное программное обеспечение. Если вы используете это программное обеспечение
   в продукте, упоминание авторов программного обеспечения в документации продукта не требуется,
   но приветствуется.
2. Изменённые версии исходного кода должны быть явно обозначены как таковые и не должны выдаваться
   за оригинал.
3. Данное сообщение не должно быть удалено или изменено в распространяемом исходном коде.


Зависимости
-----------

1. FFmpeg — LGPL v2.1+ или GPL v2+ `при включении GPL-компонентов <https://ffmpeg.org/legal.html>`_.
   Файлы с расширением ``mp4`` кодируются
   библиотекой `x264 <https://www.videolan.org/developers/x264.html>`_ (GPLv2),
   с расширением ``webm`` — библиотекой libvpx (3-пунктовая BSD).
2. Библиотека `Pillow <https://python-pillow.org/>`_ — пермиссивная лицензия HPND.
3. Хотя бы один поддерживаемый юникодный моноширинный TrueType-шрифт (см. код PillowFrameView).

"""

# from __future__ import annotations  # для псевдонимов в autodoc

from argparse import ArgumentParser, ArgumentTypeError, RawDescriptionHelpFormatter
from datetime import datetime
import functools
import gc
import hashlib
import itertools
import io
import json
import math
import os
from operator import itemgetter
from pathlib import Path
import platform
import random
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import textwrap
from queue import Queue, Empty, Full
from collections import deque

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Dict, Iterable, List, NamedTuple, Optional, Sequence, Tuple, Union

import base64
from time import sleep, monotonic
from unittest import TestCase

from PIL import Image, ImageColor, ImageDraw, ImageFont


__version__ = '2024.8.0'
__license__ = 'Zlib'


TITLE = f'Catframes {__version__}'

DESCRIPTION = f"""{TITLE}

  License: {__license__}

  Source code: https://github.com/georgy7/catframes

"""


class FileUtils:
    """A module of auxiliary functions related to the file system."""

    @staticmethod
    def get_checksum(path: Union[Path, None]) -> Optional[str]:
        """This function does not throw exceptions."""
        if not path:
            return None
        hashsum = hashlib.sha1()
        try:
            with path.expanduser().open(mode = 'rb') as binary:
                chunk = binary.read(4096)
                while chunk:
                    hashsum.update(chunk)
                    chunk = binary.read(4096)
            return hashsum.hexdigest()
        except OSError:
            return None

    @staticmethod
    def get_mtime(path: Union[Path, None]) -> Optional[datetime]:
        """This function does not throw exceptions."""
        if not path:
            return None
        try:
            return datetime.fromtimestamp(os.path.getmtime(path.expanduser()))
        except OSError:
            return None

    @staticmethod
    def get_file_size(path: Union[Path, None]) -> Optional[int]:
        """This function does not throw exceptions."""
        if not path:
            return None
        try:
            normal_path = path.expanduser()
            if normal_path.is_file():
                return os.path.getsize(normal_path)
            return None
        except OSError:
            return None

    @staticmethod
    def is_symlink(path: Union[Path, None]) -> bool:
        """This function does not throw exceptions."""
        if not path:
            return False
        return path.expanduser().is_symlink()

    @staticmethod
    def tail(file_path, line_count):
        """Retuns at the most n last lines of a file, or empty string."""
        result = deque(maxlen = line_count)
        try:
            with file_path.open(mode='r') as f:
                for line in f:
                    result.append(line)
        except OSError:
            pass
        return '\n'.join([x.rstrip() for x in result])

    @staticmethod
    def list_images(path: Path) -> List[Path]:
        """Набор файлов JPEG и PNG в порядке, предоставляемом pathlib (не определён в документации
        и, скорее всего, зависит от операционной системы). Файлы определяются по расширениям
        (суффиксам имён). Вложенные папки игнорируются.

        :raises ValueError: путь – не директория, доступная на просмотр (подробности в сообщении).
        :raises OSError: что-то, что не было предусмотрено.
        """
        folder = path.expanduser()

        frame_extensions = "jpg", "jpeg", "png", "qoi", "pcx"

        try:
            # Поскольку здесь мы не читаем файлы,
            # все ошибки будут свидетельствовать о проблеме с папкой.
            # Если мы получим PermissionError, вызвав метод is_file(),
            # это будет значить, что скорее всего папка не даёт нам разрешения
            # узнать, чем являются её элементы.
            # Проверено в Alpine: если установить у папки права 600, получится
            # получить список, но не удасться узнать что-либо о его элементах.
            # Если же файл будет удалён прямо перед вызовом is_file(),
            # этот метод согласно документации просто вернёт False.
            return [
                file_path
                for file_path in folder.iterdir()
                if file_path.is_file()
                and file_path.suffix[1:].lower() in frame_extensions
            ]
        except FileNotFoundError:
            raise ValueError(f'The path is not a folder: {folder}')
        except NotADirectoryError:
            raise ValueError(f'The path is not a folder: {folder}')
        except PermissionError:
            raise ValueError(f'Forbidden: {folder}')

    @staticmethod
    def sort_natural(files: List[Path]):
        """В Linux также известен как version sort. Многосимвольные десятичные числа считаются
        за один символ и сортируются в зависимости от значения числа.

        Функция сортирует файлы или симлинки по именам, игнорируя их местоположения. Список
        сортируется на месте, чтобы экономить память.

        Способ сортировки имён похож на используемый в команде sort из GNU Coreutils, если
        использовать её как ``echo СПИСОК | sort -Vs``, но не совпадает полностью.
        """
        extension_pattern = re.compile(r'(\.[a-zA-Z0-9]+)+$')
        part_pattern = re.compile(r'(\D|\d+)')

        def get_max_integer(path: Path) -> int:
            parts = part_pattern.findall(path.name)
            integers = [int(x) for x in parts if x.isdigit()]
            return max(integers) if integers else 0

        max_int_value = max((get_max_integer(x) for x in files)) if files else 0

        def natural_simple(level: int, value: str) -> List[Tuple[int, int, int]]:
            result: List[Tuple[int, int, int]] = []
            parts = part_pattern.findall(value)
            for letter_or_number in parts:
                if letter_or_number.isdigit():
                    result.append((level, int(letter_or_number), 0))
                else:
                    result.append((level, max_int_value+1, ord(letter_or_number)))
            return result

        def key_function(path):
            filename = path.name
            extension_match = extension_pattern.search(filename)
            if extension_match:
                extension = extension_match[0]
                basename = filename[:-len(extension)]
            else:
                extension = ''
                basename = filename

            # Символы расширений — раньше в алфавите, значит чем короче
            # базовая часть, тем раньше файл в последовательности.
            tuples = natural_simple(1, basename)
            tuples.extend(natural_simple(0, extension))
            return functools.reduce(lambda x, y: x+y, tuples)

        files.sort(key=key_function)


class _FileUtilsTest(TestCase):
    def test_checksum(self):
        """Works like sha1sum on Linux. For folders and non-existent files, it returns None."""
        with tempfile.TemporaryDirectory() as folder_path_string:
            file_path = Path(folder_path_string) / '1.txt'
            self.assertEqual(FileUtils.get_checksum(file_path), None)

        with tempfile.TemporaryDirectory() as folder_path_string:
            folder_path = Path(folder_path_string)
            self.assertEqual(FileUtils.get_checksum(folder_path), None)

        with tempfile.TemporaryDirectory() as folder_path_string:
            file_path = Path(folder_path_string) / '1.txt'
            file_path.write_text('12345', encoding='utf-8')
            expected = '8cb2237d0679ca88db6464eac60da96345513964'
            self.assertEqual(FileUtils.get_checksum(file_path), expected)

        with tempfile.TemporaryDirectory() as folder_path_string:
            file_path = Path(folder_path_string) / '1.txt'
            file_path.write_text('.' * 20_000, encoding='utf-8')
            expected = 'c629c5d9a1e44286b80e3566f0204b6024dffef2'
            self.assertEqual(FileUtils.get_checksum(file_path), expected)

    def test_mtime(self):
        """Returns the local time of the modification, and
        if the file does not exist, returns None.
        """
        with tempfile.TemporaryDirectory() as folder_path_string:
            file_path = Path(folder_path_string) / '1.txt'
            self.assertEqual(FileUtils.get_mtime(file_path), None)

        with tempfile.TemporaryDirectory() as folder_path_string:
            file_path = Path(folder_path_string) / '1.txt'

            start = datetime.now()
            sleep(0.1)
            file_path.write_text('12345', encoding='utf-8')
            mtime = FileUtils.get_mtime(file_path)

            self.assertGreater(mtime, start)
            self.assertLess((mtime - start).seconds, 10)

    def test_file_size(self):
        """For folders and non-existent files, it returns None."""
        with tempfile.TemporaryDirectory() as folder_path_string:
            file_path = Path(folder_path_string) / '1.txt'
            self.assertEqual(FileUtils.get_file_size(file_path), None)

        with tempfile.TemporaryDirectory() as folder_path_string:
            folder_path = Path(folder_path_string)
            self.assertEqual(FileUtils.get_file_size(folder_path), None)

        with tempfile.TemporaryDirectory() as folder_path_string:
            file_path = Path(folder_path_string) / '1.txt'
            file_path.write_text('12345', encoding='utf-8')
            self.assertEqual(FileUtils.get_file_size(file_path), 5)

    def test_is_symlink(self):
        """For non-existent files, it returns False. For existing ones too."""
        with tempfile.TemporaryDirectory() as folder_path_string:
            file_path = Path(folder_path_string) / '1.txt'
            self.assertEqual(FileUtils.is_symlink(file_path), False)

        with tempfile.TemporaryDirectory() as folder_path_string:
            file_path = Path(folder_path_string) / '1.txt'
            file_path.write_text('12345', encoding='utf-8')
            self.assertEqual(FileUtils.is_symlink(file_path), False)

    def test_list_images_1(self):
        filenames = [
            '123.jpg',
            '456.JPEG',
            '__________.PNG',
            '_______________.png',
            'a b c.jpeg',
            'd e f.JPEG',
        ]
        with tempfile.TemporaryDirectory() as folder_path_string:
            for fn in filenames:
                file_path = Path(folder_path_string) / fn
                file_path.touch()

            result = FileUtils.list_images(Path(folder_path_string))
            self.assertEqual(len(result), len(filenames))

            result_filenames = [os.path.basename(x) for x in result]
            for x in result_filenames:
                self.assertIn(x, filenames)

    def test_list_images_2(self):
        filenames = [
            '123.jpg',
            '456.JPEG',
            '__________.PNG',
            '_______________.png',
            'a b c.jpeg',
            'd e f.JPEG',
            'g h i.exe',
            'a_song.wav',
            'plain.txt',
        ]
        expected = [
            '123.jpg',
            '456.JPEG',
            '__________.PNG',
            '_______________.png',
            'a b c.jpeg',
            'd e f.JPEG',
        ]
        with tempfile.TemporaryDirectory() as folder_path_string:
            for fn in filenames:
                file_path = Path(folder_path_string) / fn
                file_path.touch()

            result = FileUtils.list_images(Path(folder_path_string))
            self.assertEqual(len(result), len(expected))

            result_filenames = [os.path.basename(x) for x in result]
            for x in result_filenames:
                self.assertIn(x, expected)

    def test_list_images_of_non_existent_folder(self):
        with tempfile.TemporaryDirectory() as folder_path_string:
            fake_path = Path(folder_path_string) / 'fake'
            with self.assertRaisesRegex(ValueError, '\S+'):
                FileUtils.list_images(fake_path)

    def test_list_images_of_non_existent_parent(self):
        with tempfile.TemporaryDirectory() as folder_path_string:
            fake_path = Path(folder_path_string) / 'fake_parent' / 'a_folder'
            with self.assertRaisesRegex(ValueError, '\S+'):
                FileUtils.list_images(fake_path)

    def test_list_images_of_forbidden_folder(self):
        # on Unix-like systems
        pass # TODO

    def test_natural_sort_of_empty_list(self):
        """It must not crash when sorting empty file lists."""
        items = []
        FileUtils.sort_natural(items)
        self.assertSequenceEqual([], items)

    def test_natural_sort_of_letters(self):
        """It must not crash when there are no numbers in the filenames."""
        folder_a, folder_b = 'some_folder', 'another_folder'
        expected = [
            Path(folder_a, 'A.JPG'),
            Path(folder_b, 'B.JPG'),
            Path(folder_a, 'C.JPG'),
            Path(folder_b, 'D.JPG'),
            Path(folder_a, 'E.JPG'),
            Path(folder_b, 'F.JPEG'),
            Path(folder_a, 'G.JPG'),
        ]

        items = expected.copy()
        random.shuffle(items)

        FileUtils.sort_natural(items)
        self.assertSequenceEqual(expected, items)

    def test_natural_sort_of_digital_camera_images(self):
        """An extreme example to demonstrate."""
        folder_a, folder_b = 'some_folder', 'another_folder'
        expected = [
            Path(folder_a, 'IMG_.JPG'),
            Path(folder_b, 'IMG_00001.JPG'),
            Path(folder_a, 'IMG_075.JPG'),
            Path(folder_b, 'IMG_0670.JPG'),
            Path(folder_a, 'IMG_0671.JPG'),
            Path(folder_b, 'IMG_0672.JPEG'),
            Path(folder_a, 'IMG_0672.JPG'),
            Path(folder_a, 'IMG_0672 edited.png'),  # ord(' ') == 32
            Path(folder_b, 'IMG_0672-edited.png'),  # ord('-') == 45
            Path(folder_b, 'IMG_0672e.png'),        # ord('e') == 101
            Path(folder_a, 'IMG_0673.JPG'),
            Path(folder_b, 'IMG_0673.jpg'),
            Path(folder_a, 'IMG_0674.JPG'),
            Path(folder_b, 'IMG_0675.JPG'),
            Path(folder_a, 'IMG_A.JPG'),
        ]

        items = expected.copy()
        random.shuffle(items)

        FileUtils.sort_natural(items)
        self.assertSequenceEqual(expected, items)

    def test_natural_sort_of_iso_dates(self):
        """The example shows that leading zeros do not interfere with natural sorting."""
        folder_a, folder_b = 'some_folder', 'another_folder'
        expected = [
            Path(folder_a, '20211231T235959.jpg'),
            Path(folder_b, '20220831T060005.jpg'),
            Path(folder_a, '20220901T040013.jpg'),
            Path(folder_b, '20220901T040021.jpg'),
            Path(folder_a, '20220901T040101.jpg'),
            Path(folder_b, '20220901T041617.jpg'),
            Path(folder_a, '20220901T050002.jpg'),
            Path(folder_b, '20220901T060000.jpg'),
            Path(folder_a, '20220901T060002.jpg'),
            Path(folder_b, '20220901T060005.jpg'),
        ]

        items = expected.copy()
        random.shuffle(items)

        FileUtils.sort_natural(items)
        self.assertSequenceEqual(expected, items)

    def test_natural_sort(self):
        """The basic case for which natural sorting is designed."""
        folders = 'some_folder', 'another_folder'
        expected = []
        for i in range(1, 201):
            filename = f'frame_{i}.jpg'
            expected.append(Path(random.choice(folders), filename))

        items = expected.copy()
        random.shuffle(items)

        FileUtils.sort_natural(items)
        self.assertSequenceEqual(expected, items)


@dataclass(frozen=True)
class Resolution:
    """Non-zero size in pixels."""

    width: int
    height: int

    def __post_init__(self):
        assert self.width > 0
        assert self.height > 0

    def __str__(self):
        """Returns a string of the form `WxH". The letter X was chosen as the separator
        for compatibility reasons with most fonts and encodings.
        """
        return f'{self.width}x{self.height}'

    @property
    def ratio(self) -> float:
        """Aspect ratio. Always greater than zero."""
        return self.width / self.height


class Frame:
    """Кадр на диске. Сырьё для :class:`FrameView`. Конструктор создаёт объект, даже если путь
    ведёт в никуда. Не иммутабельная сущность, некоторые поля могут обновляться.

    :param path: Путь к файлу.

    :param banner: Кадр не является отображением никакого файла на диске, т.е. он существует
    только чтобы что-то сообщить. Соответственно, такой кадр не должен влиять ни на выбор
    разрешения, ни на подсчет кадров. Рендерится он примерно как кадры, которые были удалены
    после запуска скрипта.

    :param message: Если это кадр-заглушка (баннер), этот текст будет выведен
    где-нибудь в центре кадра.
    """
    __slots__ = '_checksum', '_path', '_resolution', '_message', 'numdir', 'numvideo'

    def __init__(self, path: Union[Path, None], banner: bool = False, message: str = ''):
        self._path = path
        self._resolution = None
        self._checksum = FileUtils.get_checksum(path)
        self._message = message

        assert (path is None) == banner
        assert (self._path is None) == banner

        # Чек-сумма может быть незаполнена не только из-за того, что путь незаполнен.
        # Сюда же относятся все ошибки доступа к содержимому.
        if self._checksum:
            assert path is not None
            try:
                with Image.open(path.expanduser()) as image:
                    width, height = image.size
                    self._resolution = Resolution(width, height)
            except OSError:
                pass

        self.numdir: int = 0
        """Каким он будет по счету в своей папке, если её содержимое отсортировать."""

        self.numvideo: int = 0
        """Каким он будет по счету, если отсортировать изображения в папках и склеить эти списки."""

    @property
    def banner(self) -> bool:
        return (self._path is None)

    @property
    def message(self) -> str:
        return self._message

    @property
    def path(self) -> Union[Path, None]:
        """Путь к файлу в директории, указанной пользователем. Может быть симлинком."""
        return self._path

    @property
    def name(self) -> str:
        """Имя файла или симлинка (для нанесения на кадр)."""
        if self.path:
            return self.path.name
        else:
            return ''

    @property
    def folder(self) -> str:
        """Имя папки с файлом (для нанесения на кадр)."""
        if self.path:
            return self.path.parent.parts[-1]
        else:
            return ''

    @property
    def checksum(self) -> Union[str, None]:
        """Незаполнено, если не удалось прочитать файл в момент создания объекта."""
        return self._checksum

    @property
    def resolution(self) -> Union[Resolution, None]:
        """Незаполнено, если не удалось прочитать файл в момент создания объекта."""
        return self._resolution


class _ResolutionTest(TestCase):
    def test_eq(self):
        """It's equality of values, not references."""
        first = Resolution(640, 480)
        second = Resolution(640, 480)
        self.assertEqual(first, second)
        self.assertFalse(first != second)

        second = Resolution(320, 240)
        self.assertNotEqual(first, second)
        self.assertFalse(first == second)

        second = Resolution(640, 481)
        self.assertNotEqual(first, second)
        self.assertFalse(first == second)


class _FrameTest(TestCase):
    CRC32_HEX_LENGTH = 8

    def test_path_to_nowhere(self):
        """Кадр должен быть создан, даже если путь никуда не ведёт."""
        path = Path(f'{random.randint(0, sys.maxsize)}.jpg')
        frame = Frame(path)
        self.assertIsNone(frame.checksum)
        self.assertIsNone(frame.resolution)
        self.assertEqual(frame.name, path.name)

    def test_not_image(self):
        """Кадр должен быть создан, даже если картинка не читается."""
        with tempfile.TemporaryDirectory() as folder_path_string:
            folder_path = Path(folder_path_string)
            path = folder_path / '1.jpg'
            path.write_text('12345', encoding='utf-8')
            frame = Frame(path)
            self.assertIsInstance(frame.checksum, str)
            self.assertTrue(len(frame.checksum) >= self.CRC32_HEX_LENGTH)
            self.assertIsNone(frame.resolution)
            self.assertEqual(frame.name, path.name)

    def test_jpeg(self):
        """Проверяется заполнение конструктором основных свойств кадра."""
        width = random.randint(10, 1920)
        height = random.randint(10, 1080)
        with tempfile.TemporaryDirectory() as folder_path_string:
            folder_path = Path(folder_path_string)
            path = folder_path / '1.jpg'

            image = Image.new("RGB", (width, height))
            image.save(path)

            frame = Frame(path)
            self.assertIsInstance(frame.checksum, str)
            self.assertTrue(len(frame.checksum) >= self.CRC32_HEX_LENGTH)
            self.assertEqual(frame.resolution.width, width)
            self.assertEqual(frame.resolution.height, height)
            self.assertEqual(frame.name, path.name)
            self.assertEqual(frame.folder, folder_path.parts[-1])

    def test_root_folder(self):
        """Свойство folder не должно падать, когда кадр находится в корне файловой системы."""
        root_dir = Path(Path().resolve().parts[0])
        frame = Frame(root_dir / 'qwe.png')
        self.assertTrue(isinstance(frame.folder, str))


class ResolutionUtils:
    """Useful functions related to resolution."""

    @staticmethod
    def round(value: float) -> int:
        """There are always encoders that can't handle odd frame side sizes."""
        return math.floor(value/2)*2

    @staticmethod
    def get_scale_size(src: Resolution, goal: Resolution) -> Optional[Resolution]:
        """Changes the resolution proportionally so that the source fits into the goal resolution
        without gap. A returned None means a recommendation to crop the image instead of scaling,
        or a signal that it already fits perfectly.
        Going out of bounds by one pixel does not count: cropping will be applied later.
        Cropping an odd pixel instead of zooming out entire frame reduces the loss of sharpness.
        """
        should_zoom_out = \
            (src.width > goal.width + 1) or \
            (src.height > goal.height + 1)

        should_zoom_in = (src.width < goal.width) and (src.height < goal.height)

        should_scale = should_zoom_in or should_zoom_out

        if should_scale:
            scale = goal.width / src.width if src.ratio >= goal.ratio \
                else goal.height / src.height
            return Resolution(
                round(scale * src.width),
                round(scale * src.height))
        return None

    @staticmethod
    def get_crop_size(src: Resolution, goal: Resolution) -> Resolution:
        """It should be used only if :meth:`get_scale_size` returned None."""
        width = src.width if src.width < goal.width else goal.width
        height = src.height if src.height < goal.height else goal.height
        return Resolution(width, height)


class ResolutionStatistics:
    """Знает, какие разрешения как часто используются."""
    __slots__ = ('_table',)

    def __init__(self, frames: Sequence[Frame]):
        self._table: Dict[Resolution, int] = {}
        for frame in frames:
            if frame.resolution in self._table:
                self._table[frame.resolution] += 1
            elif isinstance(frame.resolution, Resolution):
                self._table[frame.resolution] = 1

    def sort_by_count_desc(self) -> Sequence[Tuple[Resolution, int]]:
        """Возвращает разрешения в порядке убывания числа кадров."""
        return sorted(self._table.items(), key=itemgetter(1), reverse=True)

    def choose(self) -> Resolution:
        """Решает, какое разрешение лучше использовать для видео.

        Совмещает самую частую ширину и самую частую высоту, которые не меньше, чем средние этих
        показателей. Если есть несколько значений ширины или высоты с одинаковой частотой,
        выбираются максимальные числа.

        Если соотношение сторон непостоянно, этот метод приведёт к добавлению полей, возможно,
        на всех кадрах, но почти все кадры впишутся в итоговое разрешение без снижения качества.

        Пример:

        ======= ======= ===================
        Ширина  Высота  Количество кадров
        ======= ======= ===================
        1280    720     3000
        800     800     2000
        ======= ======= ===================

        Поскольку

        - средневзвешенная ширина равна 1088,
        - средневзвешенная высота — 752,
        - 800 меньше 1088,
        - 720 меньше 752,

        выбрано может быть только разрешение 1280×800.

        У кадров 800×800 появятся поля по бокам, у кадров 1280×720 — сверху и снизу.
        """
        def find(xw_list: List[Tuple[int, int]]) -> int:
            total_value = sum(a[0] * a[1] for a in xw_list)
            total_weight = sum(a[1] for a in xw_list)
            weighted_average = total_value / total_weight

            filtered = [xw for xw in xw_list if xw[0] >= weighted_average]

            # Здесь могут дублироваться значения, т.к. может быть
            # много разрешений с одинаковой шириной или с одинаковой высотой.
            # Нужно просуммировать количества в таких повторах.
            
            xmap: Dict[int, int] = {}
            for xw in filtered:
                if xw[0] in xmap:
                    xmap[xw[0]] += xw[1]
                else:
                    xmap[xw[0]] = xw[1]

            distinct = xmap.items()
            max_weight = max(xw[1] for xw in distinct)

            most_frequent = list(xw for xw in distinct if xw[1] == max_weight)
            return round(max(xw[0] for xw in most_frequent))

        def find_other_axis(x, keys: List[int], values: List[int], count: List[int]) -> int:
            indices = [i for i, k in enumerate(keys) if k == x]
            values2 = [v for i, v in enumerate(values) if i in indices]
            count2 = [c for i, c in enumerate(count) if i in indices]
            return ResolutionUtils.round(find(list(zip(values2, count2))))

        if len(self._table) < 1:
            return Resolution(1280, 720)

        res_list, count = zip(*self._table.items())
        width = [resolution.width for resolution in res_list]
        height = [resolution.height for resolution in res_list]

        raw_result = Resolution(
                find(list(zip(width, count))),
                find(list(zip(height, count))))

        result = Resolution(
                ResolutionUtils.round(raw_result.width),
                ResolutionUtils.round(raw_result.height))

        alternatives = []

        if result.height < ResolutionUtils.round(find_other_axis(raw_result.width, width, height, list(count))):
            alternatives.append(Resolution(
                result.width,
                ResolutionUtils.round(find_other_axis(result.width, width, height, list(count)))
            ))

        if result.width < ResolutionUtils.round(find_other_axis(raw_result.height, height, width, list(count))):
            alternatives.append(Resolution(
                ResolutionUtils.round(find_other_axis(result.height, height, width, list(count))),
                result.height
            ))

        if len(alternatives) == 1:
            return alternatives[0]
        elif len(alternatives) > 1:
            alternatives.sort(key=lambda x: x.width*x.height, reverse=True)
            return alternatives[0]

        return result


class _ResolutionStatisticsTest(TestCase):
    def test_simple_1(self):
        with tempfile.TemporaryDirectory() as folder_path_string:
            folder_path = Path(folder_path_string)
            file_1 = folder_path / '1.jpg'
            file_2 = folder_path / '2.jpg'
            Image.new("RGB", (1280, 720)).save(file_1)
            Image.new("RGB", (800, 800)).save(file_2)

            frame_1 = Frame(file_1)
            frame_2 = Frame(file_2)

            frames = [frame_1] * 3000 + [frame_2] * 2000
            resolution_table = ResolutionStatistics(frames)
            lines = [x for x in resolution_table.sort_by_count_desc()]
            self.assertEqual(2, len(lines))

            resolution = resolution_table.choose()
            self.assertEqual(str(Resolution(1280, 800)), str(resolution))

    def test_simple_2(self):
        with tempfile.TemporaryDirectory() as folder_path_string:
            folder_path = Path(folder_path_string)
            file_1 = folder_path / '1.jpg'
            file_2 = folder_path / '2.jpg'
            Image.new("RGB", (720, 1280)).save(file_1)
            Image.new("RGB", (800, 800)).save(file_2)

            frame_1 = Frame(file_1)
            frame_2 = Frame(file_2)

            frames = [frame_1] * 3000 + [frame_2] * 2000
            resolution_table = ResolutionStatistics(frames)
            lines = [x for x in resolution_table.sort_by_count_desc()]
            self.assertEqual(2, len(lines))

            resolution = resolution_table.choose()
            self.assertEqual(str(Resolution(800, 1280)), str(resolution))

    def test_simple_3(self):
        with tempfile.TemporaryDirectory() as folder_path_string:
            folder_path = Path(folder_path_string)
            frames = []

            def make_frame(i, w, h):
                file = folder_path / (str(i) + '.jpg')
                Image.new("RGB", (w, h)).save(file)
                return Frame(file)

            frames.append(make_frame( 1, 1280,  720))
            frames.append(make_frame( 2, 1280,  640))
            frames.append(make_frame( 3,  800,  600))
            frames.append(make_frame( 4, 1024,  768))
            frames.append(make_frame( 5,  640,  480))

            frames.append(make_frame( 6,  720, 1280))
            frames.append(make_frame( 7, 1440, 1080))
            frames.append(make_frame( 8, 1440, 1080))
            frames.append(make_frame( 9, 1280,  960))
            frames.append(make_frame(10, 1280,  960))

            frames.append(make_frame(11, 1280,  960))
            frames.append(make_frame(12,  800,  600))
            frames.append(make_frame(13,  800,  600))
            frames.append(make_frame(14,  800,  600))

            resolution_table = ResolutionStatistics(frames)
            resolution = resolution_table.choose()
            self.assertEqual(str(Resolution(1280, 960)), str(resolution))

    def test_simple_4(self):
        with tempfile.TemporaryDirectory() as folder_path_string:
            folder_path = Path(folder_path_string)
            frames = []

            def make_frame(i, w, h):
                file = folder_path / (str(i) + '.jpg')
                Image.new("RGB", (w, h)).save(file)
                return Frame(file)

            frame = make_frame(1, 1280, 720)
            for i in range(98):
                frames.append(frame)

            frame = make_frame(2, 1920, 1080)
            for i in range(69):
                frames.append(frame)

            frame = make_frame(3, 1280, 960)
            for i in range(57):
                frames.append(frame)

            frame = make_frame(4, 1280, 640)
            for i in range(30):
                frames.append(frame)

            frame = make_frame(5, 1440, 1080)
            for i in range(30):
                frames.append(frame)

            frame = make_frame(6, 800, 600)
            for i in range(14):
                frames.append(frame)

            frame = make_frame(7, 4096, 2160)
            for i in range(14):
                frames.append(frame)

            frame = make_frame(8, 852, 480)
            for i in range(8):
                frames.append(frame)

            resolution_table = ResolutionStatistics(frames)
            resolution = resolution_table.choose()
            self.assertEqual(str(Resolution(1920, 1080)), str(resolution))

    def test_simple_5_even_even(self):
        with tempfile.TemporaryDirectory() as folder_path_string:
            folder_path = Path(folder_path_string)
            file_1 = folder_path / '1.jpg'
            file_2 = folder_path / '2.jpg'
            Image.new("RGB", (1024, 768)).save(file_1)
            Image.new("RGB", (1024, 768)).save(file_2)

            frame_1 = Frame(file_1)
            frame_2 = Frame(file_2)

            frames = [frame_1] + [frame_2]

            resolution_table = ResolutionStatistics(frames)
            lines = [x for x in resolution_table.sort_by_count_desc()]
            self.assertEqual(1, len(lines))

            resolution = resolution_table.choose()
            self.assertEqual(str(Resolution(1024, 768)), str(resolution))

    def test_simple_5_odd_even(self):
        with tempfile.TemporaryDirectory() as folder_path_string:
            folder_path = Path(folder_path_string)
            file_1 = folder_path / '1.jpg'
            file_2 = folder_path / '2.jpg'
            Image.new("RGB", (1023, 768)).save(file_1)
            Image.new("RGB", (1023, 768)).save(file_2)

            frame_1 = Frame(file_1)
            frame_2 = Frame(file_2)

            frames = [frame_1] + [frame_2]

            resolution_table = ResolutionStatistics(frames)
            lines = [x for x in resolution_table.sort_by_count_desc()]
            self.assertEqual(1, len(lines))

            resolution = resolution_table.choose()
            self.assertEqual(str(Resolution(
                ResolutionUtils.round(1023),
                ResolutionUtils.round(768)
            )), str(resolution))

    def test_simple_5_even_odd(self):
        with tempfile.TemporaryDirectory() as folder_path_string:
            folder_path = Path(folder_path_string)
            file_1 = folder_path / '1.jpg'
            file_2 = folder_path / '2.jpg'
            Image.new("RGB", (1024, 767)).save(file_1)
            Image.new("RGB", (1024, 767)).save(file_2)

            frame_1 = Frame(file_1)
            frame_2 = Frame(file_2)

            frames = [frame_1] + [frame_2]

            resolution_table = ResolutionStatistics(frames)
            lines = [x for x in resolution_table.sort_by_count_desc()]
            self.assertEqual(1, len(lines))

            resolution = resolution_table.choose()
            self.assertEqual(str(Resolution(
                ResolutionUtils.round(1024),
                ResolutionUtils.round(767)
            )), str(resolution))

    def test_simple_5_odd_odd(self):
        with tempfile.TemporaryDirectory() as folder_path_string:
            folder_path = Path(folder_path_string)
            file_1 = folder_path / '1.jpg'
            file_2 = folder_path / '2.jpg'
            Image.new("RGB", (1023, 767)).save(file_1)
            Image.new("RGB", (1023, 767)).save(file_2)

            frame_1 = Frame(file_1)
            frame_2 = Frame(file_2)

            frames = [frame_1] + [frame_2]

            resolution_table = ResolutionStatistics(frames)
            lines = [x for x in resolution_table.sort_by_count_desc()]
            self.assertEqual(1, len(lines))

            resolution = resolution_table.choose()
            self.assertEqual(str(Resolution(
                ResolutionUtils.round(1023),
                ResolutionUtils.round(767)
            )), str(resolution))

    def test_simple_6(self):
        with tempfile.TemporaryDirectory() as folder_path_string:
            folder_path = Path(folder_path_string)
            file_1 = folder_path / '1.jpg'
            file_2 = folder_path / '2.jpg'
            Image.new("RGB", (720, 1280)).save(file_1)
            Image.new("RGB", (799, 799)).save(file_2)

            frame_1 = Frame(file_1)
            frame_2 = Frame(file_2)

            frames = [frame_1] * 3000 + [frame_2] * 2000
            resolution_table = ResolutionStatistics(frames)
            lines = [x for x in resolution_table.sort_by_count_desc()]
            self.assertEqual(2, len(lines))

            resolution = resolution_table.choose()
            self.assertEqual(
                str(Resolution(ResolutionUtils.round(799), 1280)),
                str(resolution))

    def test_empty(self):
        resolution_table = ResolutionStatistics([])
        lines = [x for x in resolution_table.sort_by_count_desc()]
        self.assertEqual(0, len(lines))

        resolution = resolution_table.choose()
        # Default resolution: HD, 720p
        self.assertEqual(str(Resolution(1280, 720)), str(resolution))

    def test_mixed(self):
        """К простому набору кадров подмешиваются
        кадры-заглушки, которые должны быть проигнорированы.
        """
        with tempfile.TemporaryDirectory() as folder_path_string:
            folder_path = Path(folder_path_string)
            file_1 = folder_path / '1.jpg'
            file_2 = folder_path / '2.jpg'
            Image.new("RGB", (1280, 720)).save(file_1)
            Image.new("RGB", (800, 800)).save(file_2)

            frame_1 = Frame(file_1)
            frame_2 = Frame(file_2)
            banner_1 = Frame(None, True, 'Message 1')
            banner_2 = Frame(None, True, 'Message 2')

            frames = [banner_1] * 20 + \
                [frame_1] * 3000 + \
                [banner_2] * 60 + \
                [frame_2] * 2000

            resolution_table = ResolutionStatistics(frames)
            lines = [x for x in resolution_table.sort_by_count_desc()]
            self.assertEqual(2, len(lines))

            resolution = resolution_table.choose()
            self.assertEqual(str(Resolution(1280, 800)), str(resolution))

    def test_banners_only(self):
        """Если на входе только кадры-заглушки, результат
        аналогичен пустому набору кадров (HD).
        """
        banner_1 = Frame(None, True, 'Message 1')
        banner_2 = Frame(None, True, 'Message 2')

        frames = [banner_1] * 3000 + [banner_2] * 2000

        resolution_table = ResolutionStatistics(frames)
        lines = [x for x in resolution_table.sort_by_count_desc()]
        self.assertEqual(0, len(lines))

        resolution = resolution_table.choose()
        # Default resolution: HD, 720p
        self.assertEqual(str(Resolution(1280, 720)), str(resolution))

    def test_hard_choice_1(self):
        # Обнаружилось, что в некоторых случаях предложенный ранее
        # алгоритм даёт глупые решения. Рассмотрим этот случай.
        #
        # 1056x592 => 12
        # 800x592 => 6
        # 1280x718 => 6
        # 1280x640 => 6
        # 856x480 => 6
        #
        # Решение, если мы ищем ширину и высоту отдельно,
        # как самые частые значения, большие или равные
        # среднему взвешенному: 1056x718.
        #
        # Однако, если мы уже выбрали ширину 1056, разрешения с большей
        # шириной будут уменьшены, чтобы быть вписанными в него,
        # так что высота 718 просто никак не будет задействована.
        #
        # Если мы пропорционально уменьшим широкие кадры, получится следующее.
        #
        # 1056x592 => 12
        # 800x592 => 6
        # 1056x592 => 6
        # 1056x528 => 6
        # 856x480 => 6
        #
        # Внезапно оказывается, что самое частое вертикальное разрешение здесь -
        # 592, которое также очевидно выше среднего взвешенного.
        #
        # Мы также можем зайти с другой стороны.
        # Если мы определились с высотой, можно найти средневзвешенную ширину,
        # соответствующую этой высоте.
        # И тогда, если выбранная ранее ширина ниже этого числа,
        # поменять решение о ширине, найдя всё так же
        # самую частую ширину выше или равную средней взвешенной ширине
        # из соответствующих данной высоте.
        # Тогда выбор очевиден: 1280x718.
        #
        # Разница не в приоритете ширины или высоты (вопрос второстепенный),
        # а в том, приводит корректировка к увеличению
        # или к уменьшению разрешения.
        # Я склоняюсь ко второму варианту, хоть логика и будет чуть сложнее.
        with tempfile.TemporaryDirectory() as folder_path_string:
            folder_path = Path(folder_path_string)
            file = folder_path / '1.jpg'
            frames = []
            for i in range(36):
                if i < 12:
                    Image.new("RGB", (1056, 592)).save(file)
                elif i < 12+6:
                    Image.new("RGB", (800, 592)).save(file)
                elif i < 12+6+6:
                    Image.new("RGB", (1280, 718)).save(file)
                elif i < 12+6+6+6:
                    Image.new("RGB", (1280, 640)).save(file)
                elif i < 12+6+6+6+6:
                    Image.new("RGB", (856, 480)).save(file)

                frames.append(Frame(file))

            resolution_table = ResolutionStatistics(frames)
            lines = [x for x in resolution_table.sort_by_count_desc()]
            self.assertEqual(5, len(lines))

            resolution = resolution_table.choose()
            self.assertEqual(str(Resolution(1280, 718)), str(resolution))

    def test_hard_choice_2(self):
        # Тот же пример, просто меняем ширину и высоту местами.
        # В этом относительно простом примере поведение должно остаться неизменным.
        with tempfile.TemporaryDirectory() as folder_path_string:
            folder_path = Path(folder_path_string)
            file = folder_path / '1.jpg'
            frames = []
            for i in range(36):
                if i < 12:
                    Image.new("RGB", (592, 1056)).save(file)
                elif i < 12+6:
                    Image.new("RGB", (592, 800)).save(file)
                elif i < 12+6+6:
                    Image.new("RGB", (718, 1280)).save(file)
                elif i < 12+6+6+6:
                    Image.new("RGB", (640, 1280)).save(file)
                elif i < 12+6+6+6+6:
                    Image.new("RGB", (480, 856)).save(file)

                frames.append(Frame(file))

            resolution_table = ResolutionStatistics(frames)
            lines = [x for x in resolution_table.sort_by_count_desc()]
            self.assertEqual(5, len(lines))

            resolution = resolution_table.choose()
            self.assertEqual(str(Resolution(718, 1280)), str(resolution))

    def test_hard_choice_3(self):
        # То же самое, но есть несколько вариантов ширины у данной высоты.
        # Должна быть выбрана самая частая больше или равная средней взвешенной.
        with tempfile.TemporaryDirectory() as folder_path_string:
            folder_path = Path(folder_path_string)
            frames = []

            counter = 1

            def get_next_file():
                nonlocal counter
                return folder_path / (str(counter) + '.jpg');

            def save_file(file):
                nonlocal counter
                frames.append(Frame(file))
                counter += 1

            for i in range(12):
                file = get_next_file()
                Image.new("RGB", (1056, 592)).save(file)
                save_file(file)

            for i in range(6):
                file = get_next_file()
                Image.new("RGB", (800, 592)).save(file)
                save_file(file)

            for i in range(2):
                file = get_next_file()
                Image.new("RGB", (1100, 718)).save(file)
                save_file(file)
            for i in range(1):
                file = get_next_file()
                Image.new("RGB", (1150, 718)).save(file)
                save_file(file)
            for i in range(2):
                file = get_next_file()
                Image.new("RGB", (1190, 718)).save(file)
                save_file(file)
            for i in range(1):
                file = get_next_file()
                Image.new("RGB", (1400, 718)).save(file)
                save_file(file)

            for i in range(6):
                file = get_next_file()
                Image.new("RGB", (1280, 640)).save(file)
                save_file(file)
            for i in range(6):
                file = get_next_file()
                Image.new("RGB", (856, 480)).save(file)
                save_file(file)

            resolution_table = ResolutionStatistics(frames)
            lines = [x for x in resolution_table.sort_by_count_desc()]
            self.assertEqual(8, len(lines))

            resolution = resolution_table.choose()
            self.assertEqual(str(Resolution(1190, 718)), str(resolution))

    def test_hard_choice_4(self):
        # Ширина и высота меняются местами.
        with tempfile.TemporaryDirectory() as folder_path_string:
            folder_path = Path(folder_path_string)
            frames = []

            counter = 1

            def get_next_file():
                nonlocal counter
                return folder_path / (str(counter) + '.jpg');

            def save_file(file):
                nonlocal counter
                frames.append(Frame(file))
                counter += 1

            for i in range(12):
                file = get_next_file()
                Image.new("RGB", (592, 1056)).save(file)
                save_file(file)

            for i in range(6):
                file = get_next_file()
                Image.new("RGB", (592, 800)).save(file)
                save_file(file)

            for i in range(2):
                file = get_next_file()
                Image.new("RGB", (718, 1100)).save(file)
                save_file(file)
            for i in range(1):
                file = get_next_file()
                Image.new("RGB", (718, 1150)).save(file)
                save_file(file)
            for i in range(2):
                file = get_next_file()
                Image.new("RGB", (718, 1190)).save(file)
                save_file(file)
            for i in range(1):
                file = get_next_file()
                Image.new("RGB", (718, 1400)).save(file)
                save_file(file)

            for i in range(6):
                file = get_next_file()
                Image.new("RGB", (640, 1280)).save(file)
                save_file(file)
            for i in range(6):
                file = get_next_file()
                Image.new("RGB", (480, 856)).save(file)
                save_file(file)

            resolution_table = ResolutionStatistics(frames)
            lines = [x for x in resolution_table.sort_by_count_desc()]
            self.assertEqual(8, len(lines))

            resolution = resolution_table.choose()
            self.assertEqual(str(Resolution(718, 1190)), str(resolution))


class FrameView(ABC):
    """Appearance of a frame. It is responsible for adjusting the resolution, as well as for
    any other processing: adding inscriptions, adjusting brightness and contrast, etc.
    """
    def __init__(self, resolution: Resolution):
        self.resolution = resolution

        self.thumbnail: Queue = Queue(maxsize = 1)
        """A thread-safe channel for getting a thumbnail of a recently processed frame."""

    @abstractmethod
    def apply(self, frame: Frame) -> bytes:
        """It returns raw data in RGB24."""


class Quality(Enum):
    """Абстракция над бесконечными настройками качества FFmpeg."""

    HIGH = 'HIGH'
    """Очень высокое, но всё же с потерями. Подходит для художественных таймлапсов, где важно
    сохранить текстуру, световые переливы, зернистость камеры. Битрейт — как у JPEG 75.
    """

    MEDIUM = 'MEDIUM'
    """Подойдёт почти для любых задач. Зернистость видео пропадает, градиенты становятся чуть
    грубее, картинка может быть чуть мутнее, но детали легко узнаваемы.
    """

    POOR = 'POOR'
    """Некоторые мелкие детали становятся неразличимыми."""


class Encoder:
    def get_options(self, quality: Quality, fps: int = None) -> Sequence[str]:
        raise NotImplementedError("Subclasses should implement this method")
    
    
class H264Encoder(Encoder):
    _settings = {
        Quality.HIGH: {'crf': '1', 'pix_fmt': 'yuv444p'},
        Quality.MEDIUM: {'crf': '12', 'pix_fmt': 'yuv422p'},
        Quality.POOR: {'crf': '22', 'pix_fmt': 'yuv420p'}
    }

    def get_options(self, quality: Quality, fps: int) -> Sequence[str]:
        settings = self._settings[quality]
        crf = settings['crf']
        pix_fmt = settings['pix_fmt']
        if fps is not None:
            crf = round(crf + 2.3 * math.log2(60 / fps))
        return [
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-tune', 'fastdecode',
            '-movflags', '+faststart',
            '-pix_fmt', pix_fmt,
            '-crf', crf
        ]


class VP9Encoder(Encoder):
    _settings = {
        Quality.HIGH: {'crf': '3', 'pix_fmt': 'yuv444p'},
        Quality.MEDIUM: {'crf': '14', 'pix_fmt': 'yuv422p'},
        Quality.POOR: {'crf': '31', 'pix_fmt': 'yuv420p'}
    }

    def get_options(self, quality: Quality, fps: int = None) -> Sequence[str]:
        settings = self._settings[quality]
        crf = settings['crf']
        pix_fmt = settings['pix_fmt']
        return [
            '-c:v', 'libvpx-vp9',
            '-deadline', 'realtime',
            '-cpu-used', '4',
            '-pix_fmt', pix_fmt,
            '-crf', crf,
            '-b:v', '0'
        ]
        

class H264NvencEncoder(Encoder):
    _settings = {
        Quality.HIGH: {'qp': '7', 'pix_fmt': 'yuv444p'},
        Quality.MEDIUM: {'qp': '14', 'pix_fmt': 'yuv422p'},
        Quality.POOR: {'qp': '28', 'pix_fmt': 'yuv420p'}
    }

    def get_options(self, quality: Quality, fps: int = None) -> Sequence[str]:
        settings = self._settings[quality]
        qp = settings['qp']
        pix_fmt = settings['pix_fmt']
        return [
            '-c:v', 'h264_nvenc',            
            '-preset', 'fast',
            '-movflags', '+faststart',
            '-pix_fmt', pix_fmt,
            '-qp', qp
        ]
        

class H264AmfEncoder(Encoder):
    _settings = {
        Quality.HIGH: {'qp_i': '7', 'qp_p': '9'},
        Quality.MEDIUM: {'qp_i': '16', 'qp_p': '18'},
        Quality.POOR: {'qp_i': '26', 'qp_p': '27'}
    }

    def get_options(self, quality: Quality, fps: int = None) -> Sequence[str]:
        settings = self._settings[quality]
        qp_i = settings['qp_i']
        qp_p = settings['qp_p']
        return [
            '-c:v', 'h264_amf',
            '-preset', 'speed',
            '-movflags', '+faststart',
            '-pix_fmt', 'yuv420p',
            '-rc', 'cqp',
            '-qp_i', qp_i,
            '-qp_p', qp_p
        ]
        
        
class HevcNvencEncoder(Encoder):
    _settings = {
        Quality.HIGH: {'qp': '7', 'pix_fmt': 'yuv444p'},
        Quality.MEDIUM: {'qp': '14', 'pix_fmt': 'yuv422p'},
        Quality.POOR: {'qp': '28', 'pix_fmt': 'yuv420p'}
    }

    def get_options(self, quality: Quality, fps: int = None) -> Sequence[str]:
        settings = self._settings[quality]
        qp = settings['qp']
        pix_fmt = settings['pix_fmt']
        return [
            '-c:v', 'hevc_nvenc',            
            '-preset', 'fast',
            '-movflags', '+faststart',
            '-pix_fmt', pix_fmt,
            '-qp', qp
        ]


class HevcAmfEncoder(Encoder):
    _settings = {
        Quality.HIGH: {'qp_i': '7', 'qp_p': '9'},
        Quality.MEDIUM: {'qp_i': '16', 'qp_p': '18'},
        Quality.POOR: {'qp_i': '26', 'qp_p': '27'}
    }

    def get_options(self, quality: Quality, fps: int = None) -> Sequence[str]:
        settings = self._settings[quality]
        qp_i = settings['qp_i']
        qp_p = settings['qp_p']
        return [
            '-c:v', 'hevc_amf',
            '-preset', 'speed',
            '-movflags', '+faststart',
            '-pix_fmt', 'yuv420p',
            '-rc', 'cqp',
            '-qp_i', qp_i,
            '-qp_p', qp_p
        ]


class FFmpegEncoderChecker:
    def __init__(self):
        self.hardware_encoders = {
            'h264_nvenc': H264NvencEncoder,
            'h264_amf': H264AmfEncoder,
            'hevc_nvenc': HevcNvencEncoder,
            'hevc_amf': HevcAmfEncoder,
        }
        #TODO h264_qsv, hevc_qsv, h264_v4l2m2m

        self.software_encoders = {
            'libx264': H264Encoder,
            'libvpx': VP9Encoder
        }
        
        self.encoder_map = {
            '.mp4': ['h264_nvenc', 'h264_amf', 'h264_qsv', 'h264_v4l2m2m', 'hevc_nvenc', 'hevc_amf', 'libx264'],
            '.webm': ['libvpx']
        }
        """
        В encoder_map настраивается приоритетность энкодера.
        Кто первый доступный и рабочий будет, тот и будет выбран.
        """

    def check_encoders(self):
        """Возвращает список актуальных энкодеров, которые доступны в ffmpeg"""
        try:
            result = subprocess.run(['ffmpeg', '-encoders'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            encoders = result.stdout
        except FileNotFoundError:
            print("FFmpeg is not installed on this system.")
            return []

        available_encoders = []
        for line in encoders.splitlines():
            for encoder in {**self.hardware_encoders, **self.software_encoders}:
                if encoder in line:
                    available_encoders.append(encoder)
                    break
            
        return list(set(available_encoders))

    def test_encoder(self, encoder):
        """
        Принимает кодировщик в качестве аргумента, генерирует тестовый шаблон с помощью опции -f lavfi
        и color=c=black:s=1280x720:d=1 (черный экран размером 1280x720 пикселей, длительность 1 секунда),
        для кодирования тестового шаблона с использованием указанного кодировщика и отправляем вывод в /dev/null
        (или nul на Windows) с помощью опции -f null -
        """
        try:
            subprocess.run(['ffmpeg', '-y', '-f', 'lavfi', '-i', 'color=c=black:s=1280x720:d=1', '-c:v', encoder, '-f', 'null', '-'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError:
            return False

    def select_encoder(self, file_extension) -> Encoder:
        """Возвращает экземпляр класса энкодера для указанного суффикса"""
        available_encoders = self.check_encoders()
        
        for encoder in self.encoder_map[file_extension]:
            if encoder in available_encoders and self.test_encoder(encoder):
                encoder_class = {**self.hardware_encoders, **self.software_encoders}.get(encoder)
                if encoder_class:
                    return encoder_class()

        raise ValueError(f"No working encoders found for {file_extension}.")


@dataclass(frozen=True)
class OutputOptions:
    """Это опции сохранения видеозаписи. Грубо говоря, опции FFmpeg. Они не влияют ни на выбор
    разрешения, ни на обработку кадров. Ограничение длины не влияет на выбор разрешения, т.к. цель
    опции — заранее посмотреть, как будет выглядеть результат, поэтому и влияние на результат
    должно быть минимальным.
    """
    frame_rate: int
    quality: Quality
    destination: Path
    overwrite: bool
    limit_seconds: Union[int, None]
    live_preview: bool

    def __post_init__(self):
        assert 1 <= self.frame_rate <= 60
        assert isinstance(self.quality, Quality)
        assert isinstance(self.destination, Path)
        assert isinstance(self.overwrite, bool)
        if self.limit_seconds is not None:
            assert self.limit_seconds > 0

    @staticmethod
    def get_supported_suffixes() -> Sequence[str]:
        """Возвращает поддерживаемые расширения файлов."""
        return '.mp4', '.webm'

    def limit_frames(self, frames: Sequence[Frame]):
        if self.limit_seconds:
            frames = frames[:(self.limit_seconds*self.frame_rate)]
        return frames


class OutputProcessor:
    def __init__(self, options: OutputOptions):
        self._options = options
        self._encoder_checker = FFmpegEncoderChecker()
        self._exit_lock = threading.Lock()
        self._write_pixels_control: Queue = Queue(maxsize = 10)

    def _get_encoder_options(self, encoder: Encoder) -> Sequence[str]:
        return encoder.get_options(self._options.quality, self._options.frame_rate)

    def exit_threads(self):
        """To terminate all threads running in the main method in a controlled manner."""
        with self._exit_lock:
            if not self._write_pixels_control.full():
                self._write_pixels_control.put('stop', block=False)

    def make(self, view: FrameView, frames: Sequence[Frame]):

        processed_frame_count = 0
        processed_per_cent = -1

        def set_processed(count):
            nonlocal processed_frame_count
            nonlocal processed_per_cent

            last_processed = processed_per_cent

            processed_per_cent = math.floor(count / len(frames) * 100)
            processed_frame_count = count

            if last_processed < processed_per_cent:
                print(f'Progress: {processed_per_cent}%', flush=True)

        ffmpeg_options = [
            'ffmpeg', '-f', 'rawvideo', '-c:v', 'rawvideo', '-pix_fmt', 'rgb24',
            '-s', str(view.resolution),
            '-r', str(self._options.frame_rate),
            '-i', '-'
        ]
        
        suffix = self._options.destination.suffix
        selected_encoder = self._encoder_checker.select_encoder(suffix)
        
        ffmpeg_options.extend(self._get_encoder_options(selected_encoder))
        ffmpeg_options.extend([
            '-r', str(self._options.frame_rate),
            ('-y' if self._options.overwrite else '-n'),
            str(self._options.destination.expanduser())
        ])

        set_processed(0)

        with tempfile.TemporaryDirectory() as logs_path_string:
            logs_path = Path(logs_path_string)

            errors_path = logs_path / 'error.txt'
            catched = None

            process = subprocess.Popen(ffmpeg_options,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )

            write_thread_messages: Queue = Queue(maxsize = 10)

            def write_pixels(items, control_queue, pipe, progress_queue):
                def poll_for_exit_comand():
                    while not control_queue.empty():
                        control_message = control_queue.get_nowait()
                        if 'stop' == control_message:
                            return True
                    return False

                for index in range(len(items)):
                    item = items[index]

                    must_stop = poll_for_exit_comand()
                    if must_stop:
                        break

                    try:
                        pipe.write(view.apply(item))
                    except:
                        if must_stop:
                            break
                        elif poll_for_exit_comand():
                            break
                        else:
                            raise

                    if not progress_queue.full():
                        progress_queue.put(1 + index, block=False)

                pipe.close()

            input_thread = threading.Thread(
                target=write_pixels,
                args=[
                    frames,
                    self._write_pixels_control,
                    process.stdin,
                    write_thread_messages
                ],
                daemon=False
            )

            input_thread.start()

            def read_write_thread_messages():
                while not write_thread_messages.empty():
                    message = write_thread_messages.get_nowait()
                    if int == type(message):
                        set_processed(message)

            with process.stdout:
                ret_code = process.poll()
                while None == ret_code:
                    read_write_thread_messages()
                    chunk = process.stdout.read(32)

                    if self._options.live_preview and not view.thumbnail.empty():
                        print('Preview: ' + view.thumbnail.get_nowait(), flush=True)

                    # I want this code to work in Python 3.7.
                    # The operator := requires 3.8.
                    ret_code = process.poll()

                print(f'FFmpeg exited with {ret_code}.', flush=True)

                if 0 == ret_code:
                    set_processed(len(frames))
                else:
                    sys.exit(15) # == F(Fmpeg)

            input_thread.join()


class PillowFrameView(FrameView):
    """For guaranteed single-threaded rendering by the Pillow library. This allows you
    to use the same canvas multiple times without loading heap and GC.
    """
    def __init__(self, resolution: Resolution):
        super().__init__(resolution)

        self._lock = threading.Lock()

        self._image: Image.Image = Image.new('RGB', (resolution.width, resolution.height))
        """The canvas to fill with :meth:`_render`."""

        self._draw: ImageDraw.ImageDraw = ImageDraw.Draw(self._image)
        """The 2D context for drawing on this canvas."""

        self._thumbnail_time: float = monotonic()

    def _make_jpeg_base64_thumbnail(self) -> str:
        """For use with self._lock only!"""
        thumbnail_size = (80, 60)
        thumbnail = self._image.resize(
            thumbnail_size,
            resample=Image.Resampling.BICUBIC,
            reducing_gap=2.0)

        result = io.BytesIO()
        thumbnail.save(result, 'JPEG', quality=95, subsampling=0)
        return base64.b64encode(result.getvalue()).decode('utf-8')

    def apply(self, frame: Frame) -> bytes:
        with self._lock:
            self._render(frame)
            assert self._image.size[0] == self.resolution.width
            assert self._image.size[1] == self.resolution.height

            subtle_delay: float = 0.2
            it_is_time = (monotonic() - self._thumbnail_time) >= subtle_delay
            if it_is_time and not self.thumbnail.full():
                b64_thumbnail = self._make_jpeg_base64_thumbnail()
                self.thumbnail.put(b64_thumbnail, block=False)
                self._thumbnail_time = monotonic()

            return self._image.tobytes()

    @abstractmethod
    def _render(self, frame: Frame):
        """Рисует на холсте исходный кадр и что угодно поверх него. Выбрасывание исключений
        приведёт к пятисотой ошибке. FFmpeg при получении такого статуса прекращает работу, так что
        лучше делать метод устойчивым к любым проблемам.
        """

    def _clear(self, color):
        """Тип аргумента допустим любой из тех, что понимает Pillow."""
        size = (self.resolution.width, self.resolution.height)
        self._draw.rectangle([(0, 0), size], fill=color)

    def _paste(self, source: Image.Image):
        """Вписывает отмасштабированную картинку по центру поверх текущего содержимого."""

        source_resolution = Resolution(*source.size)
        scale_size = ResolutionUtils.get_scale_size(
            source_resolution, self.resolution)

        if scale_size:
            size_tuple = (scale_size.width, scale_size.height)
            scaled = source.resize(size_tuple, Image.Resampling.LANCZOS)
        elif source_resolution != self.resolution:
            crop_size = ResolutionUtils.get_crop_size(
                source_resolution, self.resolution)
            scaled = source.crop((0, 0, crop_size.width, crop_size.height))
        else:
            scaled = source

        assert scaled.size[0] <= self.resolution.width
        assert scaled.size[1] <= self.resolution.height

        assert (scaled.size[0] == self.resolution.width) or \
            (scaled.size[1] == self.resolution.height)

        position = (
            (self.resolution.width - scaled.size[0]) // 2,
            (self.resolution.height - scaled.size[1]) // 2)

        if scaled.mode == 'RGBA':
            alpha = scaled.getchannel(3)
            self._image.paste(scaled, position, mask=alpha)
        else:
            self._image.paste(scaled, position)

    def _find_font(self, size: int) -> ImageFont.FreeTypeFont:
        """Ищет в системе что-нибудь из популярных юникодных моноширинных TrueType-шрифтов.

        В документации Pillow сказано, что файлы TrueType-шрифтов могут оставаться открытыми всё
        время существования объекта шрифта. Вроде бы, это не страшно, ведь файл открывается
        на чтение, но в Windows есть лимит одновременно открытых программой файлов, поэтому, думаю,
        лучше использовать один объект для обработки всех кадров.

        :returns: первый попавшийся шрифт.
        :raises ValueError: ни один из ожидаемых шрифтов не найден.
        """
        popular_fonts = [
            'DejaVuSansMono.ttf',
            'DroidSansMono.ttf',
            'LiberationMono-Regular.ttf',
            'UbuntuMono-R.ttf',
            'cour.ttf',
            'arial.ttf'
        ]

        for filename in popular_fonts:
            try:
                result = ImageFont.truetype(font=filename, size=size)
                print(f'{filename}: yes', flush=True)
                return result
            except OSError:
                print(f'{filename}: no', flush=True)

        raise ValueError('Could not find any font.')


@dataclass(frozen=True)
class OverlayModel:
    """Вся информация, которая может быть использована в оверлеях. Она для всех оверлеев кадра
    одинаковая, так что подготавливается один раз перед отрисовкой кадра.
    """

    warning: str
    """Как правило это пустая строка. Задача этого поля — сообщать пользователю об очень-очень
    странных вещах вроде подмены кадра на диске прямо перед встраиванием в видео. Если сюда что-то
    записано, значит это серьёзно, но это не значит, что нужно останавливать сжатие. Напротив,
    об инциденте нужно рассказать всем.

    Не заполняется, когда картинку не удалось открыть: вместо картинки будет показана одноцветная
    заглушка с названием ошибки по центру. Оверлеи будут нанесены на эту заглушку как обычно.
    """
    filename: str
    """Имя файла целиком, без пути."""
    foldername: str
    """Только имя папки, где кадр находится непосредственно."""

    symlink: bool
    """Является ли файл симлинком в данный момент."""

    mtime: Union[datetime, None]
    """Местное время последнего изменения файла на текущий момент.

    Не заполняется, если файла не оказалось на диске.
    """

    size: Union[int, None]
    """Размер файла в байтах на текущий момент.

    Не заполняется, если файла не оказалось на диске.
    """

    resolution: Union[Resolution, None]
    """Исходное разрешение кадра на текущий момент.

    Не заполняется, если файла нет или его не удалось открыть.
    """

    numdir: int
    """Номер кадра в директории, начиная с единицы."""

    numvideo: int
    """Номер кадра в итоговом видео, начиная с единицы."""

    vtime: datetime
    """Приблизительное местное время создания видео."""
    machine: str
    """Типа машины, накотором создаётся видео. Пустая строка, если не удаётся определить."""
    node: str
    """Сетевое имя компьютера, где создаётся видео. Пустая строка, если не удаётся определить."""

    def __post_init__(self):
        assert isinstance(self.filename, str)
        assert isinstance(self.foldername, str)
        assert isinstance(self.numdir, int)
        assert isinstance(self.numvideo, int)
        assert isinstance(self.vtime, datetime)
        assert isinstance(self.machine, str)
        assert isinstance(self.node, str)


OverlayTemplate = Callable[[OverlayModel], str]
"""Скомпилированный в функцию шаблон, по которому формируется текст оверлея."""


class Layout:
    """Кадр как таблица три-на-три. Назначаемые пользователем оверлеи располагаются в боковых
    ячейках, выровненные в сторону края. Отсчёт индексов ячеек ведётся от левого верхнего угла.
    Центр занять нельзя по очевидным причинам.
    """
    __slots__ = ('_cells',)

    def __init__(self):
        self._cells = [None] * 9

    @staticmethod
    def _get_position(xpos: int, ypos: int):
        assert 0 <= xpos <= 2
        assert 0 <= ypos <= 2
        assert not xpos*ypos == 1
        return 3*ypos + xpos

    def put(self, xpos: int, ypos: int, overlay: OverlayTemplate):
        """Установить в ячейку шаблон оверлея.

        :raises ValueError: ячейка уже занята.
        """
        position = self._get_position(xpos, ypos)

        if self._cells[position] is not None:
            raise ValueError(f'More than one overlay is specified for [x={xpos}, y={ypos}].')

        self._cells[position] = overlay

    def get(self, xpos: int, ypos: int) -> Optional[OverlayTemplate]:
        """Получить шаблон."""
        return self._cells[self._get_position(xpos, ypos)]

    def __len__(self):
        return len([x for x in self._cells if x])


class DefaultFrameView(PillowFrameView):
    """Масштабирует, добавляет поля при необходимости, накладывает текстовые индикаторы, а если
    файл внезапно стал недоступен, создаёт красный кадр-заглушку с названием ошибки по центру.

    :raises ValueError: ошибки в параметрах или в системе не найден шрифт.
    """
    ERROR_BG = ImageColor.getrgb('#ac4949')
    ERROR_TEXT = ImageColor.getrgb('#fff')

    FONT_SIZE: int = 12
    LINE_HEIGHT: int = 16
    TEXT_STROKE_WIDTH: int = 2

    def __init__(self, resolution: Resolution, margin_color: str, layout: Layout):
        super().__init__(resolution)
        self.overlay_font = self._find_font(self.FONT_SIZE)
        self.margin_color = ImageColor.getrgb(margin_color)
        self.layout = layout

        self.vtime = datetime.now()
        self.machine = platform.machine()
        self.network_name = platform.node()
        self.message_text_wrapper = textwrap.TextWrapper(width=70)

    def _make_overlay_model(self, frame: Frame, source_size: Tuple[int, int]) -> OverlayModel:
        file_checksum = FileUtils.get_checksum(frame.path)
        if file_checksum == frame.checksum:
            warning = ''
        elif file_checksum == None:
            warning = f'{frame.folder}/{frame.name}\nНе удалось определить хеш-сумму.'
        else:
            warning = f'{frame.folder}/{frame.name}\nХеш-сумма изменилась!'

        return OverlayModel(
            warning=warning,
            filename=frame.name,
            foldername=frame.folder,
            symlink=FileUtils.is_symlink(frame.path),
            mtime=FileUtils.get_mtime(frame.path),
            size=FileUtils.get_file_size(frame.path),
            resolution=Resolution(source_size[0], source_size[1]),
            numdir=frame.numdir,
            numvideo=frame.numvideo,
            vtime=self.vtime,
            machine=self.machine,
            node=self.network_name)

    def _get_overlay_anchor(self, xpos: int, ypos: int) -> str:
        return 'lmr'[xpos] + 'amd'[ypos]

    def _get_line_position(self,
            xpos: int, ypos: int,
            line_index: int, total_lines: int) -> Tuple[int, int]:
        top, right, bottom, left = 0, 2, 1, 2
        x_variants = left, (self.resolution.width // 2), (self.resolution.width - 1 - right)
        y_variants = top, (self.resolution.height // 2), (self.resolution.height - 1 - bottom)

        origin = (x_variants[xpos], y_variants[ypos])

        assert self.LINE_HEIGHT > 0
        assert line_index >= 0
        assert line_index < total_lines

        min_y, max_y = 0, self.resolution.height-1

        if ypos == 0:
            index = line_index
            return origin[0], min(max_y, origin[1] + index * self.LINE_HEIGHT)
        elif ypos == 2:
            index = total_lines - 1 - line_index
            return origin[0], max(min_y, origin[1] - index * self.LINE_HEIGHT)
        else:
            index = line_index - (total_lines // 2)
            unbounded = origin[1] + index * self.LINE_HEIGHT
            if total_lines % 2 == 0:
                unbounded += self.LINE_HEIGHT // 2
            return origin[0], max(min_y, min(max_y, unbounded))

    def _draw_multiline(self, xpos: int, ypos: int, text: str, stroke_color_src, fill_color_src):
        lines = text.split('\n')
        for line_index, line in enumerate(lines):
            line_position = self._get_line_position(xpos, ypos, line_index, len(lines))

            stroke_color = stroke_color_src(line_position)

            bounding_box = self._draw.textbbox(
                line_position, line,
                anchor=self._get_overlay_anchor(xpos, ypos),
                font=self.overlay_font,
                stroke_width=self.TEXT_STROKE_WIDTH)

            self._draw.rectangle(bounding_box, fill=stroke_color)
            self._draw.text(
                line_position, line,
                anchor=self._get_overlay_anchor(xpos, ypos),
                font=self.overlay_font,
                stroke_width=self.TEXT_STROKE_WIDTH,
                stroke_fill=stroke_color,
                fill=fill_color_src(line_position))

    def _wrap(self, text):
        return '\n'.join(self.message_text_wrapper.wrap(text))

    def _render(self, frame: Frame):
        overlay_model: Union[OverlayModel, None] = None

        if frame.banner:
            self._clear(self.ERROR_BG)
            self._draw_multiline(
                1, 1,
                self._wrap(frame.message),
                lambda _: self.ERROR_BG,
                lambda _: self.ERROR_TEXT)
            return

        # (frame.path is None) == frame.banner
        assert frame.path is not None

        try:
            with Image.open(frame.path) as source:
                overlay_model = self._make_overlay_model(frame, source.size)
                self._clear(self.margin_color)
                self._paste(source)
        except OSError as image_open_error:
            self._clear(self.ERROR_BG)
            self._draw_multiline(
                1, 1,
                self._wrap(f'{frame.folder}/{frame.name}\n{image_open_error.__class__.__name__}'),
                lambda _: self.ERROR_BG,
                lambda _: self.ERROR_TEXT)

        if overlay_model:
            thumbnail_size = \
                math.ceil(self.resolution.width / self.LINE_HEIGHT), \
                math.ceil(self.resolution.height / self.LINE_HEIGHT)

            thumbnail = self._image.resize(
                thumbnail_size,
                resample=Image.Resampling.BICUBIC,
                reducing_gap=2.0)

            bg_rgb = thumbnail.convert('RGB').load()
            bg_brightness = thumbnail.convert('L').load()

            def get_text_stroke_color(line_position):
                bg_x = min(thumbnail_size[0]-1, line_position[0] // self.LINE_HEIGHT)
                bg_y = min(thumbnail_size[1]-1, line_position[1] // self.LINE_HEIGHT)
                return bg_rgb[bg_x, bg_y]

            def get_text_fill_color(line_position):
                bg_x = min(thumbnail_size[0]-1, line_position[0] // self.LINE_HEIGHT)
                bg_y = min(thumbnail_size[1]-1, line_position[1] // self.LINE_HEIGHT)
                return '#fff' if bg_brightness[bg_x, bg_y] < 127 else '#000'

            for xpos, ypos in itertools.product(range(3), range(3)):
                if xpos == ypos == 1:
                    continue

                template = self.layout.get(xpos, ypos)
                if template:
                    self._draw_multiline(
                        xpos, ypos,
                        template(overlay_model),
                        get_text_stroke_color,
                        get_text_fill_color)


class _DefaultFrameViewTest(TestCase):
    def test_alpha_blending(self):
        """Цвет полей должен быть также цветом фона."""
        margin_color_string = '#ffff00'
        margin_color = ImageColor.getrgb(margin_color_string)
        image_color = ImageColor.getrgb('#00f')

        view = DefaultFrameView(Resolution(640, 480), margin_color_string, Layout())

        with tempfile.TemporaryDirectory() as folder_path_string:
            folder_path = Path(folder_path_string)

            non_transparent_path = folder_path / '1.jpg'
            non_transparent = Image.new("RGB", (400, 480), image_color)
            non_transparent.save(non_transparent_path)

            transparent_path = folder_path / '2.png'
            transparent = Image.new("RGBA", (400, 480))
            draw = ImageDraw.Draw(transparent)
            draw.ellipse([(100, 140), (300, 340)], fill=image_color)
            transparent.save(transparent_path)

            response_1: bytes = view.apply(Frame(non_transparent_path))
            response_2: bytes = view.apply(Frame(transparent_path))

        from_rgb_src = Image.frombytes(
            mode='RGB',
            size=(view.resolution.width, view.resolution.height),
            data=response_1).load()

        from_rgba_src = Image.frombytes(
            mode='RGB',
            size=(view.resolution.width, view.resolution.height),
            data=response_2).load()

        def assert_close(rgb_a, rgb_b, threshold=10):
            msg = f'{rgb_a} != {rgb_b}'
            self.assertTrue(abs(rgb_a[0] - rgb_b[0]) < threshold, msg)
            self.assertTrue(abs(rgb_a[1] - rgb_b[1]) < threshold, msg)
            self.assertTrue(abs(rgb_a[2] - rgb_b[2]) < threshold, msg)

        assert_close(margin_color, from_rgb_src[0, 0])
        assert_close(margin_color, from_rgba_src[0, 0])

        assert_close(margin_color, from_rgb_src[119, 0])
        assert_close(margin_color, from_rgba_src[119, 0])

        assert_close(image_color, from_rgb_src[120, 0])
        assert_close(margin_color, from_rgba_src[120, 0])
        assert_close(image_color, from_rgba_src[320, 240])



class OverLang:
    """Модуль разбора шаблонов оверлеев."""

    @classmethod
    def compile(cls, template: str) -> OverlayTemplate:
        """Оверлей может быть описан одним из двух способов.

        Первый способ — написать только ``WARN`` и ничего больше (любым регистром). В этом случае,
        вся эта область будет показывать предупреждение о кадре, если оно есть.

        Второй способ — использовать произвольный текст с вычисляемыми выражениями в фигурных
        скобках вида ``{[[выравнивание]ширина[!]:]функция[:аргумент]}``.

        Ширина — целое число больше нуля. Подразумевается минимальная ширина, но если добавить
        восклицательный знак, лишние символы будут отрезаны. Выравнивание может быть по левому краю
        (по-умолчанию), по правому краю (``>``) и приблизительно по центру (``^``).

        Перечень доступных функций:

        ======================= ==================================================================
        Функция                 Описание
        ======================= ==================================================================
        ``{catframes}``         Название и версия скрипта.
        ``{machine}``           Значение :py:func:`platform.machine`. Обычно это архитектура
                                процессора. Может быть пустой строкой, если не удаётся определить.
        ``{node}``              Значение :py:func:`platform.node`. Сетевое имя компьютера.
                                Может быть пустой строкой, если не удаётся определить.

        ``{vtime[:формат]}``    Приблизительно соответствует времени запуска скрипта.

                                Синтаксис формата соответствует используемому в методе
                                :py:meth:`datetime.datetime.strftime`. Если не указывать,
                                используется ISO 8601 с миллисекундами (обычно 23 символа).

        ``{fn}``                Имя кадра целиком (не обязательно всегда указывать, поскольку
                                предупреждения и ошибки обычно содержат имя файла).
        ``{dir}``               Название директории, где непосредственно находится текущий кадр.
        ``{frame:контекст}``    Номер кадра. Контекст определяет точку отсчёта.

                                Возможные значения:

                                * ``dir`` — директория;
                                * ``video`` — видеозапись;
                                * ``dirs`` — синоним ``video`` для обратной совместимости.
        ``{mtime[:формат]}``    Местное время последнего изменения кадра на диске. Пустая строка,
                                если не получается определить.

                                Синтаксис формата соответствует используемому в методе
                                :py:meth:`datetime.datetime.strftime`. Если не указывать,
                                используется ISO 8601 с миллисекундами.

        ``{size}``              Размер кадра на диске в байтах.
        ``{resolution}``        Исходное разрешение кадра.
        ``{symlink[:вид]}``     Отметка о том, что кадр является симлинком или пустая строка.
                                Вид по-умолчанию — ``symlink``.
        ======================= ==================================================================
        """
        if cls.is_warning(template):
            return lambda model: model.warning

        template = template.encode('utf8')\
            .decode("unicode_escape").encode("latin1")\
            .decode('utf8')

        parts = cls._split(template)
        functions = tuple(map(cls._compile_part, parts))

        def reverse_map(funcs, argument):
            return map(lambda f: f(argument), funcs)

        return lambda x: ''.join(reverse_map(functions, x))

    @staticmethod
    def is_warning(template: str):
        """Означает ли этот шаблон место, зарезервированное для предупреждений."""
        return 'WARN' == template.upper()

    @staticmethod
    def _split(template: str) -> Sequence[str]:
        """Разделяет шаблон оверлея на последовательность частей — строковых литералов и вызовов
        функций. Например, шаблон ``'Имя файла: {fn}'`` превратится в ``['Имя файла: ', '{fn}']``.

        :raises ValueError: нарушен синтаксис шаблона как последовательности частей (отсутствие
            ошибки не гарантирует, что синтаксис частей не нарушен).
        """
        if not re.fullmatch(r'(\{[^\{\}]+\}|[^\{\}]+)*', template):
            raise ValueError(f'There is a syntax error in "{template}".')
        return re.findall(r'(\{[^\{\}]+\}|[^\{\}]+)', template)

    @classmethod
    def _compile_part(cls, template_part: str) -> Callable[[OverlayModel], str]:
        """Обычные строки превращает в лямбды, которые выводят эти строки без изменений, а вызовы
        функций языка — в лямбды, которые формируют результат на основе :class:`OverlayModel`.

        :raises ValueError: ошибка в синтаксисе, в параметрах или в названии функции.
        """
        if not template_part.startswith('{'):
            return lambda _: template_part

        width_pattern = re.compile(r'[>^]?\d+!?')
        function_call_pattern = re.compile(r'([>^]?\d+!?:)?[a-z]+(:.+)?')

        body = template_part[1:-1]
        if not function_call_pattern.fullmatch(body):
            raise ValueError(f'There is a syntax error near "{body}".')

        function_call = body.split(':')
        assert len(function_call) >= 1

        if not width_pattern.fullmatch(function_call[0]):
            return cls._get_unformatted(function_call)

        unformatted = cls._get_unformatted(function_call[1:])
        return lambda x: cls._format(function_call[0], unformatted(x))

    @staticmethod
    def _check_datetime_format(fmt: str):
        try:
            assert isinstance(datetime.now().strftime(fmt), str)
        except Exception as exc:
            raise ValueError from exc

    @classmethod
    def _get_unformatted(cls, options) -> Callable[[OverlayModel], str]:
        config = ':'.join(options[1:]) if len(options) > 1 else ''
        func = options[0]

        if func == 'catframes':
            return lambda _: TITLE
        elif func == 'machine':
            return lambda x: x.machine
        elif func == 'node':
            return lambda x: x.node
        elif func == 'vtime':
            if config:
                cls._check_datetime_format(config)
                return lambda x: x.vtime.strftime(config)
            return lambda x: x.vtime.isoformat(timespec='milliseconds')
        elif func == 'fn':
            return lambda x: x.filename
        elif func == 'dir':
            return lambda x: x.foldername
        elif func == 'frame':
            if not config:
                raise ValueError('A context of the frame number required.')
            elif config == 'dir':
                return lambda x: str(x.numdir)
            elif config == 'dirs':
                return lambda x: str(x.numvideo)
            elif config == 'video':
                return lambda x: str(x.numvideo)
            else:
                raise ValueError(f'Bad context: "{config}".')
        elif func == 'mtime':
            if config:
                cls._check_datetime_format(config)
                return lambda x: x.mtime.strftime(config) if x.mtime else ''
            return lambda x: x.mtime.isoformat(timespec='milliseconds') if x.mtime else ''
        elif func == 'size':
            return lambda x: str(x.size)
        elif func == 'resolution':
            return lambda x: str(x.resolution)
        elif func == 'symlink':
            if config:
                return lambda x: config if x.symlink else ''
            return lambda x: 'symlink' if x.symlink else ''
        else:
            raise ValueError(f'Unsupported function "{options[0]}".')

    @staticmethod
    def _format(format_string, value) -> str:
        if not format_string:
            return value

        width_match = re.search(r'\d+', format_string)
        if not width_match:
            raise ValueError(f'Bad format "{format_string}".')

        width = int(width_match[0])
        cut = '!' in format_string
        alignment = format_string[0]

        if (alignment == '>') and not cut:
            result = f'{{0: >{width}}}'.format(value)

        elif (alignment == '>') and cut:
            result = f'{{0: >{width}}}'.format(value)[-width:]

        elif (alignment == '^') and not cut:
            result = f'{{0: ^{width}}}'.format(value)

        elif (alignment == '^') and cut:
            result = f'{{0: ^{width}}}'.format(value)
            side: float = (len(result) - width) / 2
            if len(result) > width:
                result = result[math.ceil(side):]
            if len(result) > width:
                result = result[:-math.floor(side)]

        elif not cut:
            result = f'{{0: <{width}}}'.format(value)
        else:
            result = f'{{0: <{width}}}'.format(value)[:width]

        return result


class _OverLangTest(TestCase):
    @staticmethod
    def _get_overlay_mockup(symlink: bool = False, with_mtime = True) -> OverlayModel:
        modified = datetime(2022, 9, 7, 0, 1, 23, 123000) if with_mtime else None
        return OverlayModel(
            warning='Что-то не так\nс кадром example.jpg...',
            filename='example.jpg',
            foldername='some_folder',
            symlink=symlink,
            mtime=modified,
            size=1234567,
            resolution=Resolution(640, 480),
            numdir=55,
            numvideo=520,
            vtime=datetime(2022, 9, 9, 15, 5, 54, 320000),
            machine='БК-0010',
            node='хост')

    def test_warning(self):
        """Должно работать в любом регистре."""
        model = self._get_overlay_mockup()
        view = OverLang.compile('WARN')
        self.assertEqual(model.warning, view(model))
        view = OverLang.compile('warn')
        self.assertEqual(model.warning, view(model))
        view = OverLang.compile('WaRN')
        self.assertEqual(model.warning, view(model))

    def _check_overlay(self, model: OverlayModel, template: str, value: str):
        text = 'anything 12345'

        def _compile(full_template):
            return OverLang.compile(full_template)

        view = _compile(f'{{{template}}}')
        self.assertEqual(value, view(model))

        view = _compile(f'{text} {{{template}}}')
        self.assertEqual(f'{text} {value}', view(model))
        view = _compile(f'{text}{{{template}}}')
        self.assertEqual(f'{text}{value}', view(model))

        view = _compile(f'{{{template}}} {text}')
        self.assertEqual(f'{value} {text}', view(model))
        view = _compile(f'{{{template}}}{text}')
        self.assertEqual(f'{value}{text}', view(model))

        view = _compile(f'{text}{{{template}}}{text}')
        self.assertEqual(f'{text}{value}{text}', view(model))

        # Тестируем установку минимальной ширины.

        wider = len(value) + random.randint(2, 20)

        view = _compile(f'{{{wider}:{template}}}')
        self.assertEqual(f'{{0: <{wider}}}'.format(value), view(model))
        view = _compile(f'{{{wider}!:{template}}}')
        self.assertEqual(f'{{0: <{wider}}}'.format(value), view(model))

        view = _compile(f'{{>{wider}:{template}}}')
        self.assertEqual(f'{{0: >{wider}}}'.format(value), view(model))
        view = _compile(f'{{>{wider}!:{template}}}')
        self.assertEqual(f'{{0: >{wider}}}'.format(value), view(model))

        center_margin = ' ' * ((wider - len(value)) // 2)

        view = _compile(f'{{^{wider}:{template}}}')
        self.assertEqual(wider, len(view(model)))
        self.assertTrue(value in view(model))
        self.assertTrue(view(model).startswith(center_margin))
        self.assertTrue(view(model).endswith(center_margin))

        view = _compile(f'{{^{wider}!:{template}}}')
        self.assertEqual(wider, len(view(model)))
        self.assertTrue(value in view(model))
        self.assertTrue(view(model).startswith(center_margin))
        self.assertTrue(view(model).endswith(center_margin))

        if len(value) > 1:
            short = random.randint(1, len(value)-1)
            assert 1 <= short < len(value)

            # Если минимальная ширина оказывается меньше, значение выводится без изменений.

            view = _compile(f'{{{short}:{template}}}')
            self.assertEqual(value, view(model))
            view = _compile(f'{{>{short}:{template}}}')
            self.assertEqual(value, view(model))
            view = _compile(f'{{^{short}:{template}}}')
            self.assertEqual(value, view(model))

            # Кроме случаев, когда задаётся жёстко.

            view = _compile(f'{{{short}!:{template}}}')
            self.assertEqual(short, len(view(model)))
            self.assertTrue(value.startswith(view(model)))

            view = _compile(f'{{>{short}!:{template}}}')
            self.assertEqual(short, len(view(model)))
            self.assertTrue(value.endswith(view(model)))

            view = _compile(f'{{^{short}!:{template}}}')
            self.assertEqual(short, len(view(model)))
            self.assertTrue(view(model) in value)

    def test_title(self):
        """Должно выводить название и версию скрипта."""
        model = self._get_overlay_mockup()
        self._check_overlay(model, 'catframes', TITLE)

    def test_machine(self):
        """Должно выводить значение из модели."""
        model = self._get_overlay_mockup()
        self._check_overlay(model, 'machine', model.machine)

    def test_node(self):
        """Должно выводить значение из модели."""
        model = self._get_overlay_mockup()
        self._check_overlay(model, 'node', model.node)

    def test_vtime(self):
        """Стандартный формат — с миллисекундами. В остальном, формат работает у datetime."""
        model = self._get_overlay_mockup()
        expected = model.vtime.isoformat(timespec='milliseconds')
        self._check_overlay(model, 'vtime', expected)
        expected = model.vtime.isoformat(timespec='microseconds')
        self._check_overlay(model, 'vtime:%Y-%m-%dT%H:%M:%S.%f', expected)

        expected = model.vtime.strftime('%d.%m.%Y')
        self._check_overlay(model, 'vtime:%d.%m.%Y', expected)

        expected = model.vtime.strftime('%d.%m.%Y %H:%M:%S')
        self._check_overlay(model, 'vtime:%d.%m.%Y %H:%M:%S', expected)

    def test_file_name(self):
        """Должно выводить значение из модели."""
        model = self._get_overlay_mockup()
        self._check_overlay(model, 'fn', model.filename)

    def test_folder_name(self):
        """Должно выводить значение из модели."""
        model = self._get_overlay_mockup()
        self._check_overlay(model, 'dir', model.foldername)

    def test_frame_number(self):
        """Просто приводит к строке значения из модели."""
        model = self._get_overlay_mockup()
        self._check_overlay(model, 'frame:dir', str(model.numdir))
        self._check_overlay(model, 'frame:dirs', str(model.numvideo))
        self._check_overlay(model, 'frame:video', str(model.numvideo))

    def test_mtime(self):
        """Стандартный формат — с миллисекундами. В остальном, формат работает у datetime."""
        model = self._get_overlay_mockup()
        expected = model.mtime.isoformat(timespec='milliseconds')
        self._check_overlay(model, 'mtime', expected)
        expected = model.mtime.isoformat(timespec='microseconds')
        self._check_overlay(model, 'mtime:%Y-%m-%dT%H:%M:%S.%f', expected)

        expected = model.mtime.strftime('%d.%m.%Y')
        self._check_overlay(model, 'mtime:%d.%m.%Y', expected)

        expected = model.mtime.strftime('%d.%m.%Y %H:%M:%S')
        self._check_overlay(model, 'mtime:%d.%m.%Y %H:%M:%S', expected)

        model = self._get_overlay_mockup(with_mtime = False)
        assert model.mtime is None
        self._check_overlay(model, 'mtime', '')
        self._check_overlay(model, 'mtime:%d.%m.%Y %H:%M:%S', '')

    def test_size(self):
        """Просто приводит к строке значение из модели."""
        model = self._get_overlay_mockup()
        # Без разделителей разрядов вне зависимости от локали.
        assert int(str(model.size)) == model.size
        self._check_overlay(model, 'size', str(model.size))

    def test_resolution(self):
        """Просто приводит к строке значение из модели."""
        model = self._get_overlay_mockup()
        self._check_overlay(model, 'resolution', str(model.resolution))

    def test_symlink(self):
        """Выводит строку, если в модели кадр отмечен как симлинк."""
        a_file = self._get_overlay_mockup(symlink=False)
        a_link = self._get_overlay_mockup(symlink=True)

        self._check_overlay(a_file, 'symlink', '')
        self._check_overlay(a_link, 'symlink', 'symlink')

        self._check_overlay(a_file, 'symlink:L', '')
        self._check_overlay(a_link, 'symlink:L', 'L')
        self._check_overlay(a_link, 'symlink:симлинк', 'симлинк')
        self._check_overlay(a_link, 'symlink:Это симлинк!', 'Это симлинк!')

    def test_complex_overlay(self):
        """Уже что-то похожее на реальный пример с переводами строк."""
        model = self._get_overlay_mockup()
        assert len(str(model.numdir)) < 7
        time_str = model.mtime.strftime('%H:%M:%S') if model.mtime else ''

        template = 'Folder: {dir}\\nFrame: {7!:frame:dir} Time: {mtime:%H:%M:%S}'
        expected = f'Folder: {model.foldername}\nFrame: {model.numdir:<7} Time: {time_str}'
        view = OverLang.compile(template)
        self.assertEqual(expected, view(model))

        template = 'Folder: {dir}\\nFrame: {7!:frame:dir}\\nTime: {mtime:%H:%M:%S}'
        expected = f'Folder: {model.foldername}\nFrame: {model.numdir:<7}\nTime: {time_str}'
        view = OverLang.compile(template)
        self.assertEqual(expected, view(model))

        # Пользователь экранировал слэш.
        # Важно, чтобы не портился юникод.
        template = 'Директория: {dir}\\\\nКадр: {7!:frame:dir} Время: {mtime:%H:%M:%S}'
        expected = f'Директория: {model.foldername}\\nКадр: {model.numdir:<7} Время: {time_str}'
        view = OverLang.compile(template)
        self.assertEqual(expected, view(model))

    def test_bad_template(self):
        """Исключение должно выбрасываться на этапе компиляции шаблона."""
        templates = \
            '{}', \
            '{ }', \
            '{ machine }', \
            '{machine', \
            'machine}', \
            'machine}ddf', \
            '{machine}}', \
            '{asd:frame:dir}', \
            '{zxcvbn}'

        for template in templates:
            info = f'"{template}"'
            with self.assertRaises(ValueError, msg=info):
                OverLang.compile(template)


class Enumerator:
    """Модуль, включающий в себя логику нумерации кадров."""

    @classmethod
    def enumerate(cls, frame_groups: List[List[Frame]]):
        """Пронумеровывает кадры на месте."""
        for folder_index, folder in enumerate(frame_groups):
            previous_folders = frame_groups[:folder_index]
            previous_frames = sum((cls.count(x) for x in previous_folders))

            number = 1
            for frame in folder:
                if not frame.banner:
                    frame.numdir = number
                    frame.numvideo = previous_frames + number
                    number += 1

    @staticmethod
    def count(frames: List[Frame]):
        """Считает кадры, игнорируя кадры-заглушки."""
        return sum((1 for x in frames if not x.banner))


class _EnumeratorTest(TestCase):
    def test_simple(self):
        with tempfile.TemporaryDirectory() as folder_path_string:
            folder_path = Path(folder_path_string)
            file_1 = folder_path / '1.jpg'
            Image.new("RGB", (640, 480)).save(file_1)

            frame_groups = []
            for _ in range(3):
                frames = []
                frame_groups.append(frames)
                for _ in range(100):
                    frames.append(Frame(file_1))

            Enumerator.enumerate(frame_groups)

            for group_index in range(3):
                previous = sum(len(x) for x in frame_groups[:group_index])
                for frame_index in range(100):
                    frame = frame_groups[group_index][frame_index]
                    self.assertEqual(1+frame_index, frame.numdir)
                    self.assertEqual(previous+(1+frame_index), frame.numvideo)

            all_frames = functools.reduce(lambda x, y: x+y, frame_groups)
            self.assertEqual(300, Enumerator.count(all_frames))

            self.assertEqual(1, all_frames[0].numvideo)
            self.assertEqual(300, all_frames[-1].numvideo)

    def test_mixed(self):
        banner_1 = Frame(None, True, 'Message 1')
        banner_2 = Frame(None, True, 'Message 2')
        banner_3 = Frame(None, True, 'Message 3')

        with tempfile.TemporaryDirectory() as folder_path_string:
            folder_path = Path(folder_path_string)
            file_1 = folder_path / '1.jpg'
            Image.new("RGB", (640, 480)).save(file_1)

            frame_groups = []
            for _ in range(3):
                frames = []
                frame_groups.append(frames)
                for _ in range(100):
                    frames.append(Frame(file_1))

            # Добавляю 40 кадров-заглушек.

            frame_groups[0].insert(0, banner_1)

            for i in range(10):
                frame_groups[0].insert(3, banner_1)

            for i in range(20):
                frame_groups[1].insert(44, banner_1)

            for i in range(5):
                frame_groups[2].insert(70, banner_3)

            for i in range(4):
                frame_groups[2].append(banner_3)

            Enumerator.enumerate(frame_groups)

            previous = 0
            for group_index in range(3):
                previous_in_the_directory = 0
                for frame in frame_groups[group_index]:
                    if not frame.banner:

                        self.assertEqual(previous_in_the_directory + 1, frame.numdir)
                        self.assertEqual(previous + 1, frame.numvideo)

                        previous_in_the_directory += 1
                        previous += 1

            all_frames = functools.reduce(lambda x, y: x+y, frame_groups)
            self.assertEqual(340, len(all_frames))
            self.assertEqual(300, Enumerator.count(all_frames))

            first_real_frame = next((x for x in all_frames if not x.banner), None)
            last_real_frame = next((x for x in reversed(all_frames) if not x.banner), None)
            self.assertIsNotNone(first_real_frame)
            self.assertIsNotNone(last_real_frame)

            self.assertEqual(1, first_real_frame.numvideo)
            self.assertEqual(300, last_real_frame.numvideo)


class ConsoleInterface:
    """Интерфейс пользователя.

    Превращает аргументы командной строки в настройки и наборы данных. И тут также выводится
    информация в стандартный вывод по ходу анализа параметров скрипта.
    """
    __slots__ = '_args', '_source', '_destination', '_layout'

    def __init__(self):
        parser = ArgumentParser(prog='catframes.py', description=DESCRIPTION,
            formatter_class=RawDescriptionHelpFormatter)

        self._add_input_arguments(parser)
        self._add_rendering_arguments(parser)
        self._add_output_arguments(parser)
        self._add_system_arguments(parser)

        parser.add_argument('--resolutions', action='store_true',
            help='show the resolution choosing process and exit')

        supported_suffixes = ' or '.join(map(lambda x: x[1:], OutputOptions.get_supported_suffixes()))
        parser.add_argument('paths', metavar='PATH', nargs='+',
            help='The paths are input folders (a source), ' + 
            'and the last one is an output video file ' +
            f'({supported_suffixes}, a destination). ' + 
            'The order of the folders determines in which order ' +
            'they will be concatenated. ' +
            'If `--resolutions` argument is used, the destination path is optional. ' +
            'That means, that if the last path points ' +
            'to a folder or a symlink to a folder, ' +
            'even if its name is similar to a video file, ' +
            'the script treat it as an input folder.')

        self._args = parser.parse_args()
        if self._args.resolutions and \
                (
                    (len(self._args.paths) <= 1) or
                    Path(self._args.paths[-1]).expanduser().is_dir() or
                    Path(self._args.paths[-1]).suffix not in OutputOptions.get_supported_suffixes()
                ):
            self._source = self._args.paths
            self._destination = None
        elif len(self._args.paths) <= 1:
            parser.error('A destination path is required.')
        else:
            self._source = self._args.paths[:-1]
            self._destination = self._args.paths[-1]

        self._layout = self._make_layout()

    @staticmethod
    def _get_minmax_type(min_value: int, max_value: int = (sys.maxsize-1)):
        def validator(arg):
            try:
                int_value = int(arg)
            except ValueError as error:
                raise ArgumentTypeError from error

            if int_value not in range(min_value, max_value+1):
                raise ArgumentTypeError(
                    f'It must be in range ({min_value}, {max_value}).')

            return int_value
        return validator

    @classmethod
    def _add_input_arguments(cls, parser: ArgumentParser):
        input_arguments = parser.add_argument_group('Input')
        input_arguments.add_argument('-s', '--sure', action='store_true',
            help="do not exit if some or all of input directories " + 
            "do not exist. You are sure that you are specifying " +
            "the correct folders. If they don't exist, it just has to be " +
            "shown in the resulting video.")

    def _make_layout(self):
        h_positions = ('left', 0), ('right', 2)
        v_positions = ('top', 0), ('bottom', 2)
        middle = 1

        result = Layout()
        has_warning = False
        options_dict = vars(self._args)

        def add_overlay(xpos: int, ypos: int, option_name: str):
            nonlocal has_warning
            template = options_dict[option_name]
            if template:
                result.put(xpos, ypos, OverLang.compile(template))
                if OverLang.is_warning(template):
                    has_warning = True

        for pos in h_positions:
            add_overlay(pos[1], middle, pos[0])

        for pos in v_positions:
            add_overlay(middle, pos[1], pos[0])

        for h_pos, v_pos in itertools.product(h_positions, v_positions):
            add_overlay(h_pos[1], v_pos[1], f'{h_pos[0]}_{v_pos[0]}')

        for v_pos, h_pos in itertools.product(v_positions, h_positions):
            add_overlay(h_pos[1], v_pos[1], f'{v_pos[0]}_{h_pos[0]}')

        if not has_warning:
            print("\nBy the way: You didn't specify any WARN overlays.", flush=True)

        return result

    @classmethod
    def _add_rendering_arguments(cls, parser: ArgumentParser):
        h_positions = ('left', 0), ('right', 2)
        v_positions = ('top', 0), ('bottom', 2)
        center = ('center', 1)
        warning_x, warning_y = 1, 0

        def get_default_overlay(h_pos, v_pos):
            if h_pos[1] == warning_x and v_pos[1] == warning_y:
                return 'WARN'
            return None

        rendering_arguments = parser.add_argument_group('Rendering')

        def add_overlay_argument(argument, base_help, h_pos, v_pos):
            default = get_default_overlay(h_pos, v_pos)
            help_tail = ' (default: %(default)s)' if default else ''
            rendering_arguments.add_argument(
                argument, metavar='T',
                help=base_help+help_tail,
                default=default)

        overlay_help_head = 'text at the'

        for pos in h_positions:
            add_overlay_argument(
                f'--{pos[0]}',
                f'{overlay_help_head} {pos[0]} in the middle',
                pos, center)

        for pos in v_positions:
            add_overlay_argument(
                f'--{pos[0]}',
                f'{overlay_help_head} {pos[0]} in the middle',
                center, pos)

        for h_pos, v_pos in itertools.product(h_positions, v_positions):
            add_overlay_argument(
                f'--{h_pos[0]}-{v_pos[0]}',
                f'{overlay_help_head} {h_pos[0]} {v_pos[0]}',
                h_pos, v_pos)

        for v_pos, h_pos in itertools.product(v_positions, h_positions):
            add_overlay_argument(
                f'--{v_pos[0]}-{h_pos[0]}',
                f'alias for --{h_pos[0]}-{v_pos[0]}',
                h_pos, v_pos)

        rendering_arguments.add_argument('--margin-color', metavar='X',
            default='#000',
            help='#rrggbb or #rgb (default: %(default)s)')

    @classmethod
    def _add_output_arguments(cls, parser: ArgumentParser):
        quality_choices = 'poor', 'medium', 'high'
        default_quality = quality_choices[1]

        video_arguments = parser.add_argument_group('Output')
        video_arguments.add_argument('-r', '--frame-rate', metavar='X',
            default=30, type=cls._get_minmax_type(1, 60),
            help='an integer from 1 to 60 (default: %(default)s)')
        video_arguments.add_argument('-q', '--quality', metavar='X',
            choices=quality_choices, default=default_quality,
            help='%(choices)s (default: %(default)s)')
        video_arguments.add_argument('--limit', metavar='SECONDS',
            type=cls._get_minmax_type(1),
            help='to try different options')
        video_arguments.add_argument('-f', '--force', action='store_true',
            help='overwrite video file if exists')

    @classmethod
    def _add_system_arguments(cls, parser: ArgumentParser):
        system_arguments = parser.add_argument_group('System')
        system_arguments.add_argument('-p', '--port-range', metavar='X',
            default='10240:65535',
            help='deprecated and will be removed soon')

        system_arguments.add_argument('--live-preview', action='store_true',
            help='print base64 encoded JPEG thumbnails')

    def show_options(self):
        """Чтобы пользователь видел, как проинтерпретированы его аргументы."""
        print(flush=True)
        for key, value in vars(self._args).items():
            if 'paths' == key:
                continue

            if isinstance(value, list):
                print(f'  {key}:', flush=True)
                for item in value:
                    print(f'    - {item}', flush=True)
            elif value:
                print(f'  {key}: {value}', flush=True)

        print(f'  source:', flush=True)
        for item in self._source:
            print(f'    - {item}', flush=True)
        if None != self._destination:
            print(f'  destination:', flush=True)
            print(f'    - {self._destination}', flush=True)
        print(flush=True)

    def show_splitter(self):
        """Визуально отделить всё, что было выведено в консоль выше."""
        print(f"{'-'*42}\n", flush=True)

    def get_input_sequence(self) -> Sequence[Frame]:
        """Возвращает отсортированную и пронумерованную последовательность кадров.

        :raises ValueError: не удалось прочитать список файлов или в указанных директориях нет
            ни одного изображения.
        """
        print('Scanning for files...', flush=True)
        frame_groups = []

        banner_duration_seconds = 4

        def get_banner_frames(message):
            banner = Frame(None, True, message)
            return [banner for i in range(banner_duration_seconds * self._args.frame_rate)]

        for raw_folder_path in self._source:
            folder_path = Path(raw_folder_path)
            real_images: Union[List[Path], None] = None
            try:
                real_images = FileUtils.list_images(folder_path)
            except (ValueError, OSError) as e:
                if self._args.sure:
                    frame_groups.append(get_banner_frames(f'{type(e).__name__}: {str(e)}'))
                else:
                    raise

            if real_images is None:
                # Либо мы выбросили исключение ранее,
                # либо кадры-заглушки уже добавлены.
                pass
            elif (len(real_images) < 1) and self._args.sure:
                frame_groups.append(get_banner_frames(f'Could not find images in {folder_path}'))
            else:
                FileUtils.sort_natural(real_images)
                frame_groups.append([Frame(image) for image in real_images])

        print('Numbering frames...', flush=True)
        Enumerator.enumerate(frame_groups)

        frames = functools.reduce(lambda x, y: x+y, frame_groups)

        print(f'\nThere are {Enumerator.count(frames)} frames...', flush=True)

        # Имеется ввиду, что совсем никаких кадров нет, даже кадров-заглушек.
        # Если не только несуществующие, но и пустые папки будут приводить
        # к добавлению кадров-заглушек, это невозможная ситуация.
        # Добавление заглушек для пустых папок имеет смысл, если указана
        # опция --sure, ведь если мы уверены, что указали папки верно,
        # в них должны быть кадры.
        if not frames:
            raise ValueError('Error: empty frame set.')

        print(flush=True)

        return frames

    def get_output_options(self) -> OutputOptions:
        """Возвращает настройки сохранения видео.

        :raises ValueError: пользователь указал файл с недопустимым расширением и т.п.
        """
        destination = Path(self._destination)

        if destination.is_dir():
            raise ValueError('Destination must not be a folder.')

        if destination.is_symlink():
            raise ValueError('Destination must not be a symbolic link.')

        if destination.suffix not in OutputOptions.get_supported_suffixes():
            expected = ', '.join(
                map(lambda x: x[1:], OutputOptions.get_supported_suffixes())
            )
            raise ValueError(f'Unsupported destination file extension.\nExpected: {expected}.')

        if self._args.quality == 'high':
            quality = Quality.HIGH
        elif self._args.quality == 'poor':
            quality = Quality.POOR
        else:
            quality = Quality.MEDIUM

        return OutputOptions(
            destination=destination,
            overwrite=bool(self._args.force),
            limit_seconds=self._args.limit,
            live_preview=self._args.live_preview,
            quality=quality,
            frame_rate=self._args.frame_rate)

    @property
    def statistics_only(self) -> bool:
        """Пользователь не хочет пока делать видео, только посмотреть логику выбора разрешения."""
        return self._args.resolutions

    @property
    def margin_color(self) -> str:
        """В случае полупрозрачных кадров, это будет также цвет фона."""
        return self._args.margin_color

    @property
    def layout(self) -> Layout:
        """План наложения оверлеев."""
        return self._layout

    @staticmethod
    def list_resolutions(resolutions: ResolutionStatistics, limit:int = 10):
        """Перечислить разрешения от самых частых к самым редким."""
        lines = resolutions.sort_by_count_desc()
        assert limit > 0

        print('Resolutions:', flush=True)
        for resolution, count in lines[:limit]:
            print(f"{resolution} => {count}", flush=True)

        if len(lines) > limit:
            print('...', flush=True)


def main():
    gc.set_threshold(100, 10, 10)   # По-умолчанию 700-10-10.
    try:
        if not shutil.which('ffmpeg'):
            raise ValueError('FFmpeg not found.')

        cli = ConsoleInterface()
        cli.show_options()
        cli.show_splitter()
        print(f'The number of overlays: {len(cli.layout)}\n', flush=True)
        cli.show_splitter()

        if not cli.statistics_only:
            output_options = cli.get_output_options()
            if (not output_options.overwrite) and output_options.destination.exists():
                raise ValueError('Destination file already exists.')
        else:
            output_options = None

        frames = cli.get_input_sequence()

        resolution_table = ResolutionStatistics(frames)
        cli.list_resolutions(resolution_table)

        resolution = resolution_table.choose()
        print(f'\nDecision: {resolution}\n', flush=True)

        if cli.statistics_only:
            sys.exit(0)

        cli.show_splitter()
        del resolution_table

        processing_start = monotonic()

        view: DefaultFrameView = DefaultFrameView(resolution, cli.margin_color, cli.layout)
        frames = output_options.limit_frames(frames)

        output_processor = OutputProcessor(output_options)

        def on_interrupt(sig, frame):
            os.write(sys.stdout.fileno(), b'Keyboard interrupt!\n')
            output_processor.exit_threads()

        def on_terminate(sig, frame):
            os.write(sys.stdout.fileno(), b'Termination!\n')
            output_processor.exit_threads()

        def on_ctrl_break(sig, frame):
            os.write(sys.stdout.fileno(), b'CTRL+BREAK!\n')
            output_processor.exit_threads()

        signal.signal(signal.SIGINT, on_interrupt)
        signal.signal(signal.SIGTERM, on_terminate)
        signal.signal(signal.SIGBREAK, on_ctrl_break)

        output_processor.make(view, frames)

        print(f'\nFinished in {int(monotonic() - processing_start)} seconds.', flush=True)

    except ValueError as err:
        print(f'\n{err}\n', file=sys.stderr, flush=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

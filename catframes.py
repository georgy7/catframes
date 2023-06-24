#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Catframes

© Устинов Г.М., 2022

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
3. Хотя бы один юникодный моноширинный TrueType-шрифт (см. код PillowFrameView).

"""

# from __future__ import annotations  # для псевдонимов в autodoc

from argparse import ArgumentParser, ArgumentTypeError, RawDescriptionHelpFormatter
from datetime import datetime
import functools
import gc
import hashlib
import itertools
import io
import math
import os
from operator import itemgetter
from pathlib import Path
import platform
import random
import re
import shutil
import subprocess
import sys
import tempfile
import threading
from wsgiref.simple_server import make_server

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Dict, Iterable, List, NamedTuple, Optional, Sequence, Tuple, Union

import http.client
from time import sleep, monotonic
from unittest import TestCase

from PIL import Image, ImageColor, ImageDraw, ImageFont


__version__ = '2023.06-SNAPSHOT'
__license__ = 'Zlib'


TITLE = f'Catframes v{__version__}'

DESCRIPTION = f"""{TITLE}

  License: {__license__}

  Documentation: http://itustinov.ru/cona/latest/docs/html/catframes.html

  Git: https://gitflic.ru/project/georgy7/cona

  Git bundle: http://itustinov.ru/cona/latest/cona.pack

  GitHub: https://github.com/georgy7/catframes

"""

WebApp = Callable[[dict, Callable], Iterable[bytes]]
"""Первый аргумент — WSGI environment (включает всю информацию о запросе), второй — функция начала
ответа, которая принимает статус HTTP-ответа и список HTTP-заголовков. В терминах MVC, это еще
неразграниченные роутинг с контроллерами.

Подробнее читайте в официальной документации: :py:func:`wsgiref.simple_server.make_server`.
"""

WebJob = Callable[[int], None]
"""Функция, которая работает с локальным веб-приложением. Аргумент — номер порта."""


@dataclass(frozen=True)
class JobServerOptions:
    min_http_port: int
    max_http_port: int

    def __post_init__(self):
        assert self.min_http_port > 0
        assert self.max_http_port > 0
        assert self.min_http_port <= self.max_http_port


class JobServer:
    """Механизм межпроцессного взаимодействия на основе HTTP. Открывает порт и обслуживает другие
    программы, которые контролируются из этого же сервера.

    Грубо говоря, эта штука позволяет делать что-то вроде динамической файловой системы, если
    считать URL файлами: в тот момент, когда что-то запрашивается сторонней программой, оно
    подготавливается на лету. Не тратится дисковое пространство, а если не использовать временные
    файлы при обработке запросов, то и ресурс SSD.

    В целях безопасности:

    1. на компьютере следует использовать файрвол;
    2. лучше не передавать списки URL по HTTP-каналу.

    Номер порта выбирается автоматически. Значения ниже десяти тысяч не используются, чтобы
    не мешать всяким Томкэтам и Ноджиэсам.

    :param app: Функция, которая обслуживает HTTP-запросы.
    :param job: Запускается один раз. Сервер ждёт завершения. Выброшенные исключения приводят
        к остановке сервера и вылетают из метода :meth:`run`.
    :param options: Системные настройки.
    """
    def __init__(self, app: WebApp, job: WebJob, options: JobServerOptions):
        self._app: WebApp = app
        self._job: WebJob = job
        self._options = options
        self._job_error: Union[Exception, None] = None

    def run(self):
        """Запускает сервер, ждёт завершения работ, останавливает сервер.

        :raises Exception: если исключение вылетело из джобы.
        """
        while not self._was_running():
            print('Trying different port...')
        if self._job_error:
            raise self._job_error

    def _do_the_job(self, port):
        try:
            self._job(port)
        except Exception as exc:
            # Ловля общего исключения обоснована:
            # нужно остановить сервер, а потом можно перевыбросить.
            self._job_error = exc

    def _was_running(self) -> bool:
        port = random.randint(
            self._options.min_http_port,
            self._options.max_http_port
        )
        print(f"\nPort: {port}\n")
        try:
            with make_server(host='', port=port, app=self._app) as httpd:
                web_thread = threading.Thread(target = httpd.serve_forever)
                web_thread.start()
                self._do_the_job(port)
                httpd.shutdown()
            return True
        except OSError:
            return False


class _JobServerTest(TestCase):
    def test_get(self):
        """Сервер должен ждать завершения работ. Здесь используются GET-запросы и ASCII-пути."""

        content = 'Hello World'.encode("utf-8")

        def webapp(environ, start_response):
            method: str = environ['REQUEST_METHOD']
            pathname: str = environ['PATH_INFO']

            if method == 'GET' and pathname == '/abc.txt':
                status = '200 OK'
                headers = [('Content-type', 'text/plain; charset=utf-8')]
                start_response(status, headers)
                return [content]

            if method == 'GET' and pathname.startswith('/Item'):
                status = '200 OK'
                headers = [('Content-type', 'text/plain; charset=utf-8')]
                start_response(status, headers)
                return [pathname.encode("utf-8")]

            status = '404 Not Found'
            headers = [('Content-type', 'text/plain; charset=utf-8')]
            start_response(status, headers)
            return ['Not found.'.encode("utf-8")]

        def webjob(port):
            base_url = f'localhost:{port}'

            def read(pathname):
                conn = http.client.HTTPConnection(base_url)
                conn.request('GET', pathname)
                response = conn.getresponse()
                return (response.status, response.read())

            self.assertEqual(read('/abc.txt'), (200, content))
            self.assertEqual(read('/wrong')[0], 404)
            sleep(1)
            self.assertEqual(read('/abc.txt'), (200, content))

            self.assertEqual(
                read('/Item/123'),
                (200, '/Item/123'.encode("utf-8")))

        server = JobServer(webapp, webjob, JobServerOptions(10240, 65535))
        server.run()


class FileUtils:
    """Модуль вспомогательных функций, связанных с файловой системой."""

    @staticmethod
    def get_checksum(path: Path) -> Optional[str]:
        """Функция не выбрасывает исключения."""
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
    def get_mtime(path: Path) -> Optional[datetime]:
        """Функция не выбрасывает исключения."""
        try:
            return datetime.fromtimestamp(os.path.getmtime(path.expanduser()))
        except OSError:
            return None

    @staticmethod
    def get_file_size(path: Path) -> Optional[int]:
        """Функция не выбрасывает исключения."""
        try:
            normal_path = path.expanduser()
            if normal_path.is_file():
                return os.path.getsize(normal_path)
            return None
        except OSError:
            return None

    @staticmethod
    def is_symlink(path: Path) -> bool:
        """Функция не выбрасывает исключения."""
        return path.expanduser().is_symlink()

    @staticmethod
    def list_images(path: Path) -> List[Path]:
        """Набор файлов JPEG и PNG в порядке, предоставляемом pathlib (не определён в документации
        и, скорее всего, зависит от операционной системы). Файлы определяются по расширениям
        (суффиксам имён). Вложенные папки игнорируются.

        :raises ValueError: путь не является директорией.
        :raises OSError: не удалось получить список файлов.
        """
        folder = path.expanduser()

        if not folder.is_dir():
            raise ValueError(f'The path is not a folder: {folder}')

        frame_extensions = "jpg", "jpeg", "png", "JPG", "JPEG", "PNG"

        return [
            file_path
            for file_path in folder.iterdir()
            if file_path.is_file()
            and file_path.suffix[1:] in frame_extensions
        ]

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
        """Работает как sha1sum в Linux. У папок и несуществующих файлов возвращает None.
        """
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
        """Выдаёт местное время модификации, если файл не существует — None.
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
        """У папок и несуществующих файлов возвращает None.
        """
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
        """Для несуществующих файлов возвращает False. Для существующих тоже. Не создаю симлинки
        в этом тесте, т.к. некоторые системы могут это запрещать непривилегированным пользователям.
        """
        with tempfile.TemporaryDirectory() as folder_path_string:
            file_path = Path(folder_path_string) / '1.txt'
            self.assertEqual(FileUtils.is_symlink(file_path), False)

        with tempfile.TemporaryDirectory() as folder_path_string:
            file_path = Path(folder_path_string) / '1.txt'
            file_path.write_text('12345', encoding='utf-8')
            self.assertEqual(FileUtils.is_symlink(file_path), False)

    def test_natural_sort_of_empty_list(self):
        """Не должно падать при сортировке пустых списков файлов."""
        items = []
        FileUtils.sort_natural(items)
        self.assertSequenceEqual([], items)

    def test_natural_sort_of_letters(self):
        """Не должно падать, когда в именах файлов нет цифр."""
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
        """Экстремальный пример для демонстрации."""
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
        """Показывает, что ведущие нули не мешают натуральной сортировке."""
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
        """Базовый случай, на который натуральная сортировка рассчитана."""
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
    """Ненулевое разрешение в пикселях."""

    width: int
    height: int

    def __post_init__(self):
        assert self.width > 0
        assert self.height > 0

    def __str__(self):
        """Возвращает строку вида ``ШxВ``. Икс в качестве разделителя выбран из соображений
        совместимости с максимальным числом шрифтов оверлеев и кодировок терминалов.
        """
        return f'{self.width}x{self.height}'

    @property
    def ratio(self) -> float:
        """Соотношение сторон. Всегда больше нуля."""
        return self.width / self.height


class Frame:
    """Кадр на диске. Сырьё для :class:`FrameView`. Конструктор создаёт объект, даже если путь
    ведёт в никуда. Не иммутабельная сущность, некоторые поля могут обновляться.
    """
    __slots__ = '_checksum', '_path', '_resolution', 'numdir', 'numdirs', 'numvideo'

    def __init__(self, path: Path):
        self._checksum = FileUtils.get_checksum(path)
        self._path = path

        self._resolution = None

        if self._checksum:
            try:
                with Image.open(path.expanduser()) as image:
                    width, height = image.size
                    self._resolution = Resolution(width, height)
            except OSError:
                pass

        self.numdir: int = 0
        """Каким он будет по счету в своей папке, если её содержимое отсортировать."""

        self.numdirs: int = 0
        """Каким он будет по счету, если отсортировать изображения в папках и склеить списки."""

        self.numvideo: int = 0
        """Как :attr:`numdirs`, но если пользователь просит отрезать сколько-то кадров из начала
        последовательности, нумерация всё равно начинается с единицы, т.к. это первый кадр в видео.
        """

    @property
    def path(self) -> Path:
        """Путь к файлу в директории, указанной пользователем. Может быть симлинком."""
        return self._path

    @property
    def name(self) -> str:
        """Имя файла или симлинка."""
        return self.path.name

    @property
    def folder(self) -> str:
        """Имя папки с файлом (для демонстрации пользователю)."""
        return self.path.parent.parts[-1]

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
        """Равенство у разрешений — равенство значений, а не ссылок."""
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
    """Модуль вспомогательных функций, связанных с разрешениями."""

    @staticmethod
    def round(value: float) -> int:
        """Округляет вычисленный размер стороны. Поддерживаемые форматы видео могут иметь
        ограничения, поэтому это округление не обязательно идёт до ближайшего целого. Имеет смысл
        использовать как финальный этап выбора разрешения видео.
        """
        # H264 требует чётные размеры. Если мы выбираем самое частое разрешение, то, пожалуй,
        # будем отрезать нечётный пиксель, чтобы не терять качество из-за масштабирования.
        return math.floor(value/2)*2

    @staticmethod
    def get_scale_size(src: Resolution, goal: Resolution) -> Optional[Resolution]:
        """Пропорционально меняет разрешение, чтобы исходник вписался в целевое разрешение без
        зазора. None означает либо рекомендацию кадрировать картинку вместо масштабирования, либо
        что она уже идеально вписывается.
        """
        max_crop = 1    # Значение связано с принципом работы метода round.

        should_zoom_out = \
            (src.width > goal.width + max_crop) or \
            (src.height > goal.height + max_crop)

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
        """Следует применять только если :meth:`get_scale_size` вернул None. Если соотношение
        сторон отличается, размер будет меньше целевого по одной стороне.
        """
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
            max_weight = max(xw[1] for xw in filtered)

            most_frequent = (xw for xw in filtered if xw[1] == max_weight)
            return round(max(xw[0] for xw in most_frequent))

        res_list, count = zip(*self._table.items())
        width = [resolution.width for resolution in res_list]
        height = [resolution.height for resolution in res_list]

        return Resolution(
                ResolutionUtils.round(find(list(zip(width, count)))),
                ResolutionUtils.round(find(list(zip(height, count)))))


class FrameResponse(NamedTuple):
    """Ответ сервера на запрос кадра. Предполагается, что раз ответ есть, это HTTP OK."""
    data: bytes
    content_type: str


class FrameView(ABC):
    """Абстрактное представление кадра. Отвечает как за подгонку разрешения (обязательно), а также
    за любую другую обработку: добавление надписей, подстраивание яркости и контрастности и т.п.
    """
    def __init__(self, resolution: Resolution):
        self.resolution = resolution

    @abstractmethod
    def apply(self, frame: Frame) -> FrameResponse:
        """Получить оформленный кадр как набор байт. Выбрасывание исключений здесь приведёт
        к пятисотой ошибке в HTTP-ответе.
        """


class Quality(Enum):
    """Абстракция над бесконечными настройками качества FFmpeg."""

    HIGH = 8, 4
    """Очень высокое, но всё же с потерями. Подходит для художественных таймлапсов, где важно
    сохранить текстуру, световые переливы, зернистость камеры. Битрейт — как у JPEG 75.
    """

    MEDIUM = 16, 18
    """Подойдёт почти для любых задач. Зернистость видео пропадает, градиенты становятся чуть
    грубее, картинка может быть чуть мутнее, но детали легко узнаваемы.
    """

    POOR = 22, 31
    """Некоторые мелкие детали становятся неразличимыми."""

    def get_h264_crf(self, fps: int) -> int:
        """Constant Rate Factor меняет битрейт для поддержания постоянного уровня качества. Метрика
        качества в кодеке связана с движением — медленные объекты считаются более заметными.

        При повышении частоты кадров, детали в каждом отдельном кадре становятся всё менее
        различимыми для зрителей, поэтому кодек при том же CRF порождает меньшие файлы.

        Всё это логично для фильмов, но плохо для видеонаблюдения, где важен каждый кадр. Данный
        метод корректирует CRF обратно по частоте смены кадров.
        """
        if (fps < 1) or (fps > 60):
            raise ValueError('Unsupported frame rate.')
        return round(self.value[0] + 2.3 * math.log2(60/fps))

    def get_vp9_crf(self) -> int:
        """Мои тесты показали, что опция CRF в VP9 не связана с частотой кадров."""
        return self.value[1]


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

    def __post_init__(self):
        assert 1 <= self.frame_rate <= 60
        assert isinstance(self.quality, Quality)
        assert isinstance(self.destination, Path)
        assert isinstance(self.overwrite, bool)
        if self.limit_seconds is not None:
            assert self.limit_seconds > 0

    def _get_h264_options(self) -> Sequence[str]:
        # Настраивать промежутки между ключевыми кадрами смысла нет: большинство плееров
        # умеют точно перематывать, даже если между ними большие промежутки.
        h264_crf = self.quality.get_h264_crf(self.frame_rate)
        return ['-pix_fmt', 'yuv420p', '-c:v', 'libx264',
            '-preset', 'fast', '-tune', 'fastdecode',
            '-movflags', '+faststart',
            '-crf', str(h264_crf)]

    def _get_vp9_options(self) -> Sequence[str]:
        vp9_crf = self.quality.get_vp9_crf()
        return ['-c:v', 'libvpx-vp9', '-pix_fmt', 'yuv420p',
            '-crf', str(vp9_crf), '-b:v', '0']

    @staticmethod
    def get_supported_suffixes() -> Sequence[str]:
        """Возвращает поддерживаемые расширения файлов."""
        return '.mp4', '.webm'

    def make(self, frames: Sequence[Frame], view: FrameView, server_options: JobServerOptions):
        """Обрабатывает с помощью :class:`FrameView` и соединяет кадры последовательности
        в видеозапись. Сортировка последовательности, как и валидация всех опций, должны быть
        сделаны заранее.

        Всё происходит в ОЗУ. Диск используется только для

        1. чтения кадров,
        2. хранения списка кадров в текстовом временном файле,
        3. сохранения видео.

        Скрипт ответственнен примерно за одну пятую суммарного с FFmpeg потребления памяти.
        """
        if self.limit_seconds:
            frames = frames[:(self.limit_seconds*self.frame_rate)]

        # На случай отсутствия файрвола, адреса не должны быть предсказуемыми. При таком смещении,
        # шанс угадать URL одного кадра 24-часового видео с 60 fps — 1:2e12 на 64-битной машине.
        offset: int = random.randint(0, max(0, sys.maxsize - len(frames)))

        def app(environ, start_response):
            method: str = environ['REQUEST_METHOD']
            pathname: str = environ['PATH_INFO']

            http_get = (method == 'GET')
            img_page = re.fullmatch(r'/img/(\d+)', pathname)

            if http_get and img_page:
                frame_index = int(img_page.groups()[0]) - offset
                if frame_index in range(len(frames)):
                    frame = frames[frame_index]
                    status = '200 OK'
                    render_result = view.apply(frame)
                    headers = [('Content-type', render_result.content_type)]
                    start_response(status, headers)
                    return [render_result.data]

            status = '404 Not Found'
            headers = [('Content-type', 'text/plain; charset=utf-8')]
            start_response(status, headers)
            return ['Not found.'.encode("utf-8")]

        def job(port: int):
            base_url = f'http://localhost:{port}/img/'

            with tempfile.TemporaryDirectory() as folder_path_string:
                folder_path = Path(folder_path_string)
                list_path = folder_path / 'list.txt'

                duration = 1 / self.frame_rate

                with list_path.open('w') as list_file:
                    for frame_index in range(len(frames)):
                        shifted_index = offset + frame_index
                        list_file.write(f"file '{base_url}{shifted_index}'\n")
                        list_file.write(f"duration {duration:.10f}\n")

                ffmpeg_options = [
                    'ffmpeg', '-f', 'concat',
                    '-safe', '0',
                    '-protocol_whitelist', 'file,http,tcp',
                    '-i', str(list_path)
                ]

                suffix = self.destination.suffix
                if suffix == '.mp4':
                    ffmpeg_options.extend(self._get_h264_options())
                elif suffix == '.webm':
                    ffmpeg_options.extend(self._get_vp9_options())
                else:
                    raise ValueError('Unsupported file name suffix.')

                ffmpeg_options.extend([
                    '-r', str(self.frame_rate),
                    ('-y' if self.overwrite else '-n'),
                    str(self.destination.expanduser())
                ])

                subprocess.check_call(ffmpeg_options)

        server = JobServer(app, job, server_options)
        server.run()


class PillowFrameView(FrameView):
    """Каркас для гарантированно однопоточного рендеринга библиотекой Pillow. Синхронизация
    позволяет использовать один и тот же холст многократно, не нагружая кучу и сборщик мусора.
    """
    def __init__(self, resolution: Resolution):
        super().__init__(resolution)

        self._lock = threading.Lock()

        self._image: Image.Image = Image.new('RGB', (resolution.width, resolution.height))
        """Холст для заполнения методом render."""

        self._draw: ImageDraw.ImageDraw = ImageDraw.Draw(self._image)
        """2D-контекст для рисования на холсте."""

    def apply(self, frame: Frame) -> FrameResponse:
        """Создаёт картинку прямо в ОЗУ."""
        with self._lock:
            self._render(frame)
            assert self._image.size[0] == self.resolution.width
            assert self._image.size[1] == self.resolution.height
            result = io.BytesIO()
            self._image.save(result, 'JPEG', quality=95, subsampling=0)
            return FrameResponse(result.getvalue(), 'image/jpeg')

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
                print(f'{filename}: yes')
                return result
            except OSError:
                print(f'{filename}: no')

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
    """Номер кадра в текущей директории, начиная с единицы. Если мы пропускаем N кадров опцией
    ``--trim-start=N``, и N меньше числа кадров в первой директории, у первого кадра видео этот
    номер будет равен N+1.
    """
    numdirs: int
    """Номер кадра во всех директориях (сплошная нумерация). Если мы пропускаем N кадров опцией
    ``--trim-start=N``, первый кадр видео всегда будет под номером N+1.
    """
    numvideo: int
    """Сплошная нумерация, но всегда начинается с единицы."""

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
        assert isinstance(self.numdirs, int)
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
            numdirs=frame.numdirs,
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

    def _render(self, frame: Frame):
        overlay_model: Union[OverlayModel, None] = None

        try:
            with Image.open(frame.path) as source:
                overlay_model = self._make_overlay_model(frame, source.size)
                self._clear(self.margin_color)
                self._paste(source)
        except OSError as image_open_error:
            self._clear(self.ERROR_BG)
            self._draw_multiline(
                1, 1,
                f'{frame.folder}/{frame.name}\n{image_open_error.__class__.__name__}',
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

            response_1: FrameResponse = view.apply(Frame(non_transparent_path))
            response_2: FrameResponse = view.apply(Frame(transparent_path))

        from_rgb_src = Image.open(io.BytesIO(response_1.data)).convert('RGB').load()
        from_rgba_src = Image.open(io.BytesIO(response_2.data)).convert('RGB').load()

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

                                * ``dir`` — текущая директория;
                                * ``dirs`` — все директории;
                                * ``video`` — видеозапись: нумерация начинается с единицы даже при
                                  использовании опции ``--trim-start``.
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
                return lambda x: str(x.numdirs)
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
            numdirs=555,
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
        self._check_overlay(model, 'frame:dirs', str(model.numdirs))
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


class ConsoleInterface:
    """Интерфейс пользователя.

    Превращает аргументы командной строки в настройки и наборы данных. И тут также выводится
    информация в стандартный вывод по ходу анализа параметров скрипта.
    """
    __slots__ = 'options', '_layout'

    def __init__(self):
        parser = ArgumentParser(prog='catframes.py', description=DESCRIPTION,
            formatter_class=RawDescriptionHelpFormatter)

        self._add_input_arguments(parser)
        self._add_rendering_arguments(parser)
        self._add_output_arguments(parser)
        self._add_system_arguments(parser)

        parser.add_argument('--resolutions', action='store_true',
            help='show the resolution choosing process and exit')

        parser.add_argument('folders', metavar='FOLDER', nargs='+',
            help='folders with frames in the order of appearance in the video.')

        supported_suffixes = ', '.join(OutputOptions.get_supported_suffixes())
        parser.add_argument('destination', metavar='VIDEO',
            help=f'the output video file ({supported_suffixes}).')

        self.options = parser.parse_args()
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
        input_arguments.add_argument('--trim-start', metavar='FRAMES',
            type=cls._get_minmax_type(1),
            help='cut off some frames at the beginning')
        input_arguments.add_argument('--trim-end', metavar='FRAMES',
            type=cls._get_minmax_type(1),
            help='cut off some frames at the end')

    def _make_layout(self):
        h_positions = ('left', 0), ('right', 2)
        v_positions = ('top', 0), ('bottom', 2)
        middle = 1

        result = Layout()
        has_warning = False
        options_dict = vars(self.options)

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
            raise ValueError('At least one WARN overlay required.')

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

        overlay_help_head = 'overlay the text at the'

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
        def port_range_validator(arg):
            tip = 'It must be written in the format MinPort:MaxPort.'
            min_port = 1024
            if re.match('^\d+:\d+$', arg):
                nums = list(map(lambda x: int(x), arg.split(':')))
                if nums[0] > nums[1]:
                    raise ArgumentTypeError(tip)
                if min(nums) < min_port:
                    raise ArgumentTypeError(f'Port number must not be less than {min_port}.')
                return nums
            else:
                raise ArgumentTypeError(tip)

        system_arguments = parser.add_argument_group('System')
        system_arguments.add_argument('-p', '--port-range', metavar='X',
            default='10240:65535', type=port_range_validator,
            help='а range of ports that are allowed to be used ' + 
                'to interact with FFmpeg (default: %(default)s)')


    def show_options(self):
        """Чтобы пользователь видел, как проинтерпретированы его аргументы."""
        print()
        for key, value in vars(self.options).items():
            if isinstance(value, list):
                print(f'  {key}:')
                for item in value:
                    print(f'    - {item}')
            elif value:
                print(f'  {key}: {value}')
        print()

    def show_splitter(self):
        """Визуально отделить всё, что было выведено в консоль выше."""
        print(f"{'-'*42}\n")

    def get_input_sequence(self) -> Sequence[Frame]:
        """Возвращает отсортированную и пронумерованную последовательность кадров, которую попросил
        пользователь: параметры ``--trim-start`` и ``--trim-end`` уже применены.

        :raises ValueError: не удалось прочитать список файлов или в указанных директориях нет
            ни одного изображения.
        """
        print('Scanning for files...')
        image_groups = [
            FileUtils.list_images(Path(x))
            for x in self.options.folders
        ]

        print('Sorting the files...')
        for group in image_groups:
            FileUtils.sort_natural(group)

        print('Checking these images...')
        frame_groups = [
            [Frame(image) for image in group]
            for group in image_groups
        ]

        print('Numbering frames...')
        for folder_index, folder in enumerate(frame_groups):
            previous_folders = frame_groups[:folder_index]
            previous_frames = sum((len(x) for x in previous_folders))
            for frame_index, frame in enumerate(folder):
                number = 1 + frame_index
                frame.numdir = number
                frame.numdirs = previous_frames + number

        frames = functools.reduce(lambda x, y: x+y, frame_groups)

        print(f'\nThere are {len(frames)} frames in the folders.')

        trim_head = self.options.trim_start
        trim_tail = self.options.trim_end

        if trim_head:
            print(f'The first {trim_head} frame(s) will not be added.')
            frames = frames[trim_head:]

        if trim_tail:
            print(f'The last {trim_tail} frame(s) will not be added.')
            frames = frames[:-trim_tail]

        if not frames:
            raise ValueError('Error: empty frame set.')

        for frame_index, frame in enumerate(frames):
            frame.numvideo = 1 + frame_index

        print(f'Using {len(frames)} frames...\n')
        return frames

    def get_output_options(self) -> OutputOptions:
        """Возвращает настройки сохранения видео.

        :raises ValueError: пользователь указал файл с недопустимым расширением и т.п.
        """
        destination = Path(self.options.destination)

        if destination.is_dir():
            raise ValueError('Destination must not be a folder.')

        if destination.is_symlink():
            raise ValueError('Destination must not be a symbolic link.')

        if destination.suffix not in OutputOptions.get_supported_suffixes():
            raise ValueError('Unsupported destination file extension.')

        if self.options.quality == 'high':
            quality = Quality.HIGH
        elif self.options.quality == 'poor':
            quality = Quality.POOR
        else:
            quality = Quality.MEDIUM

        return OutputOptions(
            destination=destination,
            overwrite=bool(self.options.force),
            limit_seconds=self.options.limit,
            quality=quality,
            frame_rate=self.options.frame_rate)

    def get_server_options(self) -> JobServerOptions:
        return JobServerOptions(
            self.options.port_range[0],
            self.options.port_range[1]
        )

    @property
    def statistics_only(self) -> bool:
        """Пользователь не хочет пока делать видео, только посмотреть логику выбора разрешения."""
        return self.options.resolutions

    @property
    def margin_color(self) -> str:
        """В случае полупрозрачных кадров, это будет также цвет фона."""
        return self.options.margin_color

    @property
    def layout(self) -> Layout:
        """План наложения оверлеев."""
        return self._layout

    @staticmethod
    def list_resolutions(resolutions: ResolutionStatistics, limit:int = 10):
        """Перечислить разрешения от самых частых к самым редким."""
        lines = resolutions.sort_by_count_desc()
        assert limit > 0

        print('Resolutions:')
        for resolution, count in lines[:limit]:
            print(f"{resolution} => {count}")

        if len(lines) > limit:
            print('...')


def _main():
    try:
        if not shutil.which('ffmpeg'):
            raise ValueError('FFmpeg not found.')

        cli = ConsoleInterface()
        cli.show_options()
        cli.show_splitter()
        print(f'The number of overlays: {len(cli.layout)}\n')
        cli.show_splitter()

        output_options = cli.get_output_options()
        frames = cli.get_input_sequence()

        resolution_table = ResolutionStatistics(frames)
        cli.list_resolutions(resolution_table)

        resolution = resolution_table.choose()
        print(f'\nDecision: {resolution}\n')

        if cli.statistics_only:
            sys.exit(0)

        cli.show_splitter()
        del resolution_table

        processing_start = monotonic()
        view = DefaultFrameView(resolution, cli.margin_color, cli.layout)
        output_options.make(frames, view, cli.get_server_options())
        print(f'\nCompressed in {int(monotonic() - processing_start)} seconds.')

    except ValueError as err:
        print(f'\n{err}\n', file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    gc.set_threshold(100, 10, 10)   # По-умолчанию 700-10-10.
    _main()

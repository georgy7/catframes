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

    current_name = 'english'
    current_index = 0

    data = {  # языковые теги (ключи) имеют вид: "область.виджет"
        'english': {
            'root.title': 'CatFrames',
            'root.openSets': 'Settings',
            'root.newTask': 'Create',

            'bar.active': 'processing',
            'bar.inactive': 'complete', 
            'bar.btInfo': 'Info',
            'bar.btCancel': 'Cancel',
            'bar.btDelete': 'Delete',
            'bar.lbEmpty': 'Your projects will appear here',
            'bar.error.noffmpeg': 'Error! FFmpeg not found!',
            'bar.error.nocatframes': 'Error! Catframes not found!',
            'bar.error.internal': 'Internal process error!',
            'bar.error.failed': 'Error! Process start failed!',

            'sets.title': 'Settings',
            'sets.lbLang': 'Language:',
            'sets.lbPortRange': 'System ports range:',
            'sets.btApply': 'Apply',
            'sets.btSave': 'Save',

            'task.title': 'New Task',
            'task.initText': 'Add a directory of images',
            'task.lbColor': 'Background:',
            'task.lbFramerate': 'Framerate:',
            'task.lbQuality': 'Quality:',
            'task.cmbQuality': ('high', 'medium', 'poor'),
            'task.lbResolution': 'Render resolution:',
            'task.btCreate': 'Create',
            'task.lbCopy': 'Copy cli command:',
            'task.btCopy': 'Copy',

            'dirs.lbDirList': 'List of source directories:',
            'dirs.btAddDir': 'Add',
            'dirs.btRemDir': 'Remove',

            'warn.title': 'Warning',
            'warn.lbWarn': 'Warning!',
            'warn.lbText': 'Incomplete tasks!',
            'warn.btBack': 'Back',
            'warn.btExit': 'Leave',

            'noti.title': 'Error',
            'noti.lbWarn': 'Invalid port range!',
            'noti.lbText': 'The acceptable range is from 10240 to 65025',
            'noti.lbText2': 'The number of ports is at least 100',
            
        },
        'русский': {
            'root.title': 'CatFrames',
            'root.openSets': 'Настройки',
            'root.newTask': 'Создать',

            'bar.lbActive': 'обработка',
            'bar.lbInactive': 'завершено', 
            'bar.btInfo': 'Инфо',
            'bar.btCancel': 'Отмена',
            'bar.btDelete': 'Удалить',
            'bar.lbEmpty': 'Здесь появятся Ваши проекты',
            'bar.error.noffmpeg': 'Ошибка! FFmpeg не найден!',
            'bar.error.nocatframes': 'Ошибка! Catframes не найден!',
            'bar.error.internal': 'Внутренняя ошибка процесса!',
            'bar.error.failed': 'Ошибка при старте процесса!',

            'sets.title': 'Настройки',
            'sets.lbLang': 'Язык:',
            'sets.lbPortRange': 'Диапазон портов системы:',
            'sets.btApply': 'Применить',
            'sets.btSave': 'Сохранить',

            'task.title': 'Новая задача',
            'task.initText': 'Добавьте папку изображений',
            'task.lbColor': 'Цвет фона:',
            'task.lbFramerate': 'Частота кадров:',
            'task.lbQuality': 'Качество:',
            'task.cmbQuality': ('высокое', 'среднее', 'низкое'),
            'task.lbResolution': 'Разрешение рендера:',
            'task.btCreate': 'Создать',
            'task.lbCopy': 'Команда терминала:',
            'task.btCopy': 'Копировать',

            'dirs.lbDirList': 'Список директорий источников:',
            'dirs.btAddDir': 'Добавить',
            'dirs.btRemDir': 'Удалить',
            
            'warn.title': 'Внимание',
            'warn.lbWarn': 'Внимание!',
            'warn.lbText': 'Задачи не завершены!',
            'warn.btBack': 'Назад',
            'warn.btExit': 'Выйти',

            'noti.title': 'Ошибка',
            'noti.lbWarn': 'Неверный диапазон портов!',
            'noti.lbText': 'Допустимы значения от 10240 до 65025',
            'noti.lbText2': 'Количество портов не менее 100'
        },
    }

    @staticmethod  # получение всех доступных языков
    def get_all() -> tuple:
        return tuple(Lang.data.keys())

    @staticmethod  # установка языка по имени или индексу
    def set(name: str = None, index: int = None) -> None:

        if name and name in Lang.data:
            Lang.current_index = Lang.get_all().index(name)
            Lang.current_name = name

        elif isinstance(index, int) and 0 <= index < len(Lang.data):
            Lang.current_name = Lang.get_all()[index]
            Lang.current_index = index

    @staticmethod  # получение текста по тегу
    def read(tag) -> Union[str, tuple]:
        try:
            return Lang.data[Lang.current_name][tag]
        except KeyError:  # если тег не найден
            return '-----'
            

class PortSets:
    """Класс настроек диапазона портов
    системы для связи с ffmpeg."""

    min_port: int = 10240
    max_port: int = 65000

    @classmethod
    def set_range(cls, min_port: int, max_port: int) -> None:
        cls.min_port = min_port
        cls.max_port = max_port

    @classmethod
    def get_range(cls) -> Tuple:
        return cls.min_port, cls.max_port




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
        '--top-left',
        '--top',
        '--top-right',
        '--right',
        '--bottom-right',
        '--bottom',
        '--bottom-left',
        '--left',
    ]

    quality_names = ('high', 'medium', 'poor')

    def __init__(self) -> None:
                
        self._dirs: List[str] = []                    # пути к директориям с изображениями
        self._overlays: Dict[str, str] = {}           # словарь надписей
        self._color: str = DEFAULT_COLOR              # цвет отступов и фона
        self._framerate: int                          # частота кадров
        self._quality: str                            # качество видео
        self._quality_index: int = 0                  # номер значения качества
        self._limit: int                              # предел видео в секундах
        self._filepath: str                           # путь к итоговому файлу
        self._rewrite: bool = False                   # перезапись файла, если существует
        self._ports = PortSets.get_range()            # диапазон портов для связи с ffmpeg

    # установка директорий
    def set_dirs(self, dirs) -> list:
        self._dirs = dirs

    # установка оверлеев
    def set_overlays(self, overlays_texts: List[str]):
        # if any(s == "" for s in overlays_texts):
        #     empty = overlays_texts.index("")
        #     overlays_texts[empty] = "warn"

        self._overlays = dict(zip(self.overlays_names, overlays_texts))

    # установка цвета
    def set_color(self, color: str):
        self._color = color

    # установка частоты кадров, качества и лимита
    def set_specs(self, framerate: int, quality: int, limit: int = None):
        self._framerate = framerate
        self._quality_index = quality
        self._quality = self.quality_names[quality]
        self._limit = limit

    def set_resolution(self, width: int, height: int):
        self._resolution = width, height

    # установка пути файла
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

    # создание консольной команды в виде списка
    def convert_to_command(self) -> List[str]:
        command = ['catframes']
        if sys.platform == "win32":
            command = ['catframes.exe']
    
        # добавление текстовых оверлеев
        for position, text in self._overlays.items():
            if text:
                command.append(f'{position}="{text}"')
        
        command.append(f'--margin-color={self._color}')     # параметр цвета
        command.append(f"--frame-rate={self._framerate}")   # частота кадров
        command.append(f"--quality={self._quality}")        # качество рендера

        if self._limit:                                     # ограничение времени, если есть
            command.append(f"--limit={self._limit}")

        if os.path.isfile(self._filepath):                  # флаг перезаписи, если файл уже есть
            command.append("--force")

        command.append(f"--port-range={self._ports[0]}:{self._ports[1]}")  # диапазон портов
        
        for dir in self._dirs:                              # добавление директорий с изображениями
            command.append(dir)
        
        command.append(self._filepath)                      # добавление полного пути файла    
        return command                                      # возврат собранной команды


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
    def update(progress: float, delta: bool = False):
        """обновление полосы прогресса в окне"""
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
    """ Создаёт подпроцесс с запущенным catframes,
    создаёт отдельный поток для чтения порта api, 
    чтобы не задерживать обработку gui программы.
    По запросу может сообщать данные о прогрессе.
    """

    def __init__(self, command):

        # в зависимости от системы, дополнительные аргументы при создании процесса
        if sys.platform == 'win32':
            # для windows создание отдельной группы, чтобы завершить всё
            os_issues = {'creationflags': subprocess.CREATE_NEW_PROCESS_GROUP}
        else:
            # для unix создание процесса с новой сессией
            os_issues = {'preexec_fn': os.setsid}

        self.process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, **os_issues)  # запуск catframes

        self.error: Optional[str] = None
        self._progress = 0.0
        threading.Thread(target=self._update_progress, daemon=True).start()  # запуск потока обновления прогресса из вывода stdout
        # self._port = 0
        # threading.Thread(target=self._recognize_port, daemon=True).start()  # запуск потока распознования порта

    def _update_progress(self):  # обновление прогресса, чтением вывода stdout
        pattern = re.compile(r'Progress: +[0-9]+')

        for line in io.TextIOWrapper(self.process.stdout):  # читает строки вывода процесса
            if 'FFmpeg not found' in line:
                self.error = NO_FFMPEG_ERROR

            data = re.search(pattern, line)                 # ищет в строке процент прогресса
            if data:
                progress_percent = int(data.group().split()[1])  # если находит, забирает число
                if self._progress != 100:                  # если процент 100 - предерживает его
                    self._progress = progress_percent/100  # переводит чистый процент в сотые

        if self.process.poll() != 0 and not self.error:  # если процесс завершился некорректно
            self.error = INTERNAL_ERROR   # текст последней строки

        self._progress == 1.0         # полный прогресс только после завершения скрипта

    def get_progress(self):
        return self._progress

    # # получение порта api процесса
    # def _recognize_port(self):
    #     while not self._port:
    #         text = self.process.stdout.readline()
    #         if not 'port' in text:
    #             continue
    #         self._port = int(text.replace('port:', '').strip())

    # # возвращает прогресс (от 0.0 до 1.0), полученный от api процесса
    # def get_progress(self) -> float:
    #     if not self._port:  # если порт ещё не определён
    #         return 0.0

    #     try: # делает запрос на сервер, возвращает прогресс
    #         data = requests.get(f'http://127.0.0.1:{self._port}/progress', timeout=1).json()        
    #         return data['framesEncoded'] / data['framesTotal']
    #     except Exception:  # если сервер закрылся, возвращает единицу, т.е. процесс завершён
    #         return 1.0
        
    # убивает процесс (для экстренной остановки)
    def kill(self):
        if sys.platform == 'win32':  # исходя из системы, завершает семейство процессов
            self.process.send_signal(signal.CTRL_BREAK_EVENT)
        else:
            parent_pid = self.process.pid
            os.killpg(os.getppid(parent_pid), signal.SIGTERM)

    @classmethod
    def check_error(cls) -> bool:
        command = ['catframes']
        if sys.platform == 'win32':
            command = ['catframes.exe']
        try:
            proc = subprocess.Popen(command, stderr=subprocess.PIPE, text=True)
        except FileNotFoundError:
            print('\ncatframes не найден'.upper())
            return NO_CATFRAMES_ERROR
        if 'FFmpeg not found' in ''.join(proc.stderr.readlines()):
            return NO_FFMPEG_ERROR


class Task:
    """Класс самой задачи, связывающейся с catframes"""

    def __init__(self, id: int, task_config: TaskConfig) -> None:
        self.config = task_config
        self.command = task_config.convert_to_command()
        # print(self.command)

        # # !!! команда тестового api, а не процесса catframes
        # run_dir = os.path.dirname(os.path.abspath(__file__))
        # self.command = f'python {run_dir}/test_api/test_catframes_api.py'

        self._process_thread: CatframesProcess = None
        self.id = id  # получение уникального номера
        self.done = False  # флаг завершённости
        self.stop_flag = False  # требование остановки

    # запуск задачи
    def start(self, gui_callback: GuiCallback):  # инъекция зависимосей 
        self.gui_callback = gui_callback         # для оповещения наблюдателя
        TaskManager.reg_start(self)              # регистрация запуска

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
        while progress < 1.0 and not self.stop_flag:          # пока прогрес не завершён
            time.sleep(0.2)
            progress = self._process_thread.get_progress()    # получить инфу от потока с процессом
            self.gui_callback.update(progress)                # через ручку коллбека обновить прогрессбар

            if self._process_thread.error and not self.stop_flag:      # если процесс прервался не из-за юзера
                return self.handle_error(self._process_thread.error)   # обработает ошибку             
                
        # если всё завершилось корректно
        self.finish()  # обработает завершение

    # обработка ошибки процесса
    def handle_error(self, error: str):
        TaskManager.reg_finish(self)   # регистрация завершения
        self.gui_callback.set_error(   # сигнал об ошибке в ходе выполнения
            self.id,
            error=error
        )

    # обработка финиша задачи
    def finish(self):
        self.done = True  # ставит флаг завершения задачи
        TaskManager.reg_finish(self)       # регистрация завершения
        self.gui_callback.finish(self.id)  # сигнал о завершении задачи

    # остановка задачи
    def cancel(self):
        self.stop_flag = True
        TaskManager.reg_finish(self)
        self._process_thread.kill()        # убивает процесс
        self.gui_callback.delete(self.id)  # сигнал о завершении задачи

    def delete(self):
        TaskManager.wipe(self)
        self.gui_callback.delete(self.id)  # сигнал об удалении задачи


class TaskManager:
    """Менеджер задач.
    Позволяет регистрировать задачи,
    и управлять ими."""

    _last_id: int = 0          # последний номер задачи
    _all_tasks: dict = {}      # словарь всех задач
    _running_tasks: dict = {}  # словарь активных задач

    @classmethod
    def create(cls, task_config: TaskConfig) -> Task:
        cls._last_id += 1  # увеличение последнего номера задачи
        unic_id = cls._last_id  # получение уникального номера

        task = Task(unic_id, task_config)  # создание задачи
        cls._reg(task)  # регистрация в менеджере
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
    @classmethod                                         # принимает класс окна, имя окна
    def open(cls, window_cls, name: str, master: Optional[Tk] = None, **kwargs) -> Tk:    
        if not cls.check('root'):                        # проверяем, есть ли или корневое окно
            return cls._reg(window_cls(), 'root')        # регистрируем окно как корневое

        if not master:                                   # если мастер не был передан
            master = cls.call('root')                    # мастером будет корневое окно

        if not cls.check(name):                          # проверяем, зарегистрировано ли окно
            window = window_cls(root=master, **kwargs)   # создаём окно, передаём мастера
            cls._reg(window, name)                       # регистрируем окно
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
        if cls.check('warn') and not TaskManager.running_list():
            cls._all_windows['warn'].destroy()
            cls._all_windows.pop('warn')
        ...
    

class WindowMixin(ABC):
    """Абстрактный класс.
    Упрощает конструкторы окон."""

    title: Tk.wm_title        # эти атрибуты и методы объекта
    protocol: Tk.wm_protocol  # появятся автоматически при
    destroy: Tk.destroy       # наследовании от Tk или Toplevel

    size: Tuple[int, int]     # размеры (ширина, высота) окна
    name: str                 # имя окна для словаря всех окон
    widgets: Dict[str, ttk.Widget]  # словарь виджетов окна

    # настройка окна, вызывается через super в конце __init__ окна
    def _default_set_up(self):
        self.protocol("WM_DELETE_WINDOW", self.close)  # что выполнять при закрытии

        self._set_style()     # настройка внешнего вида окна
        self._to_center()     # размещение окна в центре экрана
        self._init_widgets()  # создание виджетов
        self.update_texts()   # установка текста нужного языка
        self._pack_widgets()  # расстановка виджетов

    # закрытие окна
    def close(self) -> None:
        # удаляет регистрацию окна из менеджера
        LocalWM.wipe(self.name)
        self.destroy()  # закрывает окно

    # обновление текстов всех виджетов окна, исходя из языка
    def update_texts(self) -> None:
        self.title(Lang.read(f'{self.name}.title'))

        for w_name, widget in self.widgets.items():

            if w_name.startswith('_'):  # если виджет начинается с "_", его обходит
                continue

            new_text_data = Lang.read(f'{self.name}.{w_name}')

            if w_name.startswith('cmb'): # если виджет это комбобокс
                widget.config(values=new_text_data)   
                widget.current(newindex=0)   
                continue    
            
            widget.config(text=new_text_data)

    # размещение окна в центре экрана (или родительского окна)
    def _to_center(self) -> None:

        # если это побочное окно
        if isinstance(self, Toplevel):
            x = self.master.winfo_x() + self.master.winfo_width()/2 - self.size[0]/2  # размещаем по центру
            y = self.master.winfo_y() + self.master.winfo_height()/2 - self.size[1]/2  # главного окна

        # а если это главное окно    
        else:  # размещаем по центру экрана
            x = (self.winfo_screenwidth() - self.size[0]) / 2
            y = (self.winfo_screenheight() - self.size[1]) / 2

        self.geometry(f'+{int(x)}+{int(y)}')


    # настройка стиля окна, исходя из разрешения экрана
    def _set_style(self) -> None:

        # screen_height = self.winfo_screenheight()  # достаём высоту экрана
        # scale = (screen_height/540)                # индекс масштабирования
        # scale *= MAJOR_SCALING                     # домножаем на глобальную

        style=ttk.Style()
        # if TTK_THEME: style.theme_use(TTK_THEME)   # применение темы, если есть
        _font = font.Font(
            # family= "helvetica", 
            size=12, 
            weight='bold'
        )
        style.configure(style='.', font=_font)  # шрифт текста в кнопке
        self.option_add("*Font", _font)  # шрифты остальных виджетов

        # создание стилей фона таскбара для разных состояний
        taskbar_colors = {'Running': '#cccccc', 'Error': '#ffcccc', 'Success': '#9afcab'}
        for status, color in taskbar_colors.items():
            style.configure(f'{status}.Task.TFrame', background=color)
            style.configure(f'{status}.Task.TLabel', background=color)
            style.configure(f'{status}.Task.Horizontal.TProgressbar', background=color)

        x, y = self.size                   # забираем объявленные размеры окна
        # x, y = int(x*scale), int(y*scale)  # масштабируем их
        self.geometry(f'{x}x{y}')          # и присваиваем их окну
        self.minsize(x, y)                 # и устанавливаем как минимальные
        try:
            x, y = self.size_max               # если есть максимальные размеры
            # x, y = int(x*scale), int(y*scale)  # масштабируем их
            self.maxsize(x, y)
        except AttributeError:
            pass



    # метод для создания и настройки виджетов
    @abstractmethod
    def _init_widgets(self) -> None:
        ...

    # метод для расположения виджетов
    @abstractmethod
    def _pack_widgets(self, ) -> None:
        ...





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
    img_list = [f for f in os.listdir(dir) if f.endswith(('.png', '.jpg'))]
    if full_path:
        img_list = list(map(lambda x: f'{dir}/{x}', img_list))  # добавляет путь к названию
    return img_list


# сокращает строку пути, расставляя многоточия внутри
def shrink_path(path: str, limit: int) -> str:
    if len(path) < limit:  # если длина и так меньше лимита
        return path

    # вычисление разделителя, добавление вначало, если нужно
    s = '/' if '/' in path else '\\'
    dirs = path.split(s)
    if path.startswith(s):
        dirs.pop(0)
        dirs[0] = s + dirs[0]

    # список укороченного пути, первый и последний элементы
    shrink = [dirs.pop(0), dirs.pop()] 
    while dirs and len(s.join(shrink) + dirs[-1]) + 4 < limit:  # если лимит не будет превышен,
        shrink.insert(1, dirs.pop())                            # добавить элемент с конца
    
    # сборка строки нового пути, передача её, если она короче изначальной
    new_path = f"{shrink[0]}{s}...{s}{s.join(shrink[1:])}"
    return new_path if len(new_path) < len(path) else path


class ScrollableFrame(ttk.Frame):
    """Прокручиваемый (умный) фрейм"""

    def __init__(self, root_window, *args, **kwargs):
        super().__init__(root_window, *args, **kwargs)
        
        self.root = root_window
        self.canvas = Canvas(self, highlightthickness=0)  # объект "холста"
        self.canvas.bind(           # привязка к виджету холста
            "<Configure>",          # обработчика событий, чтобы внутренний фрейм
            self._on_resize_window  # менял размер, если холст растягивается
            )

        self.scrollbar = ttk.Scrollbar(  # полоса прокрутки
            self, orient="vertical",     # установка в вертикальное положение
            command=self.canvas.yview,   # передача управления вертикальной прокруткой холста
        )  

        self.scrollable_frame = ttk.Frame(self.canvas, padding=[15, 0])  # фрейм для контента (внутренних виджетов)
        self.scrollable_frame.bind(  # привязка к виджету фрейма 
            "<Configure>",           # обработчика событий <Configure>, чтобы полоса
            self._on_frame_update,   # прокрутки менялась, когда обновляется фрейм 
        )

        # привязка холста к верхнему левому углу, получение id фрейма
        self.frame_id = self.canvas.create_window(
            (0, 0), 
            window=self.scrollable_frame, 
            anchor="nw"
        )

        # передача управления полосы прокрутки, когда холст движется от колёсика
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # упаковка виджетов
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # привязка и отвязка событий, когда курсор заходит на холст
        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)

        # создание надписи "здесь появятся Ваши проекты"
        self._empty_sign = ttk.Label(
            self.scrollable_frame,
            justify='center',
            font=("Arial", 18)
        )

        # первичное обновление полосы, чтобы сразу её не было видно
        self._update_scrollbar_visibility()

    # отрабатываывает при добавлении/удалении таскбаров в фрейм
    def _on_frame_update(self, event):
        self._update_scrollbar(event)
        self._update_empty_sign()

    # обновление видимости надписи "здесь появятся Ваши проекты" 
    def _update_empty_sign(self):
        if '!taskbar' in self.scrollable_frame.children.keys():
            self._empty_sign.pack_forget()  # если есть таскбары, удалить надпись
        else:
            self._empty_sign.pack(pady=80)  # если их нет - покажет её

    def update_texts(self):
        self._empty_sign.config(text=Lang.read('bar.lbEmpty'))

    # изменение размеров фрейма внутри холста
    def _on_resize_window(self, event):
        if event.width < 500:  # сюда залетают разные события
            return  # нас интересут только те, у которых ширина больше окна
        self.canvas.itemconfig(self.frame_id, width=event.width)  # новые размеры фрейма

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
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")


class TaskBar(ttk.Frame):
    """Класс баров задач в основном окне"""

    def __init__(self, master: ttk.Frame, task: Task, **kwargs):
        super().__init__(master, borderwidth=1, padding=5)
        self.name = 'bar'
        self.widgets: Dict[str, Widget] = {}
        self.task: Task = task
        self.progress: float = 0
        self.image: Image
        self.open_view: Callable = kwargs.get('view')  # достаёт ручку для открытия окна просмотра

        self._init_widgets()
        self.update_texts()
        self._pack_widgets()

    # установка стиля для прогрессбара
    def _set_style(self, style_id: int):
        styles = ['Running', 'Success', 'Error']
        style = styles[style_id]

        for elem in (self, self.left_frame, self.mid_frame, self.right_frame):
            elem.config(style=f'{style}.Task.TFrame')
        self.widgets['_lbData'].config(style=f'{style}.Task.TLabel')
        self.widgets['_lbPath'].config(style=f'{style}.Task.TLabel')
        self.widgets['_progressBar'].config(style=f'{style}.Task.Horizontal.TProgressbar')

    # создание и настрйока виджетов
    def _init_widgets(self):
        self.left_frame = ttk.Frame(self, padding=5)

        img_dir = self.task.config.get_dirs()[0]              # достаём первую директорию
        img_paths = find_img_in_dir(img_dir, full_path=True)  # берём все картинки из неё
        if len(img_paths) > 1:
            img_path = img_paths[len(img_paths)//2]           # выбираем центральную
        else:
            img_path = img_paths[0]

        image = Image.open(img_path)
        image_size = (80, 60)
        image = image.resize(image_size, Image.ADAPTIVE)
        image_tk = ImageTk.PhotoImage(image)

        self.widgets['_picture'] = ttk.Label(self.left_frame, image=image_tk)
        self.widgets['_picture'].image = image_tk


        # создании средней части бара
        self.mid_frame = ttk.Frame(self, padding=5)

        bigger_font = font.Font(size=16)

        # надпись в баре
        self.widgets['_lbPath'] = ttk.Label(  
            self.mid_frame, 
            font=bigger_font, padding=5,
            text=shrink_path(self.task.config.get_filepath(), 32), 
        )

        # создание локализованых строк "качество: высокое | частота кадров: 50"
        quality_index = self.task.config.get_quality()
        quality = Lang.read('task.cmbQuality')[quality_index]
        quality_text = f"{Lang.read('task.lbQuality')} {quality}  |  "
        framerate_text = f"{Lang.read('task.lbFramerate')} {self.task.config.get_framerate()}"

        self.widgets['_lbData'] = ttk.Label(
            self.mid_frame, 
            font='14', padding=5,
            text=quality_text+framerate_text, 
        )

        # создание правой части бара
        self.right_frame = ttk.Frame(self, padding=5)
       
        # кнопка "отмена"
        self.widgets['btCancel'] = ttk.Button(
            self.right_frame, 
            width=8, 
            command=lambda: self.task.cancel()
        )
        
        # полоса прогресса
        self.widgets['_progressBar'] = ttk.Progressbar(
            self.right_frame, 
            # length=320,
            maximum=1,
            value=0,
        )

        self._set_style(0)

        # каждый элемент таскбара при нажатии будет вызывать окно просмотра задачи
        self.bind("<Button-1>", lambda x: self.open_view(task_config=self.task.config))
        for w_name, w in self.widgets.items():
            if not 'bt' in w_name:  # привязка действий ко всем виджетам, кроме кнопок
                w.bind("<Button-1>", lambda x: self.open_view(task_config=self.task.config))


    # упаковка всех виджетов бара
    def _pack_widgets(self):
        self.widgets['_picture'].pack(side='left')
        self.left_frame.pack(side='left')

        self.widgets['_lbPath'].pack(side='top', fill='x', expand=True)
        self.widgets['_lbData'].pack(side='top', fill='x', expand=True)
        self.mid_frame.pack(side='left')

        self.widgets['_progressBar'].pack(side='top', expand=True)
        self.widgets['btCancel'].pack(side='bottom')
        self.right_frame.pack(side='left', expand=True)

        self.pack(pady=[0, 10])

    # изменение бара на "завершённое" состояние
    def finish(self):
        self._set_style(1)
        self.widgets['btDelete'] = self.widgets.pop('btCancel')  # переименование кнопки
        self.widgets['btDelete'].config(
            command=lambda: self.task.delete(),  # переопределение поведения кнопки
        )
        self.update_texts()  # обновление текста виджетов

    # изменение бара на состояние "ошибки"
    def set_error(self, error: str):
        self._set_style(2)
        self.widgets['btDelete'] = self.widgets.pop('btCancel')  # переименование кнопки
        self.widgets['btDelete'].config(
            command=lambda: self.task.delete(),  # переопределение поведения кнопки
        )
        self.widgets['_lbData'].config(text=Lang.read(f'bar.error.{error}'))
        self.update_texts()  # обновление текста виджетов

    # обновление линии прогресса
    def update_progress(self, progress: float, delta: bool = False):
        if delta:  # прогресс будет дополняться на переданное значение
            self.progress += progress
        else:  # прогресс будет принимать переданное значение
            self.progress = progress
        try:
            self.widgets['_progressBar'].config(value=self.progress)
        except:  # после удаления виджета вылетает ошибка из-за большой вложенности
            pass  # она ни на что не влияет, поэтому отлавливается и гасится

    # удаление бара
    def delete(self):
        self.destroy()

    # обновление текстов виджетов
    def update_texts(self):
        for w_name, widget in self.widgets.items():
            if not w_name.startswith('_'):
                widget.config(text=Lang.read(f'{self.name}.{w_name}'))


class ImageCanvas(Canvas):
    """Объект холста с картинкой в окне создания задачи.
    на которой отображаются "умные" поля ввода.
    Если текст не введён - поле будет полупрозрачным."""
    
    def __init__(
            self, 
            master: Tk, 
            veiw_mode: bool,
            overlays: list = None,
            background: str = '#888888'
        ):

        self.default_width = self.width = 800
        self.default_height = self.height = 400

        # создаёт объект холста
        super().__init__(master, width=self.width, height=self.height, highlightthickness=0, background=background)
        self.pack()
        
        self.view_mode = veiw_mode
        self.default_overlays = overlays

        self.sq_size = 24  # размер прозр. квадрата
        self.pil_img = None
        self.img = None
        self.img_id = None
        self.init_text = None

        self.color = background
        self.alpha_square = None

        self._create_image()
        self._create_entries()
        self._setup_entries()

    # обновляет разрешение холста
    # def update_resolution(self, resolution) -> int:
    #     ratio = resolution[0]/resolution[1]  # вычисляет соотношение сторон разрешения рендера
    #     last_height = self.height            # запоминает предыдущую высоту
    #     if self.width < self.default_width:
    #         self.width = self.default_width

    #     self.height = int(self.width/ratio)  # высота холста растягивается по соотношению
        
    #     if self.height > 600:                # но если высота больше 600
    #         self.height = 600                # то высота выставляется в 600
    #         self.width = int(self.height*ratio)  # а ширина выставляется по соотношению

    #     self.config(height=self.height, width=self.width)  # установка новых размеров

    #     self._setup_entries()                # обновляет позиции и настройки всех виджетов
    #     return self.height-last_height       # возвращает изменение высоты

    # позиционирует и привязывает обработчики позиций
    def _setup_entries(self):
        x_pad = int(self.width / 8)  # отступ по горизонтали, исходя из ширины холста
        y_pad = 50                   # отступ по вертикали статический

        positions = [
            (x_pad, y_pad),                             # верхний левый
            (self.width // 2, y_pad),                   # верхний
            (self.width - x_pad, y_pad),                # верхний правый
            (self.width - x_pad, self.height // 2),     # правый
            (self.width - x_pad, self.height - y_pad),  # нижний правый
            (self.width // 2, self.height - y_pad),     # нижний
            (x_pad, self.height - y_pad),               # нижний левый
            (x_pad, self.height // 2),                  # левый
        ]

        # позиционирует каждый виджет, привязывает обработчик
        for i, pos in enumerate(positions):
            self.coords(self.alpha_squares[i], pos[0]-self.sq_size/2, pos[1]-self.sq_size/2) 
            self.coords(self.labels[i], pos[0], pos[1])

            if not self.view_mode:
                # привязка события отображения поля ввода при нажатии на текст
                self.tag_bind(
                    self.labels[i], "<Button-1>", 
                    lambda event, pos=pos, entry=self.entries[i]: self._show_entry(event, pos, entry)
                )

            # привязка события скрытия поля ввода, когда с него снят фокус
            self.entries[i].bind(
                "<FocusOut>", 
                lambda event, entry=self.entries[i]: self._hide_entry(event, entry)
            )

    # инициализация полупрозрачнях треугольников и полей ввода
    def _create_entries(self):

        self.entries = []                      # список всех полей ввода
        self.shown = [None for i in range(8)]  # список отображаемых на холсте полей
        self.labels = []                       # надписи, отражающие "+" или текст
        self.alpha_squares = []                # полупрозрачные квадраты

        # создание прозрачного квадрата
        self.alpha_square = self._create_alpha_square(self.sq_size, '#ffffff', 0.5)

        # создание значка "+" и виджетов
        for i in range(8):
            """У всех объектов здесь нулевые координаты. 
            Позже их позиции обновит метод sefl._setup_entries"""

            # добавление полупрозрачного квадрата
            square = self.create_image(0, 0, image=self.alpha_square, anchor='nw')

            # добавление текста
            label = self.create_text(0, 0, text='+', font=("Arial", 24), justify='center')  

            # инициализация поля ввода
            entry = Entry(self, font=("Arial", 12), justify='center')  
            
            if self.view_mode:  # если это режим просмотра, заполняет поля ввода текстом
                entry.insert(0, self.default_overlays[i])

            # записывает сущности в их словари
            self.alpha_squares.append(square)
            self.entries.append(entry) 
            self.labels.append(label)
    
    # создаёт картинку прозрачного квадрата
    def _create_alpha_square(self, size: int, fill: str, alpha: float):
        alpha = int(alpha * 255)
        fill = self.winfo_rgb(fill) + (alpha,)
        image = Image.new('RGBA', (size, size), fill)
        return ImageTk.PhotoImage(image)

    # отображает поле ввода
    def _show_entry(self, event, pos, entry):
        index = self.entries.index(entry)
        entry_window = self.create_window(pos, window=entry, anchor=CENTER)
        self.shown[index] = entry_window
        entry.focus_set()

    # прячет поле ввода, меняет текст в лейбле
    def _hide_entry(self, event, entry):
        index = self.entries.index(entry)
        self.delete(self.shown[index])     # удаляет поле ввода
        self._update_label(index)

    # обновляет тексты лейблов и видимость квадрата
    def _update_label(self, index):
        label = self.labels[index]
        entry = self.entries[index]
        square = self.alpha_squares[index]

        text = '+'              # дефолтные значения, когда поле ввода пустое 
        font = ("Arial", 24)
        square_state = 'normal'
        label_color = 'black'

        if entry.get() or self.view_mode:  # если в поле ввода указан какой-то текст
            text = entry.get()       # этот текст будет указан в лейбле
            font = ("Arial", 16)     # шрифт будет поменьше
            square_state = 'hidden'  # полупрозрачный квадрат будет скрыт

            dark_background = self._is_dark_background(label)      # проверится, тёмный ли фон у тейбла
            label_color = 'white' if dark_background else 'black'  # если тёмный - шрифт светлый, и наоборот

        self.itemconfig(label, text=text, font=font, fill=label_color)  # придание тексту нужных параметров
        self.itemconfig(square, state=square_state)                     # скрытие или проявление квадрата

    # приобразование ссылки на картинку в объект
    def _open_image(self, image_link: str):
        try:
            pil_img = Image.open(image_link)               # открытие изображения по пути
            img_ratio = pil_img.size[0] / pil_img.size[1]  # оценка соотношения сторон картинки
            pil_img = pil_img.resize(
                (int(self.height*img_ratio), self.height), # масштабирование с учётом соотношения
                Image.LANCZOS
            )  
            self.pil_img = pil_img
            self.img = ImageTk.PhotoImage(pil_img)         # загрузка картинки и создание виджета
            
            if self.init_text:                             # если есть надпись "добавьте картинку"
                self.delete(self.init_text)                # то удаляет её
                self.init_text = None

        except (FileNotFoundError, AttributeError):        # если файл не найден
            self.set_empty()                               # создаёт пустую картинку

    # создание пустого изображения, и надписи "добавьте картинки"
    def set_empty(self):
        self.img = ImageTk.PhotoImage(                                  # создаёт пустое изображение
            Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))  # с прозрачным фоном
        )
        if not self.init_text:                             # если нет надписи добавьте картинку
            self.init_text = self.create_text(             # то добавляет её 
                self.width/2, self.height/2,               # по центру холста
                font=("Arial", 24), justify='center'
            )
            self.update_texts()                            # и обновляет тексты

    # создание изображения
    def _create_image(self, image_link: str = None):
        self._open_image(image_link)
        self.img_id = self.create_image((self.width//2)-(self.img.width()//2), 0, anchor=NW, image=self.img)

        # привязка фокусировки на холст при нажатие на изображение, чтобы снять фокус с полей ввода
        self.tag_bind(self.img_id, "<Button-1>", lambda event: self.focus_set())

    # обновление изображения 
    def update_image(self, image_link: str):
        self._open_image(image_link)
        self.itemconfig(self.img_id, image=self.img)                            # замена изображения
        self.coords(self.img_id, (self.width // 2)-(self.img.width() // 2), 0)  # повторное задание координат
        for i in range(8):
            self._update_label(i)

    # проверка, тёмный ли фон на картинке за элементом канваса
    def _is_dark_background(self, elem_id: int) -> bool:
        try:
            image_shift = self.coords(self.img_id)[0]   # сдвиг картинки от левого края холста
            x, y = self.coords(elem_id)                 # координаты элемента на холсте
            x -= int(image_shift)                       # поправка, теперь это коорд. элемента на картинке
            if x < 0:
                raise IndexError                        # если координата меньше нуля

            color = self.pil_img.getpixel((x, y))       # цвет пикселя картинки на этих координатах
            r, g, b = color[0:3]
        except TypeError:                               # если pillow вернёт не ргб, а яркость пикселя
            return color < 128
        except Exception:                               # если пиксель за пределами картинки
            r, g, b = self.winfo_rgb(self.color)        # задний план будет оцениваться, исходя из
            r, g, b = r/255, g/255, b/255               # выбранного фона холста
            
        brightness = (r*299 + g*587 + b*114) / 1000     # вычисление яркости пикселя по весам
        return brightness < 128                         # сравнение яркости

    # формирует список из восьми строк, введённых в полях
    def fetch_entries_text(self) -> list:
        entries_text = map(lambda entry: entry.get(), self.entries)
        return list(entries_text)
    
    # обновляет цвета отступов холста
    def update_background_color(self, color: str):
        self.color = color
        self.config(background=color)

    # обновление
    def update_texts(self):
        if self.init_text:
            self.itemconfig(self.init_text, text=Lang.read('task.initText'))


class DirectoryManager(ttk.Frame):
    """Менеджер директорий, поле со списком.
    Даёт возможность добавлять, удалять директории, 
    и менять порядок кнопками и перетаскиванием"""

    def __init__(self, master: Union[Tk, Frame], veiw_mode: bool, dirs: list):
        super().__init__(master)
        self.name = 'dirs'

        self.widgets: Dict[str, Widget] = {}
        self.drag_data = {"start_index": None, "item": None}

        self.veiw_mode = veiw_mode
        self._init_widgets()
        self._pack_widgets()

        self.dirs = dirs
        for dir in dirs:
            self.listbox.insert(END, shrink_path(dir, 35))

    # возвращает список директорий
    def get_dirs(self) -> list:
        return self.dirs[:]
    
    def get_all_imgs(self) -> list:
        images = []
        for dir in self.dirs:
            images += find_img_in_dir(dir, full_path=True)
        return images

    # подсветка виджета пути цветом предупреждения
    def _highlight_invalid_path(self, path_number: list):
        print(f'TODO подсветка несуществующего пути {path_number}')

    # подсветка кнопки добавления пути цветом предупреждения
    def _highlight_empty_path(self):
        print(f'TODO подсветка кнопки добавления пути')
    
    # проверка путей на валидность, передача в конфиг
    def validate_dirs(self) -> bool:
        if not self.dirs:
            self._highlight_empty_path()
            return False
        
        ok_flag = True  # вызовет подсветку несуществующих путей
        for i, dir in enumerate(self.dirs):
            if not os.path.isdir(dir):
                self._highlight_invalid_path(i)
                ok_flag = False

        return ok_flag

    # инициализация виджетов
    def _init_widgets(self):

        self.top_frame = Frame(self)

        self.widgets['lbDirList'] = ttk.Label(self.top_frame)  # надпись "Список директорий:"

        # создание списка и полосы прокрутки
        self.listbox = Listbox(self.top_frame, selectmode=SINGLE, width=28, height=4)
        self.scrollbar = ttk.Scrollbar(self.top_frame, orient="vertical", command=self.listbox.yview)
        self.listbox.config(yscrollcommand=self.scrollbar.set)

        if not self.veiw_mode:
            self.listbox.bind('<Button-1>', self._start_drag)
            self.listbox.bind('<B1-Motion>', self._do_drag)

        # добавление директории
        def add_directory():
            dir_name = filedialog.askdirectory(parent=self)
            if not dir_name or dir_name in self.dirs:
                return
            
            if not find_img_in_dir(dir_name):
                return

            self.listbox.insert(END, shrink_path(dir_name, 35))
            self.dirs.append(dir_name)  # добавление в список директорий

        # удаление выбранной директории из списка
        def remove_directory():
            selected = self.listbox.curselection()
            if selected:
                index = selected[0]
                self.listbox.delete(index)
                del self.dirs[index]

        self.button_frame = Frame(self)

        # создание кнопок для управления элементами списка
        self.widgets['btAddDir'] = ttk.Button(self.button_frame, width=8, command=add_directory)
        self.widgets['btRemDir'] = ttk.Button(self.button_frame, width=8, command=remove_directory)
        # self.widgets['btUpDir'] = ttk.Button(self.button_frame, width=2, text="^", command=self._move_up)
        # self.widgets['btDownDir'] = ttk.Button(self.button_frame, width=2, text="v", command=self._move_down)
    
    # начало перетаскивания элемента
    def _start_drag(self, event):
        self.drag_data["start_index"] = self.listbox.nearest(event.y)
        self.drag_data["item"] = self.listbox.get(self.drag_data["start_index"])

    def _swap_dirs(self, index_old: int, index_new: int, text: str = None):
        if not text:
            text = self.listbox.get(index_old)
        self.listbox.delete(index_old)
        self.listbox.insert(index_new, text)
        self.dirs[index_old], self.dirs[index_new] = self.dirs[index_new], self.dirs[index_old]

    # процесс перетаскивания элемента
    def _do_drag(self, event):
        new_index = self.listbox.nearest(event.y)
        if new_index != self.drag_data["start_index"]:
            self._swap_dirs(self.drag_data["start_index"], new_index, self.drag_data["item"])
            self.drag_data["start_index"] = new_index

    # перемещение выбранной директории вверх по списку
    def _move_up(self):
        selected = self.listbox.curselection()
        if selected:
            index = selected[0]
            if index > 0:
                self._swap_dirs(index, index-1)
                self.listbox.select_set(index - 1)

    # перемещение выбранной директории вниз по списку
    def _move_down(self):
        selected = self.listbox.curselection()
        if selected:
            index = selected[0]
            if index < self.listbox.size() - 1:
                self._swap_dirs(index, index+1)
                self.listbox.select_set(index + 1)

    # размещение виджетов
    def _pack_widgets(self):
        self.top_frame.pack(side='top', fill='x')
        self.widgets['lbDirList'].pack(side='top', anchor='w')
        self.listbox.pack(side='left', fill='x')
        self.scrollbar.pack(side='left', fill='y')


        self.button_frame.pack(side='top', anchor='w', pady=10)

        if not self.veiw_mode:
            self.widgets['btAddDir'].pack(side='left', padx=(0, 10))
            self.widgets['btRemDir'].pack(side='right')
        # self.widgets['btUpDir'].pack(side='left')  # кнопки перетаскивания 
        # self.widgets['btDownDir'].pack(side='left') # вверх и вниз, пока убрал

    def update_texts(self):
        for w_name, widget in self.widgets.items():
            if not w_name.startswith('_'):
                widget.config(text=Lang.read(f'{self.name}.{w_name}'))






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
а тексты для них прописываться в классе языковых настроек Lang.
Если появляется более сложная композиция, метод update_texts должен
быть расширен так, чтобы вызывать обновление текста во всех виджетах.
"""


class RootWindow(Tk, WindowMixin):
    """Основное окно"""

    def __init__(self):
        super().__init__()
        self.name = 'root'
        
        self.widgets:   Dict[str, ttk.Widget] = {}
        self.task_bars: Dict[int, TaskBar] = {}  # словарь регистрации баров задач

        self.size = 550, 450
        self.size_max = 700, 700
        self.resizable(True, True)  # можно растягивать

        super()._default_set_up()

    # при закрытии окна
    def close(self):
        if TaskManager.running_list():  # если есть активные задачи
            # открытие окна с новой задачей (и/или переключение на него)
            return LocalWM.open(WarningWindow, 'warn').focus()
        self.destroy()

    # создание и настройка виджетов
    def _init_widgets(self):

        # открытие окна с новой задачей (и/или переключение на него)
        def open_new_task():
            LocalWM.open(NewTaskWindow, 'task').focus()

        # открытие окна настроек (и/или переключение на него)
        def open_settings():
            LocalWM.open(SettingsWindow, 'sets').focus()

        # создание фреймов
        self.upper_bar = upperBar = ttk.Frame(self)  # верхний бар с кнопками
        self.task_space = ScrollableFrame(self)  # пространство с прокруткой
        self.taskList = self.task_space.scrollable_frame  # сокращение пути для читаемости

        # создание виджетов, привязывание функций
        self.widgets['newTask'] = ttk.Button(upperBar, command=open_new_task)
        self.widgets['openSets'] = ttk.Button(upperBar, command=open_settings)

    # расположение виджетов
    def _pack_widgets(self):
        self.upper_bar.pack(fill='x', padx=15, pady=15)
        self.task_space.pack(fill='both', expand=True)

        self.widgets['newTask'].pack(side='left')
        self.widgets['openSets'].pack(side='right')
        
    # добавление строки задачи
    def add_task_bar(self, task: Task, **params) -> Callable:
        task_bar = TaskBar(self.taskList, task, **params)  # создаёт бар задачи
        self.task_bars[task.id] = task_bar  # регистрирует в словаре
        return task_bar.update_progress  # возвращает ручку полосы прогресса

    # удаление строки задачи
    def del_task_bar(self, task_id: int) -> None:
        if task_id in self.task_bars:
            self.task_bars[task_id].delete()  # удаляет таскбар
            del self.task_bars[task_id]  # чистит регистрацию

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
        self.task_space.update_texts()  # обновляет текст в основном поле
        for bar in self.task_bars.values():
            bar.update_texts()  # обновляет текст в каждом баре


class SettingsWindow(Toplevel, WindowMixin):
    """Окно настроек"""

    def __init__(self, root: RootWindow):
        super().__init__(master=root)
        self.name = 'sets'

        self.widgets: Dict[str, ttk.Widget] = {}

        self.size = 250, 200
        self.resizable(False, False)

        super()._default_set_up()

    # создание и настройка виджетов
    def _init_widgets(self):

        # создание виджетов, привязывание функций
        self.widgets['lbLang'] = ttk.Label(self)
        self.widgets['_cmbLang'] = ttk.Combobox(  # виджет выпадающего списка
            self,
            values=Lang.get_all(),  # вытягивает список языков
            state='readonly',  # запрещает вписывать, только выбирать
            width=7,
        )

        def validate_numeric(new_value):  # валидация ввода, разрешены только цифры и пустое поле
            return new_value.isnumeric() or not new_value
        
        v_numeric = (self.register(validate_numeric), '%P')  # регистрация валидации

        self.widgets['lbPortRange'] = ttk.Label(self)
        self.widgets['_entrPortFirst'] = ttk.Entry(  # поле ввода начального порта
            self, 
            justify='center', 
            validate='key', 
            validatecommand=v_numeric  # привязка валидации
        )
        self.widgets['_entrPortLast'] = ttk.Entry(  # поле ввода конечного порта
            self, 
            justify='center', 
            validate='all',
            validatecommand=v_numeric  # привязка валидации
        )
        
        # применение настроек
        def apply_settings():
            Lang.set(index=self.widgets['_cmbLang'].current())  # установка языка
            for w in LocalWM.all():  # перебирает все прописанные в менеджере окна
                w.update_texts()  # для каждого обновляет текст методом из WindowMixin

            try:  # проверка введённых значений, если всё ок - сохранение
                port_first = int(self.widgets['_entrPortFirst'].get())
                port_last = int(self.widgets['_entrPortLast'].get())
                assert(port_last-port_first >= 100)         # диапазон не меньше 100 портов
                assert(port_first >= 10240)                 # начальный порт не ниже 10240
                assert(port_last <= 65025)                  # конечный порт не выше 65025
                PortSets.set_range(port_first, port_last)   # сохранение настроек

            except:  # если какое-то из условий не выполнено
                self._set_ports_default()  # возврат предыдущих значений виджетов
                LocalWM.open(NotifyWindow, 'noti', master=self)  # окно оповещения

        # сохранение настроек (применение + закрытие)
        def save_settings():
            apply_settings()
            self.close()

        self.widgets['btApply'] = ttk.Button(self, command=apply_settings, width=7)
        self.widgets['btSave'] = ttk.Button(self, command=save_settings, width=7)

    # установка полей ввода портов в последнее сохранённое состояние
    def _set_ports_default(self):
        self.widgets['_entrPortFirst'].delete(0, 'end')
        self.widgets['_entrPortFirst'].insert(0, PortSets.get_range()[0])
        self.widgets['_entrPortLast'].delete(0, 'end')
        self.widgets['_entrPortLast'].insert(0, PortSets.get_range()[1])

    # расположение виджетов
    def _pack_widgets(self):

        for c in range(2): 
            self.columnconfigure(index=c, weight=1)
        for r in range(7): 
            self.rowconfigure(index=r, weight=1)
        
        self.widgets['lbLang'].grid(row=0, column=0, sticky='ws', padx=15)
        self.widgets['_cmbLang'].grid(columnspan=1, row=1, column=0, sticky='wne', padx=(15 ,5))
        self.widgets['_cmbLang'].current(newindex=Lang.current_index)  # подставляем в ячейку текущий язык

        self.widgets['lbPortRange'].grid(columnspan=2, row=2, column=0, sticky='ws', padx=15)
        self.widgets['_entrPortFirst'].grid(row=3, column=0, sticky='wn', padx=(15, 5))
        self.widgets['_entrPortLast'].grid(row=3, column=1, sticky='wn', padx=(5, 15))
        self._set_ports_default()  # заполняем поля ввода портов

        self.widgets['btApply'].grid(row=6, column=0, sticky='ew', padx=(15, 5), ipadx=30, pady=10)
        self.widgets['btSave'].grid(row=6, column=1, sticky='ew', padx=(5, 15), ipadx=30, pady=10)


class NewTaskWindow(Toplevel, WindowMixin):
    """Окно создания новой задачи"""

    def __init__(self, root: RootWindow, **kwargs):
        super().__init__(master=root)
        self.name = 'task'
        self.widgets: Dict[str, Widget] = {}

        self.task_config = TaskConfig()
        self.view_mode: bool = False
        if kwargs.get('task_config'):  # если передан конфиг, берёт его
            self.task_config: TaskConfig = kwargs.get('task_config')
            self.view_mode: bool = True  # устанавливает флаг "режима просмотра"

        self.framerates = (60, 50, 40, 30, 25, 20, 15, 10, 5)  # список доступных фреймрейтов

        self.size = 800, 650
        self.resizable(True, True)

        super()._default_set_up()

        self.image_updater_thread = threading.Thread(target=self.canvas_updater, daemon=True)
        self.image_updater_thread.start()

    # поток, обновляющий картинку на на холсте
    def canvas_updater(self):
        last_dirs = []       # копия списка последних директорий
        images_to_show = []  # список картинок для показа
        index = 0            # индекс картинки в этом списке

        while True:
            
            # проверяет, поменялись ли директории
            new_dirs = self.dir_manager.get_dirs()
            if last_dirs != new_dirs:  # если поменялись
                last_dirs = new_dirs   # запоминает их

                # забирает список всех картинок
                all_images = self.dir_manager.get_all_imgs()

                # вычисляет шаг индекса (если катинок меньше 4ёх, то step == 0)
                step = int(len(all_images)/4)

                # обновляет список картинок для показа
                if step:   
                    # берёт срез списка картинок, с нужным шагом
                    images_to_show = all_images[step::step]
                else:  
                    # если картинок было меньше 4ёх, берёт весь список 
                    images_to_show = all_images[:]
                    index = 0  # обновляет индекс, чтобы
                
            # блок работы с холстом
            try:  
                if images_to_show:
                    # если список не пуст, передаёт холсту следующую
                    self.image_canvas.update_image(images_to_show[index])
                    index = (index + 1) % len(images_to_show)  # инкремент
                else:
                    # показывает на холсте надпись "выберите картинку"
                    self.image_canvas.set_empty()  
                time.sleep(4)

            except TclError:  # это исключение появится, когда окно закроется
                return

    # сбор данных из виджетов, создание конфигурации
    def _collect_task_config(self) -> None:
        overlays = self.image_canvas.fetch_entries_text()       # достаёт тексты оверлеев из виджетов,
        self.task_config.set_overlays(overlays_texts=overlays)  # передаёт их в конфиг задачи оверлеев.

        self.task_config.set_specs(
            framerate=self.widgets['_cmbFramerate'].get(),  # забирает выбранное значение в комбобоксе
            quality=self.widgets['cmbQuality'].current(),   # а в этом забирает индекс выбранного значения
        )
    
    # выбор пути для сохранения файла
    def _set_filepath(self) -> bool:
        filepath = filedialog.asksaveasfilename(
                parent=self,                                                # открытие окна сохранения файла
                filetypes=[("mp4 file", ".mp4"), ("webm file", ".webm")],   # доступные расширения и их имена
                defaultextension=".mp4"                                     # стандартное расширение
        )
        self.task_config.set_filepath(filepath)
        return bool(filepath)  # если путь выбран, вернёт true

    # создание и запуск задачи
    def _create_task_instance(self):

        # создание задачи через менеджер задач
        task = TaskManager.create(self.task_config)

        # создание бара задачи, получение метода обновления прогресса
        update_progress: Callable = self.master.add_task_bar(task, view=NewTaskWindow.open_view)

        gui_callback = GuiCallback(                         # создание колбека
            update_function=update_progress,                # передача методов обновления,
            finish_function=self.master.finish_task_bar,    # завершения задачи
            error_function=self.master.handle_error,        # обработки ошибки выполнения
            delete_function=self.master.del_task_bar,       # и удаления бара
        )

        task.start(gui_callback)  # инъекция колбека для обнволения gui при старте задачи

    # создание и настройка виджетов
    def _init_widgets(self):

        self.image_canvas = ImageCanvas(  # создание холста с изображением
            self, 
            veiw_mode=self.view_mode,
            overlays=self.task_config.get_overlays(),
            background=self.task_config.get_color(),
        )

        self.bottom_grid = Frame(self)    # создание табличного фрейма ниже холста
        self.dir_manager = DirectoryManager(
            self.bottom_grid, 
            veiw_mode=self.view_mode,
            dirs=self.task_config.get_dirs() 
        )

        self.settings_grid = Frame(self.bottom_grid)  # создание фрейма настроек в нижнем фрейме
        
        def add_task():  # обработка кнопки добавления задачи
            self._collect_task_config()   # сбор данных конфигурации с виджетов
            if not self.dir_manager.validate_dirs(): # если каких-то директорий нет,
                return                    # дальнейшие действия не произойдут
            
            dirs = self.dir_manager.get_dirs()
            self.task_config.set_dirs(dirs)

            if not self._set_filepath():  # если путь сохранения не выбирается,
                return                    # дальнейшие действия не произойдут
            self._create_task_instance()  # cоздание и запуск задачи
            self.close()                  # закрытие окна создания задачи

        def ask_color():  # вызов системного окна по выбору цвета
            color = colorchooser.askcolor(parent=self)[-1]
            self.image_canvas.update_background_color(color)
            self.task_config.set_color(color)  # установка цвета в конфиге
            self.widgets['_btColor'].configure(background=color, text=color)  # цвет кнопки

        def copy_to_clip():  # копирование команды в буфер обмена
            command = ' '.join(self.task_config.convert_to_command())
            self.clipboard_clear()
            self.clipboard_append(command)

        # виджеты столбца описания кнопок
        self.widgets['lbColor'] = ttk.Label(self.settings_grid)
        self.widgets['lbFramerate'] = ttk.Label(self.settings_grid)
        self.widgets['lbQuality'] = ttk.Label(self.settings_grid)

        # виджеты правого столбца (кнопка цвета, комбобоксы и кнопка создания задачи)
        self.widgets['_btColor'] = Button(self.settings_grid, command=ask_color, text=DEFAULT_COLOR, width=7)
        if self.view_mode:
            color = self.task_config.get_color()
            self.widgets['_btColor'].configure(background=color, text=color)  # цвет кнопки

        self.widgets['_cmbFramerate'] = ttk.Combobox(  # виджет выбора фреймрейта
            self.settings_grid,
            values=self.framerates, 
            state='readonly',
            justify='center',
            width=8,
        )
        self.widgets['_cmbFramerate'].set(  # установка начального значения в выборе фреймрейта
            self.task_config.get_framerate() if self.view_mode else 30
        )

        self.widgets['cmbQuality'] = ttk.Combobox(  # виджет выбора качества
            self.settings_grid,
            state='readonly',
            justify='center',
            width=8,
        )

        self.widgets['btCreate'] = ttk.Button(self.settings_grid, command=add_task)

        # лейбл и кнопка копирования команды
        self.widgets['lbCopy'] = ttk.Label(self.settings_grid)
        self.widgets['btCopy'] = ttk.Button(self.settings_grid, command=copy_to_clip)

        if self.view_mode:  # если это режим просмотра, все виджеты, кроме копирования - недоступны
            for w_name, w in self.widgets.items():
                if ('lb') in w_name or ('Copy') in w_name:
                    continue
                w.configure(state='disabled')

    # расположение виджетов
    def _pack_widgets(self):
        # упаковка нижнего фрейма для сетки
        self.bottom_grid.pack(side='bottom', fill='both', expand=True, pady=10, padx=100)

        for i in range(2):  # настройка веса столбцов
            self.bottom_grid.columnconfigure(i, weight=1)

        for i in range(3):  # настройка веса строк
            self.bottom_grid.rowconfigure(i, weight=1)

        # левый и правый столбцы нижнего фрейма
        self.dir_manager.grid(row=1, column=0)    # левый столбец - менеджер директорий
        self.settings_grid.grid(row=1, column=1)  # правый - фрейм настроек

        # подпись и кнопка цвета       
        self.widgets['lbColor'].grid(row=1, column=0, sticky='e', padx=10, pady=5)
        self.widgets['_btColor'].grid(row=1, column=1, sticky='w', padx=7, pady=5)

        # подпись и комбобокс частоты
        self.widgets['lbFramerate'].grid(row=2, column=0, sticky='e', padx=10, pady=5)
        self.widgets['_cmbFramerate'].grid(row=2, column=1, sticky='w', padx=7, pady=5)

        # подпись и комбобокс качества
        self.widgets['lbQuality'].grid(row=3, column=0, sticky='e', padx=10, pady=5)
        self.widgets['cmbQuality'].grid(row=3, column=1, sticky='w', padx=7, pady=5)

        # в режиме просмотра
        if self.view_mode:  # подпись и кнопка копирования команды
            self.widgets['lbCopy'].grid(row=4, column=0, sticky='e', padx=10, pady=5)
            self.widgets['btCopy'].grid(row=4, column=1, sticky='w', padx=7, pady=5)
        else:  # кнопка создания задачи
            self.widgets['btCreate'].grid(row=4, column=1, sticky='w', padx=7, pady=5)

    # расширение метода обновления текстов
    def update_texts(self) -> None:
        super().update_texts()
        self.dir_manager.update_texts()
        self.image_canvas.update_texts()
        # установка начального значения в выборе качества
        self.widgets['cmbQuality'].current(newindex=self.task_config.get_quality())

    @staticmethod  # открытие окна в режиме просмотра
    def open_view(task_config: TaskConfig):
        LocalWM.open(NewTaskWindow, 'task', task_config=task_config)


class WarningWindow(Toplevel, WindowMixin):
    """Окно предупреждения при выходе"""

    def __init__(self, root: RootWindow):
        super().__init__(master=root)
        self.name = 'warn'
        self.widgets: Dict[str, Widget] = {}

        self.size = 260, 130
        self.resizable(False, False)

        super()._default_set_up()

    # создание и настройка виджетов
    def _init_widgets(self):
        
        def back():
            self.close()

        def exit():
            for task in TaskManager.running_list():
                task.cancel()
            self.master.destroy()

        _font = font.Font(size=16)

        # два лейбла предупреждения (с крупным текстом, и обычным)
        self.widgets['lbWarn'] = ttk.Label(self, padding=[0, 20, 0, 5], font=_font)
        self.widgets['lbText'] = ttk.Label(self, padding=0)

        # кнопки "назад" и "выйти"
        self.choise_frame = ttk.Frame(self)
        self.widgets['btBack'] = ttk.Button(self.choise_frame, command=back)
        self.widgets['btExit'] = ttk.Button(self.choise_frame, command=exit)

    # расположение виджетов
    def _pack_widgets(self):
        self.widgets['lbWarn'].pack(side='top')
        self.widgets['lbText'].pack(side='top')

        self.widgets['btBack'].pack(side='left', anchor='w', padx=5)
        self.widgets['btExit'].pack(side='left', anchor='w', padx=5)
        self.choise_frame.pack(side='bottom', pady=10)


class NotifyWindow(Toplevel, WindowMixin):
    """Окно предупреждения о портах в настройках"""

    def __init__(self, root: Toplevel):
        super().__init__(master=root)
        self.name = 'noti'
        self.widgets: Dict[str, Widget] = {}

        self.size = 350, 160
        self.resizable(False, False)

        super()._default_set_up()

    # создание и настройка виджетов
    def _init_widgets(self):
        
        _font = font.Font(size=16)

        # три лейбла (один с крупным текстом, два с и обычным)
        self.widgets['lbWarn'] = ttk.Label(self, padding=[0, 20, 0, 5], font=_font)
        self.widgets['lbText'] = ttk.Label(self, padding=0)
        self.widgets['lbText2'] = ttk.Label(self, padding=0)

        # кнопка "ок"
        self.frame = ttk.Frame(self)
        self.widgets['_btOk'] = ttk.Button(self.frame, text='OK', command=self.close)

    # расположение виджетов
    def _pack_widgets(self):
        self.widgets['lbWarn'].pack(side='top')
        self.widgets['lbText'].pack(side='top')
        self.widgets['lbText2'].pack(side='top')

        self.widgets['_btOk'].pack(anchor='w', padx=5)
        self.frame.pack(side='bottom', pady=10)





    #  из файла main.py:# from task_flows import CatframesProcess


def main():
    # error = CatframesProcess.check_error()
    # if error:
    #     messagebox.showerror("Error", error)
    #     return
    root = LocalWM.open(RootWindow, 'root')  # открываем главное окно
    root.mainloop()

if __name__ == "__main__":
    main()



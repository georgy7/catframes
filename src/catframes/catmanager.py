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
            'task.title.view': 'Task settings view',
            'task.initText': 'Add a directory\nof images',
            'task.lbColor': 'Background:',
            'task.lbFramerate': 'Framerate:',
            'task.lbQuality': 'Quality:',
            'task.cmbQuality': ('high', 'medium', 'poor'),
            'task.lbResolution': 'Render resolution:',
            'task.lbSaveAs': 'Save as:',
            'task.btCreate': 'Create',
            'task.btPathChoose': 'choose',
            'task.lbCopy': 'Сli command:',
            'task.btCopy': 'Copy',

            'dirs.lbDirList': 'List of source directories:',
            'dirs.btAddDir': 'Add',
            'dirs.btRemDir': 'Remove',
            'dirs.DirNotExists': "Doesn't exists. Removing...",

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
            'task.title.view': 'Просмотр настроек задачи',
            'task.initText': 'Добавьте папку\nс изображениями',
            'task.lbColor': 'Цвет фона:',
            'task.lbFramerate': 'Частота кадров:',
            'task.lbQuality': 'Качество:',
            'task.cmbQuality': ('высокое', 'среднее', 'низкое'),
            'task.lbResolution': 'Разрешение рендера:',
            'task.lbSaveAs': 'Сохранить как:',
            'task.btCreate': 'Создать',
            'task.btPathChoose': 'выбрать',
            'task.lbCopy': 'Команда cli:',
            'task.btCopy': 'Копировать',

            'dirs.lbDirList': 'Список директорий источников:',
            'dirs.btAddDir': 'Добавить',
            'dirs.btRemDir': 'Удалить',
            'dirs.DirNotExists': 'Не существует. Удаление...',
            
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
        self._color: str = DEFAULT_CANVAS_COLOR       # цвет отступов и фона
        self._framerate: int = 30                     # частота кадров
        self._quality: str = 'medium'                 # качество видео
        self._quality_index: int = 1                  # номер значения качества
        # self._limit: int                              # предел видео в секундах
        self._filepath: str = None                    # путь к итоговому файлу
        self._rewrite: bool = False                   # перезапись файла, если существует
        # self._ports = PortSets.get_range()            # диапазон портов для связи с ffmpeg

    # установка директорий
    def set_dirs(self, dirs) -> list:
        self._dirs = dirs

    # установка оверлеев
    def set_overlays(self, overlays_texts: List[str]):
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

        # if self._limit:                                     # ограничение времени, если есть
        #     command.append(f"--limit={self._limit}")

        if os.path.isfile(self._filepath):                  # флаг перезаписи, если файл уже есть
            command.append("--force")

        # command.append(f"--port-range={self._ports[0]}:{self._ports[1]}")  # диапазон портов
        
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
        self.delete_file()
        self.gui_callback.delete(self.id)  # сигнал о завершении задачи

    # удаляет файл в системе
    def delete_file(self):
        for i in range(20):  # делает 20 попыток
            try:
                os.remove(self.config.get_filepath())
                return
            except:              # если не получилось
                time.sleep(0.2)  # ждёт чуток, и пробует ещё 

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
        self.after(1, self._init_widgets)  # создание виджетов
        self.after(2, self.update_texts)   # установка текста нужного языка
        self.after(3, self._pack_widgets)  # расстановка виджетов

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
        border_gap = 30  # минимальный отступ от края окна при открытии

        screen_size = self.winfo_screenwidth(), self.winfo_screenheight()

        # если это не побочное окно, то размещаем по центру экрана
        if not isinstance(self, Toplevel):
            x = (screen_size[0] - self.size[0]) / 2
            y = (screen_size[1] - self.size[1]) / 2
            self.geometry(f'+{int(x)}+{int(y)}')
            return

        # далее для побочных окон:
        master_size = self.master.winfo_width(), self.master.winfo_height()
        x = self.master.winfo_x() + master_size[0]/2 - self.size[0]/2  # размещаем по центру
        y = self.master.winfo_y() + master_size[1]/2 - self.size[1]/2  # главного окна

        # если окно вышло за левый край экрана
        if x < border_gap:  
            x = border_gap

        # если окно вышло за правый край экрана
        if x+self.size[0]+border_gap > screen_size[0]:
            x = screen_size[0]-self.size[0]-border_gap

        # если окно вышло за верхнюю границу
        if y < border_gap:  
            y = border_gap

        # если окно вышло за низнюю границу экрана
        if y+self.size[1]+(border_gap*3) > screen_size[1]:  # отступ больше в три раза, 
            y = screen_size[1]-self.size[1]-(border_gap*3)  # учитывая панель задач или dock

        self.geometry(f'+{int(x)}+{int(y)}')


    # настройка стиля окна, исходя из разрешения экрана
    def _set_style(self) -> None:

        # screen_height = self.winfo_screenheight()  # достаём высоту экрана
        # scale = (screen_height/540)                # индекс масштабирования
        # scale *= MAJOR_SCALING                     # домножаем на глобальную

        style=ttk.Style()
        _font = font.Font(
            size=12, 
        )
        style.configure(style='.', font=_font)  # шрифт текста в кнопке
        self.option_add("*Font", _font)  # шрифты остальных виджетов

        style.configure('Main.TaskList.TFrame', background=MAIN_TASKLIST_COLOR)

        # создание стилей фона таскбара для разных состояний
        for status, color in MAIN_TASKBAR_COLORS.items():
            style.configure(f'{status}.Task.TFrame', background=color)
            style.configure(f'{status}.Task.TLabel', background=color)
            style.configure(f'{status}.Task.Horizontal.TProgressbar', background=color)

        style.map(
            "Create.Task.TButton", 
            background=[
                ("active", 'blue'),
                ("!disabled", 'blue')
            ]
        )

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
        super().__init__(root_window, *args, **kwargs, style='Main.TFrame')
        
        self.root = root_window
        self.canvas = Canvas(self, highlightthickness=0, bg=MAIN_TASKLIST_COLOR)  # объект "холста"
        self.canvas.bind(           # привязка к виджету холста
            "<Configure>",          # обработчика событий, чтобы внутренний фрейм
            self._on_resize_window  # менял размер, если холст растягивается
        )
        self.scrollbar = ttk.Scrollbar(  # полоса прокрутки
            self, orient="vertical",     # установка в вертикальное положение
            command=self.canvas.yview,   # передача управления вертикальной прокруткой холста
        )  
        self.scrollable_frame = ttk.Frame(  # фрейм для контента (внутренних виджетов)
            self.canvas, 
            padding=[15, 0], 
            style='Main.TaskList.TFrame'
        )
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

        # # создание надписи "здесь появятся Ваши проекты"
        # self._empty_sign = ttk.Label(
        #     self.scrollable_frame,
        #     justify=CENTER,
        #     font=("Arial", 18)
        # )

        # первичное обновление полосы, чтобы сразу её не было видно
        self._update_scrollbar_visibility()

    # отрабатываывает при добавлении/удалении таскбаров в фрейм
    def _on_frame_update(self, event):
        self._update_scrollbar(event)
        # self._update_empty_sign()

    # обновление видимости надписи "здесь появятся Ваши проекты" 
    # def _update_empty_sign(self):
    #     if '!taskbar' in self.scrollable_frame.children.keys():
    #         self._empty_sign.pack_forget()  # если есть таскбары, удалить надпись
    #     else:
    #         self._empty_sign.pack(pady=80)  # если их нет - покажет её

    def update_texts(self):
        pass
    #     self._empty_sign.config(text=Lang.read('bar.lbEmpty'))

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
        super().__init__(master, borderwidth=1, padding=5, style='Scroll.Task.TFrame')
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
        self.widgets['_picture'].pack(side=LEFT)
        self.left_frame.pack(side=LEFT)

        self.widgets['_lbPath'].pack(side=TOP, fill=X, expand=True)
        self.widgets['_lbData'].pack(side=TOP, fill=X, expand=True)
        self.mid_frame.pack(side=LEFT, fill=X, expand=True)

        self.widgets['_progressBar'].pack(side=TOP, expand=True, fill=X)
        self.widgets['btCancel'].pack(side=BOTTOM, expand=True, fill=X)
        self.right_frame.pack(side=LEFT, expand=True)

        self.pack(pady=[10, 0], fill=X, expand=True)

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


class ResizingField(Text):
    """Поле, переводящее курсор по нажатию Enter,
    и изменяющее свой размер по количеству строк"""

    def __init__(self, master: Canvas, horizontal_pos, vertical_pos):
        super().__init__(
            master, 
            width=10,
            font=("Arial", 14), 
            wrap=NONE, 
            undo=True,
            highlightthickness=2
        )
        self.default_width = 10
        self.extra_width = 0
        self.num_lines = 0

        self.vertical_pos = vertical_pos
        self.horizontal_pos = horizontal_pos
        self.vertical_shift = 0  # смещение по вертикали от начальных координат
        self.horisontal_shift = 0  # смещение по горизонтали

        self.id_on_canvas: int = None   # id объекта на холсте
        self.default_coords: list = None  # начальные координаты объекта на холсте

        self.bind("<Escape>", self._on_escape)      # привязка нажатия Escape
        self.bind("<<Modified>>", self._on_text_change)  # привязка изменения текста
        self.configure(height=1, wrap="word")  # начальная высота 1 строка и перенос по словам

    # получение всего текста в поле
    def get_text(self) -> str:
        try:
            return self.get("1.0", "end-1c").strip('\n ')
        except:
            return ''
        
    # установка текста в поле
    def set_text(self, text):
        self.delete('1.0', END)
        self.insert(END, text)

    # получение id себя на холсте
    def bind_self_id(self, id):
        self.id_on_canvas = id
        x, y = self.master.coords(id)
        self.default_coords = x, y-self.vertical_shift
        self._update_height()

    # фокусировка на объект холста, чтобы убрать это поле ввода
    def _on_escape(self, event):
        self.master.focus_set()



    # сбрасываем статус изменения текста, чтобы событие могло срабатывать повторно
    def _on_text_change(self, event):
        self._update_width()
        self._update_height()
        self._update_coords()
        self.master.overlays.update()
        self.edit_modified(False)  # сбрасывает флаг изменения

    # обновление ширины, исходя из самой длинной строки
    def _update_width(self):
        lines = self.get_text().split('\n')              # забираем список строк
        longest = len(max(lines, key=lambda i: len(i)))  # вычисляем самую длинную

        self.extra_width = 0
        if longest > self.default_width-1:  # если строка слишком длинная, добавит
            self.extra_width = longest + 2 - self.default_width  # дополнительную ширину
        
        y_shift_abs = self.extra_width*5          # рассчёт модуля горизонтального смещения  
        if self.horizontal_pos == RIGHT:          # если выравнивание по правому краю 
            self.horisontal_shift = -y_shift_abs  # поле пойдёт влево при расширении,
        if self.horizontal_pos == LEFT:           # а если по левому
            self.horisontal_shift = y_shift_abs   # - пойдёт вправо

    # обновление высоты, исходя из количества строк
    def _update_height(self):
        self.num_lines = int(self.index('end-1c').split('.')[0])  # определяем количество строк

        x_shift_abs = (self.num_lines-1)*11          # рассчёт модуля вертикального смещения
        if self.vertical_pos == BOTTOM:         # если выравнивание по низу 
            self.vertical_shift = -x_shift_abs  # поле пойдёт вверх при увеличении,
        if self.vertical_pos == TOP:            # а если по верху
            self.vertical_shift = x_shift_abs   # - пойдёт вниз


    # движение по вертикали при изменении количества строк
    def _update_coords(self):
        # если поле ввода ещё не размещено
        if not self.default_coords:  
            return  # менять координаты не нужно.

        self.master.coords(
            self.id_on_canvas, 
            self.default_coords[0]+self.horisontal_shift, 
            self.default_coords[1]+self.vertical_shift
        )

        self.config(
            width=self.default_width+self.extra_width, 
            height=self.num_lines
        )


class Overlay:
    """Единичный оверлей на холсте, как сущность из
    прозрачного квадрата, лейбла, и поля ввода."""
    
    def __init__(self, master: Canvas, text: str, horizontal_pos, vertical_pos):

        self.master = master
        self.view_mode: bool = master.view_mode
        self.horizontal_pos = horizontal_pos

        self.empty = bool(text)

        # настройи прозрачного квадрата
        self.sq_size = 20
        sq_color = '#ffffff'
        sq_alpha = 0.5
        if self.view_mode:
            sq_alpha = 0

        # создание и добавление прозрачного квадрата
        self.alpha_square = self._create_alpha_square(self.sq_size, sq_color, sq_alpha)
        self.square_id = self.master.create_image(0, 0, image=self.alpha_square, anchor='nw')

        # добавление текста
        self.label_id = self.master.create_text(0, 0, text=text, font=("Arial", 24), justify=horizontal_pos)
        self.vertical_shift = 0  # смещение поля ввода и лейбла по вертикали
        self.horizontal_shift = 0  # смещение по горизонтали

        # инициализация поля ввода
        self.entry = ResizingField(self.master, horizontal_pos, vertical_pos)
        self.entry_id = self.master.create_window(0, 0, window=self.entry, state='hidden', anchor=CENTER)
        self.entry.bind_self_id(self.entry_id)  # передача полю ввода своего id на холсте
        self.entry.set_text(text)

        # привязка события скрытия и показа поля ввода
        if not self.view_mode:
            self.master.tag_bind(self.label_id, "<Button-1>", self._show_entry)
            self.entry.bind("<FocusOut>", self._hide_entry)

    # обновление смещений текста
    def _update_shifts(self):
        self.vertical_shift = self.entry.vertical_shift  # смещение по вертикали от поля ввода

        if self.horizontal_pos == CENTER:  # если поле по центру
            self.horizontal_shift = 0      # то никаких смещений не нужно
            return

        bbox = self.master.bbox(self.label_id)  # вычисляем размеры, которые
        text_object_width = bbox[2]-bbox[0]     # лейбл занимает на холсте
        shift_abs = text_object_width//2 - self.sq_size/2  # смещение 

        if self.entry.get_text():               # если в поле ввода есть текст
            shift_abs -= self.master.width//20  # смещаем его к краю на часть ширины холста
        else:
            shift_abs = 0

        if self.horizontal_pos == RIGHT:        # если поле справа
            self.horizontal_shift = shift_abs   # то смещение положительное
        
        if self.horizontal_pos == LEFT:         # если слева - 
            self.horizontal_shift = -shift_abs  # отрицательное

    # обновляет текст лейбла и видимость квадрата
    def update_label(self):
        text = '+'              # дефолтные значения, когда поле ввода пустое 
        font = ("Arial", 24)
        square_state = 'normal'
        label_color = 'black'

        if self.entry.get_text() or self.view_mode:  # если в поле ввода указан какой-то текст
            text = self.entry.get_text()             # этот текст будет указан в лейбле
            font = ("Arial", 16)                     # шрифт будет поменьше
            square_state = 'hidden'                  # полупрозрачный квадрат будет скрыт

            dark_background = self.master.is_dark_background(self.label_id)  # проверится, тёмный ли фон у тейбла
            label_color = 'white' if dark_background else 'black'  # если тёмный - шрифт светлый, и наоборот

        try:
            self.master.itemconfig(self.label_id, text=text, font=font, fill=label_color)  # придание тексту нужных параметров
            self.master.itemconfig(self.square_id, state=square_state)                     # скрытие или проявление квадрата
        except TclError:
            pass

    def get_text(self) -> str:
        return self.entry.get_text()

    # установка кординат для квадрата и лейбла
    def set_coords(self, coords: Tuple[int]):
        self._update_shifts()
        self.master.coords(self.square_id, coords[0]-self.sq_size/2, coords[1]-self.sq_size/2) 
        self.master.coords(self.label_id, coords[0]-self.horizontal_shift, coords[1]+self.vertical_shift)

    # создаёт картинку прозрачного квадрата
    def _create_alpha_square(self, size: int, fill: str, alpha: float):
        alpha = int(alpha * 255)
        fill = self.master.winfo_rgb(fill) + (alpha,)
        image = Image.new('RGBA', (size, size), fill)
        return ImageTk.PhotoImage(image)
    
    # отображает поле ввода
    def _show_entry(self, event):
        label_coords = self.master.coords(self.label_id)
        self.master.coords(self.entry_id, *label_coords)
        self.entry.bind_self_id(self.entry_id)
        self.master.itemconfig(self.entry_id, state='normal')  # скрывает поле ввода
        self.entry.focus_set()
        
    # прячет поле ввода, меняет текст в лейбле
    def _hide_entry(self, event):
        text = self.entry.get_text()  # забирает стрипнутый текст из поля,
        self.entry.set_text(text)     # возвращает (уже стрипнутый)

        self.master.itemconfig(self.entry_id, state='hidden')  # скрывает поле ввода
        self.update_label()                              # обновляет лейбл


class OverlaysUnion:
    """Группа из восьми оверлеев, расположенных на холсте.
    Этот класс занимается их инициализацией и агрегацией."""

    def __init__(self, master: Canvas, default_texts: Optional[List[str]]):
        self.master = master
        self.view_mode = master.view_mode
        self.default_texts = default_texts

        self.overlays = []

        self._create_entries()
        self.update()
        
    # инициализация полей ввода
    def _create_entries(self):

        # выравнивания виджетов, относительно расположения
        c, l, r, t, b = CENTER, LEFT, RIGHT, TOP, BOTTOM  # сокращения
        horizontal_pos = (l, c, r, r, r, c, l, l)  # 8 позиций горизонтали
        vertical_pos   = (t, t, t, c, b, b, b, c)  # 8 позиций вертикали

        # создание каждого оверлея
        for i in range(8):
            text = self.default_texts[i] if self.view_mode else ''
            overlay = Overlay(self.master, text, horizontal_pos[i], vertical_pos[i])
            self.overlays.append(overlay)

    # позиционирует и привязывает обработчики позиций
    def update(self):
        x_pad = int(self.master.width / 8)  # отступ по горизонтали, исходя из ширины холста
        y_pad = int(self.master.height/ 8)  # отступ по вертикали статический
        positions = [
            (x_pad,                   y_pad),                     # верхний левый
            (self.master.width//2,    y_pad),                     # верхний
            (self.master.width-x_pad, y_pad),                     # верхний правый
            (self.master.width-x_pad, self.master.height//2),     # правый
            (self.master.width-x_pad, self.master.height-y_pad),  # нижний правый
            (self.master.width//2,    self.master.height-y_pad),  # нижний
            (x_pad,                   self.master.height-y_pad),  # нижний левый
            (x_pad,                   self.master.height//2),     # левый
        ]

        try:
            # позиционирует каждый виджет и обновляет текст
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
    """Класс для хранения информации о картинке,
    её изменения, и преобразования."""

    def __init__(self, master: Canvas) -> None:
        self.master = master
        self.stock = True
        self.hidden = True
        self.id: int = None
        self.orig_pil: Image = None
        self.pil: Image = None
        self.tk: ImageTk = None
        self.height: int = None
        self.width: int = None
        self._create_image()
    
    # создание изображения
    def _create_image(self):
        self.set_empty()  # запись пустой картинки
        x, y = self.master.width//2 - self.height//2, 0
        self.id = self.master.create_image(x, y, anchor=NW, image=self.tk)  # передача изображения
        
        # привязка фокусировки на холст при нажатие на изображение, чтобы снять фокус с полей ввода
        self.master.tag_bind(self.id, "<Button-1>", lambda event: self.master.focus_set())

    # изменение размера картинки, подгонка под холст
    def _update_size(self, current_as_base: bool = False):
        canvas_ratio = self.master.width / self.master.height  # соотношение сторон холста
        ratio = self.orig_pil.size[0] / self.orig_pil.size[1]  # соотношение сторон картинки

        if canvas_ratio > ratio:                                      # если холст по соотносшению шире
            size = int(self.master.height*ratio), self.master.height    # упор по высоте
        else:                                                         # а если холст по соотношению выше
            size = self.master.width, int(self.master.width/ratio)      # то упор по высоте

        if (self.width, self.height) == size:  # если размеры не поменялись
            return

        try:
            self.pil = self.orig_pil.resize(size, Image.LANCZOS)  # масштабирование
            self.tk = ImageTk.PhotoImage(self.pil)                # загрузка новой тк-картинки
            self.width, self.height = size                        # сохранение новых размеров

            if current_as_base:           # установка текущего размера картинки
                self.orig_pil = self.pil  # как базового (для оптимизации)
        except Exception:  # если PIL сломается внутри из-за сложного и частого вызова
            pass

    # приобразование ссылки на картинку, наполнение объекта композита
    def open_image(self, image_link: str):
        try:
            self.orig_pil = Image.open(image_link)   # открытие изображения по пути
            self._update_size(current_as_base=True)  # установка размеров картинки базовыми
            self.stock = False
        except (FileNotFoundError, AttributeError):  # если файл не найден
            self.set_empty()                         # создаёт пустую картинку

    # расположение картинки на холсте по центру
    def update_coords(self):
        x = self.master.width//2 - self.width//2
        y = self.master.height//2 - self.height//2
        self.master.coords(self.id, x, y)

    # создание пустого изображения, и надписи "добавьте картинки"
    def set_empty(self):
        self.height, self.width = self.master.height, self.master.width
        self.orig_pil = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))  # пустое изображение
        self.pil = self.orig_pil                           # текущий объект pil будет таким же
        self.tk = ImageTk.PhotoImage(self.orig_pil)        # создаём объект тк
        self.stock = True                                  # установка флага стокового изображения

    # изменение прозрачности картинки
    def change_alpha(self, alpha):
        faded_current_image = self.pil.copy()              # копируем картинку 
        faded_current_image.putalpha(int(alpha * 255))     # применяем альфа-канал 
        self.tk = ImageTk.PhotoImage(faded_current_image)  # создаём тк картинку, сохраняем
        self.master.itemconfig(self.id, image=self.tk)     # обновляем изображения на холсте 

    # перезагрузка картинки на холсте
    def reload(self):
        self._update_size()                                # обновление размера
        self.master.itemconfig(self.id, image=self.tk)     # замена тк-картинки на холсте


# проверка, тёмный цвет, или светлый
def is_dark_color(r: int, g: int, b: int) -> bool:
    if r > 256 or g > 256 or b > 256:               # если значение в широкой палитре цветов (два байта на цвет)
        r, g, b = r//256, g//256, b//256            # то округляются до узкой палитры (один байт на цвет)
    brightness = (r*299 + g*587 + b*114) / 1000     # вычисление яркости пикселя по весам
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
            background: str = DEFAULT_CANVAS_COLOR
        ):

        self.default_width = self.width = 800
        self.default_height = self.height = 400

        # создаёт объект холста
        super().__init__(master, width=self.width, height=self.height, highlightthickness=0, background=background)
        self.pack()

        self.view_mode = veiw_mode  # флаг режима просмотра
        self.color = background

        self.init_text = None
        self._create_init_text()    # создание пригласительной надписи
        if not veiw_mode:           # и, если это не режим просмотра,
            self._show_init_text()  # показывает надпись

        self.cleared = True
        self.new_img = ImageComposite(self)   # изображения, которые будут
        self.old_img = ImageComposite(self)   # менять прозрачность по очереди

        self.alpha_step = 0.1  # Шаг изменения прозрачности 
        self.delay = 20  # Задержка между кадрами (мс) 

        self.overlays = OverlaysUnion(self, overlays)

    # анимируем смену изображений (рекурсивный метод)
    def _animate_transition(self, alpha: float = 1): 
        if alpha <= 0:                   # если альфа-канал дошёл до нуля
            self.old_img.hidden = True   # расставляем флаги прозрачности
            self.new_img.hidden = False
            self.overlays.update()       # обновляем оверлеи
            self._hide_init_text()       # только в конце прячем текст
            return
        
        if not self.old_img.stock:       # если изображение не стоковое
            self.old_img.change_alpha(alpha)  # делаем его прозрачнее
        self.new_img.change_alpha(1-alpha)    # а новое - наоборот

        # вызываем этот же метод, но уменьшая альфа-канал
        self.master.after(self.delay, self._animate_transition, alpha-self.alpha_step)
            
    # плавное исчезновение картинки (рекурсивный метод)
    def _animate_fadeoff(self, alpha: float = 1):
        if alpha <= 0:                   # если альфа-канал дошёл до нуля
            self.old_img.hidden = True   # ставим флаг прозрачности
            self.overlays.update()       # обновляем оверлеи
            return
        
        if not self.old_img.stock:
            self.old_img.change_alpha(alpha)  # делаем картинку прозрачнее
        self.master.after(self.delay, self._animate_fadeoff, alpha-self.alpha_step)  # рекурсия
        
    # обновление изображения (внешняя ручка)
    def update_image(self, image_link: str):
        self.cleared = False
        self.old_img, self.new_img = self.new_img, self.old_img  # меняем картинки местами
        self.new_img.open_image(image_link)     # открываем картинку
        self.new_img.update_coords()            # устанавливаем её координаты
        self._animate_transition()              # анимируем замену старой

    # очистка холста от изображений (внешняя ручка)
    def clear_image(self):
        if self.cleared:
            return
        self.cleared = True
        self.old_img, self.new_img = self.new_img, self.old_img  # меняем картинки местами
        self._show_init_text()                  # сначала показ пригласительного текста
        self._animate_fadeoff()                 # анимируем исчезновение
        self.new_img.set_empty()                # устанавливаем стоковую картинку
        self.new_img.update_coords()            # позиционируем её

    # создание объекта пригласительного текста
    def _create_init_text(self):
        self.init_text = self.create_text(          # то добавляет её 
            self.width/2, self.height/2,            # позиционирует по
            font=("Arial", 24), justify=CENTER,   # центру холста,
            state='hidden', fill='#cccccc')         # делает невидимым
        self.update_texts()                         # и обновляет тексты

    # показывает пригласительный текст
    def _show_init_text(self):
        self.itemconfig(self.init_text, state='normal')

    # прячет пригласительный текст
    def _hide_init_text(self):
        self.itemconfig(self.init_text, state='hidden')

    # проверка, тёмный ли фон на картинке за элементом канваса
    def is_dark_background(self, elem_id: int) -> bool:
        x_shift, y_shift = self.coords(self.new_img.id) # сдвиг картинки от левого края холста
        x, y = self.coords(elem_id)                     # координаты элемента на холсте
        try:
            x -= int(x_shift)                       # поправка, теперь это коорд. элемента на картинке
            y -= int(y_shift)
            if x < 0 or y < 0:
                raise IndexError                        # если координата меньше нуля

            if self.new_img.hidden:                     # если картинка спрятана
                raise Exception
            
            color = self.new_img.pil.getpixel((x, y))   # цвет пикселя картинки на этих координатах
            r, g, b = color[0:3]
        except TypeError:                               # если pillow вернёт не ргб, а яркость пикселя
            return color < 128
        except Exception:                               # если пиксель за пределами картинки
            r, g, b = self.winfo_rgb(self.color)        # задний план будет оцениваться, исходя из
            r, g, b = r/255, g/255, b/255               # выбранного фона холста
        
        return is_dark_color(r, g, b)                   # вычисление, тёмный цвет, или светлый

    # обновляет разрешение холста
    def update_resolution(self, width: int, height: int, resize_image: bool):

        self.width, self.height = width, height
        self.config(height=height, width=width)             # установка новых размеров
        self.overlays.update()                              # обновляет оверлеи
        self.coords(self.init_text, self.width/2, self.height/2)  # позиция прив. текста

        if resize_image:                # если нужен пересчёт картинки
            self.new_img.reload()       # то пересчитывает
        self.new_img.update_coords()    # обновляет координаты картинки

    # формирует список из восьми строк, введённых в полях
    def fetch_entries_text(self) -> list:
        return self.overlays.get_text()
    
    # обновляет цвета отступов холста
    def update_background_color(self, color: str):
        self.color = color
        self.config(background=color)
        self.overlays.update()

    # обновление
    def update_texts(self):
        if self.init_text:
            self.itemconfig(self.init_text, text=Lang.read('task.initText'))


class DirectoryManager(ttk.Frame):
    """Менеджер директорий, поле со списком.
    Даёт возможность добавлять, удалять директории, 
    и менять порядок кнопками и перетаскиванием"""

    def __init__(self, master: Union[Tk, Frame], veiw_mode: bool, dirs: list, on_change: Callable):
        super().__init__(master)
        self.name = 'dirs'

        self.widgets: Dict[str, Widget] = {}
        self.drag_data = {"start_index": None, "item": None}
        self.on_change: Callable = on_change

        self.veiw_mode = veiw_mode
        self._init_widgets()
        self._pack_widgets()
        self.update_texts()

        self.dirs = dirs
        self._update_listbox(30)

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

    # инициализация виджетов
    def _init_widgets(self):

        self.top_frame = Frame(self)

        self.widgets['lbDirList'] = ttk.Label(self.top_frame)  # надпись "Список директорий:"

        # при растягивании фрейма
        def on_resize(event):
            max_length = int(event.width // 8)  # максимальная длина имени директории
            self._update_listbox(max_length)    # обновление длины строк для всего списка

        # создание списка и полосы прокрутки
        self.listbox = Listbox(self.top_frame, selectmode=SINGLE, width=20, height=8)
        self.scrollbar = ttk.Scrollbar(self.top_frame, orient="vertical", command=self.listbox.yview)
        self.listbox.config(yscrollcommand=self.scrollbar.set)

        if not self.veiw_mode:
            self.listbox.bind('<Button-1>', self._start_drag)
            self.listbox.bind('<B1-Motion>', self._do_drag)
        self.top_frame.bind('<Configure>', on_resize)
        self.listbox.bind('<Double-Button-1>', self._on_double_click)

        self.button_frame = Frame(self)

        # создание кнопок для управления элементами списка
        self.widgets['btAddDir'] = ttk.Button(self.button_frame, width=8, command=self._add_directory)
        self.widgets['btRemDir'] = ttk.Button(self.button_frame, width=8, command=self._remove_directory)
    
    # размещение виджетов
    def _pack_widgets(self):
        self.top_frame.pack(side=TOP, fill=BOTH, expand=True)
        self.widgets['lbDirList'].pack(side=TOP, anchor='w')
        self.listbox.pack(side=LEFT, fill=BOTH, expand=True)
        self.scrollbar.pack(side=LEFT, fill=Y)

        self.button_frame.pack(side=TOP, anchor='w', padx=(0, 15), pady=10, fill=X)

        if not self.veiw_mode:
            self.widgets['btAddDir'].pack(side=LEFT, anchor='e', padx=5, expand=True)
            self.widgets['btRemDir'].pack(side=RIGHT, anchor='w', padx=5, expand=True)

    # добавление директории
    def _add_directory(self):
        dir_name = filedialog.askdirectory(parent=self)
        if not dir_name or dir_name in self.dirs:
            return
        if not find_img_in_dir(dir_name):
            return
        self.listbox.insert(END, shrink_path(dir_name, 25))
        self.dirs.append(dir_name)  # добавление в список директорий
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

    def _swap_dirs(self, index_old: int, index_new: int, text: str = None):
        if not text:
            text = self.listbox.get(index_old)
        self.listbox.delete(index_old)        # удаляет старый элемент
        self.listbox.insert(index_new, text)  # вставляет на его место новый
        self.dirs[index_old], self.dirs[index_new] = self.dirs[index_new], self.dirs[index_old]
        self.listbox.select_set(index_new)    # выбирает новый элемент (чтобы остался подсвеченным)

    # процесс перетаскивания элемента
    def _do_drag(self, event):
        new_index = self.listbox.nearest(event.y)
        if new_index != self.drag_data["start_index"]:
            self._swap_dirs(
                self.drag_data["start_index"], 
                new_index, 
                self.drag_data["item"]
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
            os.startfile(dir_to_open)
        except:
            self.listbox.delete(index)
            self.listbox.insert(index, Lang.read('dirs.DirNotExists'))
            self.after(2000, self.listbox.delete, index)
            self._remove_directory()

    def update_texts(self):
        for w_name, widget in self.widgets.items():
            if not w_name.startswith('_'):
                widget.config(text=Lang.read(f'{self.name}.{w_name}'))


class ToolTip: 
    """Подсказка при наведении на виджет.
    Лейбл с текстом поверх всего, 
    коорый появляется при наведении, 
    и исчизает при уходе курсора"""

    def __init__(self, widget: Widget, get_text: Callable):
        self.widget = widget      # виджет, к которому привязывается подсказка
        self.get_text = get_text  # функция, по которой получим текст подсказки
        self.tip_window = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)
 
    # показать "подсказку"
    def show_tip(self, event=None):
        text = self.get_text()  # достаём текст по функции из инъекции
        if not text:            # если текста нет - ничего не делаем
            return
        
        # вычисляем координаты окна
        x_shift = len(text)*2
        x = self.widget.winfo_rootx() - x_shift
        y = self.widget.winfo_rooty() + 30

        # создание окна для подсказки 
        self.tip_window = Toplevel(self.widget)
        self.tip_window.wm_overrideredirect(True)  # убрать системную рамку окна
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
        self.upper_bar = upperBar = Frame(self, background=MAIN_TOOLBAR_COLOR)  # верхний бар с кнопками
        self.task_space = ScrollableFrame(self)  # пространство с прокруткой
        self.taskList = self.task_space.scrollable_frame  # сокращение пути для читаемости

        # создание виджетов, привязывание функций
        self.widgets['newTask'] = ttk.Button(upperBar, command=open_new_task)
        self.widgets['openSets'] = ttk.Button(upperBar, command=open_settings)

    # расположение виджетов
    def _pack_widgets(self):
        self.upper_bar.pack(fill=X)
        self.task_space.pack(fill=BOTH, expand=True)

        self.widgets['newTask'].pack(side=LEFT, padx=10, pady=10)
        self.widgets['openSets'].pack(side=RIGHT, padx=10, pady=10)
        
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

        self.size = 250, 150
        # self.size = 250, 200
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

        # def validate_numeric(new_value):  # валидация ввода, разрешены только цифры и пустое поле
        #     return new_value.isnumeric() or not new_value
        
        # v_numeric = (self.register(validate_numeric), '%P')  # регистрация валидации

        # self.widgets['lbPortRange'] = ttk.Label(self)
        # self.widgets['_entrPortFirst'] = ttk.Entry(  # поле ввода начального порта
        #     self, 
        #     justify=CENTER, 
        #     validate='key', 
        #     validatecommand=v_numeric  # привязка валидации
        # )
        # self.widgets['_entrPortLast'] = ttk.Entry(  # поле ввода конечного порта
        #     self, 
        #     justify=CENTER, 
        #     validate='all',
        #     validatecommand=v_numeric  # привязка валидации
        # )
        
        # применение настроек
        def apply_settings():
            Lang.set(index=self.widgets['_cmbLang'].current())  # установка языка
            for w in LocalWM.all():  # перебирает все прописанные в менеджере окна
                w.update_texts()  # для каждого обновляет текст методом из WindowMixin

            # try:  # проверка введённых значений, если всё ок - сохранение
            #     port_first = int(self.widgets['_entrPortFirst'].get())
            #     port_last = int(self.widgets['_entrPortLast'].get())
            #     assert(port_last-port_first >= 100)         # диапазон не меньше 100 портов
            #     assert(port_first >= 10240)                 # начальный порт не ниже 10240
            #     assert(port_last <= 65025)                  # конечный порт не выше 65025
            #     PortSets.set_range(port_first, port_last)   # сохранение настроек

            # except:  # если какое-то из условий не выполнено
            #     self._set_ports_default()  # возврат предыдущих значений виджетов
            #     LocalWM.open(NotifyWindow, 'noti', master=self)  # окно оповещения

        # сохранение настроек (применение + закрытие)
        def save_settings():
            apply_settings()
            self.close()

        self.widgets['btApply'] = ttk.Button(self, command=apply_settings, width=7)
        self.widgets['btSave'] = ttk.Button(self, command=save_settings, width=7)

    # # установка полей ввода портов в последнее сохранённое состояние
    # def _set_ports_default(self):
    #     self.widgets['_entrPortFirst'].delete(0, 'end')
    #     self.widgets['_entrPortFirst'].insert(0, PortSets.get_range()[0])
    #     self.widgets['_entrPortLast'].delete(0, 'end')
    #     self.widgets['_entrPortLast'].insert(0, PortSets.get_range()[1])

    # расположение виджетов
    def _pack_widgets(self):

        for c in range(2): 
            self.columnconfigure(index=c, weight=1)
        for r in range(7): 
            self.rowconfigure(index=r, weight=1)
        
        self.widgets['lbLang'].grid(row=1, column=0, sticky='e', padx=15, pady=5)
        self.widgets['_cmbLang'].grid(row=1, column=1, sticky='w', padx=(15 ,5), pady=5)
        self.widgets['_cmbLang'].current(newindex=Lang.current_index)  # подставляем в ячейку текущий язык

        # self.widgets['lbPortRange'].grid(columnspan=2, row=2, column=0, sticky='ws', padx=15)
        # self.widgets['_entrPortFirst'].grid(row=3, column=0, sticky='wn', padx=(15, 5))
        # self.widgets['_entrPortLast'].grid(row=3, column=1, sticky='wn', padx=(5, 15))
        # self._set_ports_default()  # заполняем поля ввода портов

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

        self.size = 900, 500
        self.resizable(True, True)

        super()._default_set_up()

        self.image_updater_thread = threading.Thread(target=self.canvas_updater, daemon=True)
        self.image_updater_thread.start()

    # поток, обновляющий картинку и размеры холста
    def canvas_updater(self):
        last_dirs = []       # копия списка последних директорий
        images_to_show = []  # список картинок для показа
        index = 0            # индекс картинки в этом списке

        # проверяет, не поменялся ли список картинок
        def check_images_change():
            nonlocal images_to_show, last_dirs, index

            new_dirs = self.dir_manager.get_dirs()
            if last_dirs == new_dirs:
                return

            last_dirs = new_dirs  # обновляем директории, забираем картинки
            all_images = self.dir_manager.get_all_imgs()

            if len(all_images) < 4:  # если картинок меньше 4, забираем все
                images_to_show = all_images
                index = 0
            else:                    # если их много - выбираем с нужным шагом
                step = len(all_images) // 4
                images_to_show = all_images[step::step]

        # попытка обновления картинки
        def update_image():
            nonlocal index

            if not images_to_show:  # если список картинок пуст
                # показывает на холсте надпись "выберите картинку"
                self.image_canvas.clear_image()
                return

            # если список не пуст, и счётчик дошёл
            self.image_canvas.update_image(images_to_show[index])
            index = (index + 1) % len(images_to_show)  # инкремент
            time.sleep(10)  # если картинка поменялась, то ждёт 10 сек

        time.sleep(0.5)  # чтобы не было глича при одновременном открытии окна и картинки
        while True:
            check_images_change()
            try:
                update_image()  # пробуем обновить картинку
                time.sleep(1)
            except TclError:  # это исключение появится, когда окно закроется
                return

    # сбор данных из виджетов, создание конфигурации
    def _collect_task_config(self):
        overlays = self.image_canvas.fetch_entries_text()       # достаёт тексты оверлеев из виджетов,
        self.task_config.set_overlays(overlays_texts=overlays)  # передаёт их в конфиг задачи оверлеев.

        self.task_config.set_specs(
            framerate=self.widgets['_cmbFramerate'].get(),  # забирает выбранное значение в комбобоксе
            quality=self.widgets['cmbQuality'].current(),   # а в этом забирает индекс выбранного значения
        )

    # попытка проверяет, есть ли директории и путь сохранения файла
    def _validate_task_config(self):
        state = 'disabled'
        if self.task_config.get_dirs() and self.task_config.get_filepath():
            state = 'enabled'
        self.widgets['btCreate'].configure(state=state)
        self.widgets['btCopy'].configure(state=state)

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
        self.main_pane = PanedWindow(
            self,
            orient=HORIZONTAL,
            sashwidth=5,
            background='grey',
            sashrelief='flat',
            opaqueresize=True,
            proxybackground='grey',
            proxyborderwidth=5,
            proxyrelief='flat'
        )

        self.canvas_frame = Frame(self.main_pane, background='black')
        self.main_pane.add(self.canvas_frame, stretch='always')
        self.main_pane.paneconfig(self.canvas_frame, minsize=300)
        self.canvas_frame.pack_propagate(False)
        self.canvas_frame.config(
            width=self.winfo_width()-200,
        )

        self.image_canvas = ImageCanvas(  # создание холста с изображением
            self.canvas_frame, 
            veiw_mode=self.view_mode,
            overlays=self.task_config.get_overlays(),
            background=self.task_config.get_color(),
        )

        self.menu_frame = Frame(self.main_pane)    # создание табличного фрейма меню
        self.main_pane.add(self.menu_frame, stretch='never')
        self.main_pane.paneconfig(self.menu_frame, minsize=250)

        self._bind_resize_events()

        # передача дитекротий в конфиг, валидация
        def set_dirs_to_task_config(dirs):   # внешняя ручка, вызываемая 
            self.task_config.set_dirs(dirs)  # менеджером директорий после
            self._validate_task_config()     # добавления/удаления директории

        self.dir_manager = DirectoryManager(
            self.menu_frame, 
            veiw_mode=self.view_mode,
            dirs=self.task_config.get_dirs(),
            on_change=set_dirs_to_task_config,  # передача ручки
        )

        self.settings_grid = Frame(self.menu_frame)  # создание фрейма настроек в нижнем фрейме

        def add_task():  # обработка кнопки добавления задачи
            self._collect_task_config()
            self._create_task_instance()  # cоздание и запуск задачи
            self.close()                  # закрытие окна создания задачи

        def ask_color():  # вызов системного окна по выбору цвета
            color = colorchooser.askcolor(parent=self)[-1]
            if not color:
                return
            self.image_canvas.update_background_color(color)
            self.canvas_frame.config(background=color)
            self.task_config.set_color(color)  # установка цвета в конфиге
            text_color = 'white' if is_dark_color(*self.winfo_rgb(color)) else 'black'
            self.widgets['_btColor'].configure(bg=color, text=color, fg=text_color)  # цвет кнопки

        def set_filepath():  # выбор пути для сохранения файла
            filepath = filedialog.asksaveasfilename(
                    parent=self,                                                # открытие окна сохранения файла
                    filetypes=[("mp4 file", ".mp4"), ("webm file", ".webm")],   # доступные расширения и их имена
                    defaultextension=".mp4"                                     # стандартное расширение
            )
            if filepath:
                self.task_config.set_filepath(filepath)
                self.widgets['_btPath'].configure(text=filepath.split('/')[-1])
                self._validate_task_config()

        def copy_to_clip():  # копирование команды в буфер обмена
            self._collect_task_config()
            command = ' '.join(self.task_config.convert_to_command())
            self.clipboard_clear()
            self.clipboard_append(command)

        # виджеты столбца описания кнопок
        self.widgets['lbColor'] = ttk.Label(self.settings_grid)
        self.widgets['lbFramerate'] = ttk.Label(self.settings_grid)
        self.widgets['lbQuality'] = ttk.Label(self.settings_grid)
        self.widgets['lbSaveAs'] = ttk.Label(self.settings_grid)

        # виджеты правого столбца (кнопка цвета, комбобоксы и кнопка создания задачи)
        self.widgets['_btColor'] = Button(
            self.settings_grid, 
            command=ask_color, 
            text=DEFAULT_CANVAS_COLOR, 
            width=7,
            bg=self.task_config.get_color(),
            fg='white',
            borderwidth=1,
            relief='solid',
            highlightcolor='grey',
        )

        self.widgets['_cmbFramerate'] = ttk.Combobox(  # виджет выбора фреймрейта
            self.settings_grid,
            values=self.framerates, 
            state='readonly',
            justify=CENTER,
            width=8,
        )
        self.widgets['_cmbFramerate'].set(  # установка начального значения в выборе фреймрейта
            self.task_config.get_framerate()
        )

        self.widgets['cmbQuality'] = ttk.Combobox(  # виджет выбора качества
            self.settings_grid,
            state='readonly',
            justify=CENTER,
            width=8,
        )

        path = self.task_config.get_filepath()
        file_name = path.split('/')[-1] if path else Lang.read('task.btPathChoose')
        self.widgets['_btPath'] = ttk.Button(self.settings_grid, command=set_filepath, text=file_name)
        ToolTip(self.widgets['_btPath'], self.task_config.get_filepath)  # привязка подсказки к кнопке пути

        self.widgets['btCreate'] = ttk.Button(self.settings_grid, command=add_task, style='Create.Task.TButton')

        # лейбл и кнопка копирования команды
        self.widgets['lbCopy'] = ttk.Label(self.settings_grid)
        self.widgets['btCopy'] = ttk.Button(self.settings_grid, command=copy_to_clip)

        if self.view_mode:  # если это режим просмотра, все виджеты, кроме копирования - недоступны
            for w_name, w in self.widgets.items():
                if ('lb') in w_name or ('Copy') in w_name:
                    continue
                w.configure(state='disabled')

    # привязка событий изменений размеров
    def _bind_resize_events(self):
        """ресайз картинки - это долгий процесс, PIL задерживает поток, 
        поэтому, во избежание лагов окна - логика следующая:

        если пользователь всё ещё тянет окно/шторку - 
            холст меняет размер (оверлеи, квадратики, надпись)

        но если события изменения не было уже 100мс - 
            холст обновляет размер всего, в том числе - картинки"""
        
        resize_delay = 100   # задержка перед вызовом обновления
        resize_timer = None  # идентификатор таймера окна

        def trigger_update(resize_image: bool):
            new_width = self.canvas_frame.winfo_width()
            new_height = self.canvas_frame.winfo_height()
            self.image_canvas.update_resolution(new_width, new_height, resize_image)

        # вызов при любом любом изменении размера
        def on_resize(event):
            # если событие - изменение размера окна, но ширина или высота меньше минимальных
            if event.type == 22 and (event.width < self.size[0] or event.height < self.size[1]):
                return  # то его обрабатывать не нужно
            
            nonlocal resize_timer
            trigger_update(resize_image=False)

            # если таймер уже существует, отменяем его
            if resize_timer:
                self.after_cancel(resize_timer)

            # новый таймер, который вызовет trigger_update через заданное время
            resize_timer = self.after(resize_delay, trigger_update, True)

        # привязка обработчика к событиям изменения размеров окна и перетягиания шторки
        self.bind("<Configure>", on_resize)  # для изменения размеров окна
        self.main_pane.bind("<Configure>", on_resize)  # для отпускания лкм на шторке

    # расположение виджетов
    def _pack_widgets(self):
        self.main_pane.pack(expand=True, fill=BOTH)

        # левый и правый столбцы нижнего фрейма
        self.dir_manager.pack(expand=True, fill=BOTH, padx=(15,0), pady=(20, 0))  # менеджер директорий
        self.settings_grid.pack(pady=10)  # фрейм настроек

        # настройка столбцов и строк для сетки лейблов/кнопок в меню
        self.settings_grid.columnconfigure(0, weight=3)
        self.settings_grid.columnconfigure(1, weight=1)

        # подпись и кнопка цвета       
        self.widgets['lbColor'].grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.widgets['_btColor'].grid(row=0, column=1, sticky='ew', padx=5, pady=5)

        # подпись и комбобокс частоты
        self.widgets['lbFramerate'].grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.widgets['_cmbFramerate'].grid(row=1, column=1, sticky='ew', padx=5, pady=5)

        # подпись и комбобокс качества
        self.widgets['lbQuality'].grid(row=2, column=0, sticky='e', padx=5, pady=5)
        self.widgets['cmbQuality'].grid(row=2, column=1, sticky='ew', padx=5, pady=5)

        # подпись и кнопка выбора пути
        self.widgets['lbSaveAs'].grid(row=3, column=0, sticky='e', padx=5, pady=5)
        self.widgets['_btPath'].grid(row=3, column=1, sticky='ew', padx=5, pady=5)
        
        # подпись и кнопка копирования команды
        self.widgets['lbCopy'].grid(row=4, column=0, sticky='e', padx=5, pady=5)
        self.widgets['btCopy'].grid(row=4, column=1, sticky='ew', padx=5, pady=5)

        if not self.view_mode:  # кнопка создания задачи
            self.widgets['btCreate'].grid(row=5, column=1, sticky='ew', padx=5, pady=5)

        self._validate_task_config()


    # расширение метода обновления текстов
    def update_texts(self) -> None:
        super().update_texts()
        self.dir_manager.update_texts()
        self.image_canvas.update_texts()
        # установка начального значения в выборе качества
        self.widgets['cmbQuality'].current(newindex=self.task_config.get_quality())
        if self.view_mode:
            self.title(Lang.read(f'task.title.view'))
        if not self.task_config.get_filepath():
            self.widgets['_btPath'].configure(text=Lang.read('task.btPathChoose'))

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
        self.widgets['lbWarn'].pack(side=TOP)
        self.widgets['lbText'].pack(side=TOP)

        self.widgets['btBack'].pack(side=LEFT, anchor='w', padx=5)
        self.widgets['btExit'].pack(side=LEFT, anchor='w', padx=5)
        self.choise_frame.pack(side=BOTTOM, pady=10)


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
        self.widgets['lbWarn'].pack(side=TOP)
        self.widgets['lbText'].pack(side=TOP)
        self.widgets['lbText2'].pack(side=TOP)

        self.widgets['_btOk'].pack(anchor='w', padx=5)
        self.frame.pack(side=BOTTOM, pady=10)





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



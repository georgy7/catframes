#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import threading
import time
import os
import re

from tkinter import *
from tkinter import ttk, font, filedialog, colorchooser
from abc import ABC, abstractmethod
from typing import Optional, Tuple, Dict, Callable
from PIL import Image, ImageTk

#  Если где-то не хватает импорта, не следует добавлять его в catmanager.py,
#  этот файл будет пересобран утилитой _code_assembler.py, и изменения удалятся.
#  Недостающие импорты следует указывать в _prefix.py, именно они пойдут в сборку.



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
При конвертировании, происходит проверка каждого атрибута
на валидность данных, и если возникает нарушение, 
вызывается ошибка с текстом имени некорректного параметра.
Эти исключения далее будет обрабатывать фронт, понимая,
какой конкретно параметр не прошёл валидацию.

Чтобы в процессе обработки, задача могла как-то делиться
своим статусом с интерфейсом, реализован паттерн "наблюдатель".
При старте задачи, ей передаётся объект класса GuiCallback.
При инициализации, объект коллбэка принимает внешние зависимости,
чтобы у задачи была возможность обновлять свои статусы в gui.
"""



class TaskConfig:
    """Хранение конфигурации текущей задачи.
    Позволяет конвертировать в команду catframes,
    проверив валидность каждого из параметров."""

    def __init__(self) -> None:
        self.dirs: list = []                      # пути к директориям с изображениями
        self.sure_flag: bool = False                 # флаг для предотвращения ошибок, если нет директории
        self.overlays: dict = {}                     # словрь надписей {'--left-top': 'надпись'}
        self.margin_color: str = '#000'              # цвет отступов и фона
        self.frame_rate: int = 30                    # частота кадров (от 1 до 60)
        self.quality: str = 'medium'                 # качество видео (poor, medium, high)
        self.limit: Optional[int]                    # предел видео в секундах
        self.force_flag: bool = False                # перезапись конечного файла, если существует
        self.port_range: Optional[Tuple[int, int]]   # диапазон портов для связи с ffmpeg
        self.path: str = '.'                         # путь к директории сохранения
        self.file_name: str = 'unknown'               # имя файла
        self.extension: str = 'mp4'                  # расширение файла

    # проверка каждого атрибута на валидность, создание консольной команды
    def convert_to_command(self) -> str:
        command = 'catframes'
        invalid_characters = ('\\', '"', '\'', '$', '(', ')', '[', ']')

        # if self.sure_flag:
        #     command += ' -s'
        
        # проверка текстовых оверлеев
        for position, text in self.overlays.items():
            if position not in (
                'left',
                'right',
                'top',
                'bottom',
                'left-top',
                'left-bottom',
                'right-top',
                'right-bottom',
                'top-left',
                'top-right',
                'bottom-left',
                'bottom-right',
            ): raise AttributeError('overlay_position')
            if invalid_characters in text:
                raise AttributeError('overlay_text')
            command += f" --{position} '{text}'"
        
        # проверка корректности строки с rgb
        rgb_pattern = re.compile(r'^#([a-fA-F0-9]{3}|[a-fA-F0-9]{6})$')
        if not rgb_pattern.match(self.margin_color):
            raise AttributeError(
                f'incorrect color: {self.margin_color}'
            )
        command += f" --margin-color {self.margin_color}"

        # проверка выбора частоты кадров
        if self.frame_rate < 1 or self.frame_rate > 60:
            raise AttributeError('frame_rate')
        command += f" --frame-rate {self.frame_rate}"

        # проверка выбора качества рендера
        if self.quality not in ['poor', 'medium', 'high']:
            raise AttributeError('quality')
        command += f" --quality {self.quality}"

        # проверка наличия и валидности ограничения времени
        if hasattr(self, 'limit'):
            if self.limit < 1:
                raise AttributeError('limit')
            command += f" --limit {self.limit}"

        # проверка флага перезаписи
        if self.force_flag:
            command += f" --force"

        # проверка наличия и валидности ограничения портов
        if hasattr(self, 'port_range'):
            if self.port_range[0] > self.port_range[1]:
                raise AttributeError('port_range')
            if self.port_range[1] < 10240 or self.port_range[0] > 65535:
                raise AttributeError('port_range')
            command += f" --port-range {self.port_range[0]}:{self.port_range[1]}"
        
        # проверка наличия директорий с зображениями
        for dir in self.dirs:
            if not os.path.isdir(dir):
                raise AttributeError('dirs')
            command += f" {dir}"

        # проверка на наличие запрещённых символов
        for c in invalid_characters:
            if c in self.file_name:
                raise AttributeError('filename')

        # проверка на наличие директории конечного файла
        if not os.path.isdir(self.path):
            raise AttributeError('path')
        
        # проверка валидности выбора расширения файла
        if self.extension not in ('mp4', 'webm'):
            raise AttributeError('extension')

        # сборка полного пути файла        
        full_file_path = f"{self.path}/{self.file_name}.{self.extension}"
        command += f" {full_file_path}"

        # проверка, есть ли такой файл, если не установлен флаг перезаписи
        if os.path.isfile(full_file_path) and not self.force_flag:
            return AttributeError('exists')
        
        return command  # возврат полной собранной команды


class GuiCallback:
    """Интерфейс для инъекции внешних методов от gui.
    Позволяет из задачи обновлять статус на слое gui."""

    def __init__(
            self,
            update_function,
            finish_function,
            delete_function,
            ):
        self.update = update_function
        self.finish = finish_function
        self.delete = delete_function
        
    
    @staticmethod  # метод из TaskBar
    def update(progress: float, delta: bool = False):
        """обновление полосы прогресса в окне"""
        ...

    @staticmethod  # метод из RootWindow
    def finish(id: int):
        """сигнал о завершении задачи"""
        ...

    @staticmethod  # метод из RootWindow
    def delete(id: int):
        """сигнал об удалении задачи"""
        ...


class Task:
    """Класс самой задачи, связывающейся с catframes"""

    def __init__(self, id: int, task_config: TaskConfig) -> None:
        self.config = task_config
        self.id = id  # получение уникального номера
        self.done = False  # флаг завершённости
        self.stop_flag = False  # требование остановки

    # запуск задачи (тестовый)
    def start(self, gui_callback: GuiCallback):  # инъекция зависимосей 
        self.gui_callback = gui_callback         # для оповещения наблюдателя

        # запуск фоновой задачи (дальше перепишется через subprocess)
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()
        TaskManager.reg_start(self)

    # поток задачи (тестовый)
    def run(self):
        for i in range(21):
            if self.stop_flag:
                return
            self.gui_callback.update(i/20)
            time.sleep(0.2)
        self.done = True
        TaskManager.reg_finish(self)
        self.gui_callback.finish(self.id)  # сигнал о завершении задачи

    # остановка задачи (тестовая)
    def cancel(self):
        self.stop_flag = True
        TaskManager.reg_finish(self)
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
            'root.lbTest': 'Label 1',
            'root.openSets': 'Settings',
            'root.newTask': 'New task',

            'sets.title': 'Settings',
            'sets.lbLang': 'Language:',
            'sets.btApply': 'Apply',
            'sets.btSave': 'Save',

            'task.title': 'New Task',
            'task.btCreate': 'Create',

            'bar.active': 'processing',
            'bar.inactive': 'complete', 
            'bar.btInfo': 'Info',
            'bar.btCancel': 'Cancel',
            'bar.btDelete': 'Delete',

            'warn.title': 'Warning',
            'warn.lbWarn': 'Warning!',
            'warn.lbText': 'Incomplete tasks!',
            'warn.btBack': 'Back',
            'warn.btExit': 'Leave',
        },
        'русский': {
            'root.title': 'CatFrames',
            'root.lbTest': 'Строка 1',
            'root.openSets': 'Настройки',
            'root.newTask': 'Новая задача',

            'sets.title': 'Настройки',
            'sets.lbLang': 'Язык:',
            'sets.btApply': 'Применить',
            'sets.btSave': 'Сохранить',

            'task.title': 'Новая задача',
            'task.btCreate': 'Создать',

            'bar.lbActive': 'обработка',
            'bar.lbInactive': 'завершено', 
            'bar.btInfo': 'Инфо',
            'bar.btCancel': 'Отмена',
            'bar.btDelete': 'Удалить',
            
            'warn.title': 'Внимание',
            'warn.lbWarn': 'Внимание!',
            'warn.lbText': 'Задачи не завершены!',
            'warn.btBack': 'Назад',
            'warn.btExit': 'Выйти',
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
    def read(tag) -> str:
        try:
            return Lang.data[Lang.current_name][tag]
        except KeyError:  # если тег не найден
            return '-----'
            




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
    @classmethod
    def open(cls, window_cls, name: str) -> Tk:    # принимает класс окна, имя окна
        if not cls.check('root'):                        # проверяем, есть ли корневое окно
            return cls._reg(window_cls(), 'root')        # регистрируем окно как корневое

        if not cls.check(name):                          # проверяем, зарегистрировано ли окно
            window = window_cls(root=cls.call('root'))   # создаём окно, передаём корневое окно
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

    title: Tk.title         # эти атрибуты и методы объекта
    protocol: Tk.protocol   # появятся автоматически при
    destroy: Tk.destroy     # наследовании от Tk или Toplevel

    size: Tuple[int, int]   # размеры (ширина, высота) окна
    name: str               # имя окна для словаря всех окон
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
            if not w_name.startswith('_'):  # если виджет начинается с "_", его обходит
                widget.config(text=Lang.read(f'{self.name}.{w_name}'))

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

        # task_background = '#94d0eb'
        task_background = '#c4f0ff'
        style.configure('Task.TFrame', background=task_background)
        style.configure('Task.TLabel', background=task_background)
        style.configure('Task.Horizontal.TProgressbar', background=task_background)

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


class ScrollableFrame(ttk.Frame):
    """Прокручиваемый (умный) фрейм"""

    def __init__(self, root_window, *args, **kwargs):
        super().__init__(root_window, *args, **kwargs)
        
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
            self._update_scrollbar,  # прокрутки менялась, когда обновляется фрейм 
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

        # первичное обновление полосы, чтобы сразу её не было видно
        self._update_scrollbar_visibility()

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

    def __init__(self, master: ttk.Frame, task: Task):
        super().__init__(master, borderwidth=1, padding=5, style='Task.TFrame')
        self.widgets: dict = {}
        self.task: Task = task
        self.progress: float = 0

        self._init_widgets()
        self.update_texts()
        self._pack_widgets()

    # создание и настрйока виджетов
    def _init_widgets(self):
        self.left_frame = ttk.Frame(self, padding=5, style='Task.TFrame')

        image = Image.open("src/catframes/catmanager_sample/test_static/img.png")
        image_size = (80, 60)
        image = image.resize(image_size, Image.ADAPTIVE)
        image_tk = ImageTk.PhotoImage(image)

        self.widgets['_picture'] = ttk.Label(self.left_frame, image=image_tk)
        self.widgets['_picture'].image = image_tk


        # создании средней части бара
        self.mid_frame = ttk.Frame(self, padding=5, style='Task.TFrame')

        bigger_font = font.Font(size=16)

        # надпись в баре
        self.widgets['_lbPath'] = ttk.Label(  
            self.mid_frame, 
            font=bigger_font, padding=5,
            text=f"/usr/tester/movies/render{self.task.id}.mp4", 
            style='Task.TLabel'
        )

        self.widgets['_lbData'] = ttk.Label(  
            self.mid_frame, 
            font='14', padding=5,
            text=f"test label for options description in task {self.task.id}", 
            style='Task.TLabel'
        )


        # создание правой части бара
        self.right_frame = ttk.Frame(self, padding=5, style='Task.TFrame')
       
        # кнопка "отмена"
        self.widgets['btCancel'] = ttk.Button(self.right_frame, width=8, command=lambda: self.task.cancel())
        
        # полоса прогресса
        self.widgets['_progressBar'] = ttk.Progressbar(
            self.right_frame, 
            # length=320,
            maximum=1,
            value=0,
            style='Task.Horizontal.TProgressbar'
        )

    # упаковка всех виджетов бара
    def _pack_widgets(self):
        self.widgets['_picture'].pack(side='left')
        self.left_frame.pack(side='left')

        self.widgets['_lbPath'].pack(side='top', fill='x', expand=True)
        self.widgets['_lbData'].pack(side='top', fill='x', expand=True)
        self.mid_frame.pack(side='left')

        self.widgets['btCancel'].pack(side='bottom', expand=True)
        self.widgets['_progressBar'].pack(side='bottom', expand=True)
        self.right_frame.pack(side='left', expand=True)

        self.pack(pady=[0, 10])

    # обновление кнопки "отмена" после завершения задачи
    def update_cancel_button(self):
        self.widgets['btDelete'] = self.widgets.pop('btCancel')  # переименование кнопки
        self.widgets['btDelete'].config(
            command=lambda: self.task.delete(),  # переопределение поведения кнопки
        )
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
                widget.config(text=Lang.read(f'bar.{w_name}'))





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
        
        self.widgets:   dict[str, ttk.Widget] = {}
        self.task_bars: dict[int, TaskBar] = {}  # словарь регистрации баров задач

        self.size = 500, 450
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
        self.task_bars[task_id].delete()  # удаляет таскбар
        del self.task_bars[task_id]  # чистит регистрацию

    # закрытие задачи, смена виджета
    def finish_task_bar(self, task_id: int) -> None:
        if task_id in self.task_bars:
            self.task_bars[task_id].update_cancel_button()
        LocalWM.update_on_task_finish()

    # расширение метода обновления текстов
    def update_texts(self) -> None:
        super().update_texts()
        for bar in self.task_bars.values():
            bar.update_texts()  # обновляет текст в каждом баре


class SettingsWindow(Toplevel, WindowMixin):
    """Окно настроек"""

    def __init__(self, root: RootWindow):
        super().__init__(master=root)
        self.name = 'sets'

        self.widgets: dict[str, ttk.Widget] = {}

        self.size = 250, 200
        self.resizable(False, False)

        super()._default_set_up()

    # создание и настройка виджетов
    def _init_widgets(self):

        # применение настроек
        def apply_settings():
            Lang.set(index=self.widgets['cmbLang'].current())  # установка языка
            for w in LocalWM.all():  # перебирает все прописанные в менеджере окна
                w.update_texts()  # для каждого обновляет текст методом из WindowMixin

            ...  # считывание других виджетов настроек, и применение

        # сохранение настроек (применение + закрытие)
        def save_settings():
            apply_settings()
            self.close()

        # создание виджетов, привязывание функций
        self.widgets['lbLang'] = ttk.Label(self)
        self.widgets['cmbLang'] = ttk.Combobox(  # виджет выпадающего списка
            self,
            values=Lang.get_all(),  # вытягивает список языков
            state='readonly',  # запрещает вписывать, только выбирать
            width=7
        )
        
        self.widgets['btApply'] = ttk.Button(self, command=apply_settings, width=7)
        self.widgets['btSave'] = ttk.Button(self, command=save_settings, width=7)

    # расположение виджетов
    def _pack_widgets(self):

        for c in range(2): 
            self.columnconfigure(index=c, weight=1)
        for r in range(5): 
            self.rowconfigure(index=r, weight=1)
        
        self.widgets['lbLang'].grid(row=0, column=0, sticky='w', padx=20)
        self.widgets['cmbLang'].grid(row=0, column=1, sticky='ew', padx=(5 ,15))
        self.widgets['cmbLang'].current(newindex=Lang.current_index)  # подставляем в ячейку текущий язык

        self.widgets['btApply'].grid(row=4, column=0, sticky='ew', padx=(15, 5), ipadx=30)
        self.widgets['btSave'].grid(row=4, column=1, sticky='ew', padx=(5, 15), ipadx=30)


class NewTaskWindow(Toplevel, WindowMixin):
    """Окно создания новой задачи"""

    def __init__(self, root: RootWindow):
        super().__init__(master=root)
        self.name = 'task'
        self.widgets = {}
        self.task_config = TaskConfig()

        self.size = 300, 250
        self.resizable(False, False)

        super()._default_set_up()

    # подсветка виджета цветом предупреждения
    def mark_error_widget(self, widget_name):
        print(f'подсветит виджет {widget_name}')

    # валидация текущего конфига
    def _validate_task_config(self) -> bool:
        try:                                        # пробует конвертировать конфиг 
            self.task_config.convert_to_command()   # в команду, проверив каждый атрибут
            return True
        except AttributeError as e:                 # если поймает ошибку, то вызовет
            self.mark_error_widget(str(e))          # метод подсветки виджета с ошибкой
            return False

    # создание и запуск задачи
    def _create_task_instance(self):

        # создание задачи через менеджер задач
        task = TaskManager.create(self.task_config)

        # создание бара задачи, получение метода обновления прогресса
        update_progress: Callable = self.master.add_task_bar(task)

        gui_callback = GuiCallback(                       # создание колбека
            update_function=update_progress,              # передача методов обновления,
            finish_function=self.master.finish_task_bar,  # завершения задачи
            delete_function=self.master.del_task_bar      # и удаления бара
        )

        task.start(gui_callback)  # инъекция колбека для обнволения gui при старте задачи

    # создание и настройка виджетов
    def _init_widgets(self):
        
        def add_task():  # обработка кнопки добавления задачи
            if self._validate_task_config():  # если конфиг корректный
                self._create_task_instance()  # создаёт и запускает задачу
                self.close()                  # закрывает окно

        self.widgets['btCreate'] = ttk.Button(self, command=add_task)

        def ask_directory():
            dirpath = filedialog.askdirectory()
            if dirpath and dirpath not in self.task_config.dirs:
                self.task_config.dirs.append(dirpath)
            self.focus()

        def ask_color():
            color = colorchooser.askcolor()[-1]
            self.task_config.margin_color = color
            self.widgets['_btColor'].configure(background=color, text=color)
            self.focus()

        self.widgets['btAddDir'] = ttk.Button(self, command=ask_directory)
        self.widgets['_btColor'] = Button(self, background='#999999', command=ask_color, text='#999999')


    # расположение виджетов
    def _pack_widgets(self):
        self.widgets['btCreate'].pack(side='bottom', pady=15)
        self.widgets['btAddDir'].pack(side='top', pady=15)
        self.widgets['_btColor'].pack(side='top')


class WarningWindow(Toplevel, WindowMixin):
    """Окно предупреждения при выходе"""

    def __init__(self, root: RootWindow):
        super().__init__(master=root)
        self.name = 'warn'
        self.widgets = {}

        self.size = 260, 120
        self.resizable(False, False)

        super()._default_set_up()

    # создание и настройка виджетов
    def _init_widgets(self):
        
        def back():
            self.close()

        def exit():
            print('TODO остановка всех задач')
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





    #  из файла main.py:

def main():
    root = LocalWM.open(RootWindow, 'root')  # открываем главное окно
    root.mainloop()

if __name__ == "__main__":
    main()



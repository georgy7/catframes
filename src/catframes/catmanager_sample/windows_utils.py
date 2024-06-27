from abc import ABC, abstractmethod
from tkinter import Tk, ttk, Canvas
from sets_utils import Lang, TTK_THEME, MAJOR_SCALING
from task_flows import Task
from typing import Optional, Tuple, Dict


class WindowMixin(ABC):
    """Абстрактный класс.
    Упрощает конструкторы окон."""

    all_windows: dict = {}  # общий словарь регистрации для всех окон

    title: Tk.title         # эти атрибуты и методы объекта
    protocol: Tk.protocol   # появятся автоматически при
    destroy: Tk.destroy     # наследовании от Tk или Toplevel

    size: Tuple[int, int]   # размеры (ширина, высота) окна
    name: str               # имя окна для словаря всех окон
    widgets: Dict[str, ttk.Widget]  # словарь виджетов окна

    # настройка окна, вызывается через super в конце __init__ окна
    def _default_set_up(self):
        self.all_windows[self.name] = self  # регистрация окна в словаре
        self.protocol("WM_DELETE_WINDOW", self.close)  # что выполнять при закрытии

        self._set_style()     # настройка внешнего вида окна
        self._to_center()     # размещение окна в центре экрана
        self._init_widgets()  # создание виджетов
        self.update_texts()   # установка текста нужного языка
        self._pack_widgets()  # расстановка виджетов

    # закрытие окна
    def close(self) -> None:
        try:  # удаляет окно из словаря регистрации
            self.all_windows.pop(self.name)
        except KeyError:
            pass
        self.destroy()  # закрывает окно

    # обновление текстов всех виджетов окна, исходя из языка
    def update_texts(self) -> None:
        self.title(Lang.read(f'{self.name}.title'))

        for w_name, widget in self.widgets.items():
            if not w_name.startswith('_'):  # если виджет начинается с "_", его обходит
                widget.config(text=Lang.read(f'{self.name}.{w_name}'))

    # размещение окна в центре экрана
    def _to_center(self) -> None:
        # размещение окна в центре экрана
        x = (self.winfo_screenwidth() - self.size[0]) / 2
        y = (self.winfo_screenheight() - self.size[1]) / 2
        self.geometry(f'+{int(x)}+{int(y)}')


    # настройка стиля окна, исходя из разрешения экрана
    def _set_style(self) -> None:

        screen_height = self.winfo_screenheight()  # достаём высоту экрана
        scale = (screen_height/540)                # индекс масштабирования
        scale *= MAJOR_SCALING                     # домножаем на глобальную

        style=ttk.Style()
        if TTK_THEME: style.theme_use(TTK_THEME)   # применение темы, если есть
        style.tk.call('tk', 'scaling', scale)      # установка масштаба окна

        x, y = self.size                   # забираем объявленные размеры окна
        x, y = int(x*scale), int(y*scale)  # масштабируем их
        self.geometry(f'{x}x{y}')          # и присваиваем их окну

    # метод для создания и настройки виджетов
    @abstractmethod
    def _init_widgets(self) -> None:
        ...

    # метод для расположения виджетов
    @abstractmethod
    def _pack_widgets(self, ) -> None:
        ...


class ScrollableFrame(ttk.Frame):
    """Прокручиваемый (умный) фрейм"""

    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        
        self.canvas = Canvas(self, highlightthickness=0)  # объект "холста"

        self.scrollbar = ttk.Scrollbar(  # полоса прокрутки
            self, orient="vertical",     # установка в вертикальное положение
            command=self.canvas.yview,   # передача управления вертикальной прокруткой холста
        )  

        self.scrollable_frame = ttk.Frame(self.canvas, padding=[15, 0])  # фрейм для контента (внутренних виджетов)
        self.scrollable_frame.bind(  # привязка к виджету фрейма 
            "<Configure>",           # обработчика событий <Configure>, чтобы полоса
            self._update_scrollbar,  # прокрутки менялась, когда обновляется фрейм 
        )

        # привязка холста к верхнему левому углу
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

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
        super().__init__(master, relief='solid', padding=5)
        self.widgets: dict = {}
        self.task: Task = task
        self.progress: float = 0

        self._init_widgets()
        self.update_texts()
        self._pack_widgets()

    # создание и настрйока виджетов
    def _init_widgets(self):

        # создании левой части бара
        self.progress_frame = ttk.Frame(self, padding=5)

        # надпись в баре
        self.widgets['_lbName'] = ttk.Label(  
            self.progress_frame, 
            font='14', padding=5,
            text=f"test task space {self.task.number}", 
        )

        # полоса прогресса
        self.widgets['_progressBar'] = ttk.Progressbar(
            self.progress_frame, 
            length=320,
            maximum=1,
            value=0,
        )

        # создание правой части бара
        self.button_frame = ttk.Frame(self, padding=5)

        # кнопки "инфо" и "стоп"
        def show_info():
            print('TODO окошко с информацией')    
        self.widgets['btInfo'] = ttk.Button(self.button_frame, command=show_info)
        self.widgets['btStop'] = ttk.Button(self.button_frame, command=lambda: self.task.stop())


    # упаковка всех виджетов бара
    def _pack_widgets(self):
        self.widgets['_lbName'].pack(side='top')
        self.widgets['_progressBar'].pack(side='bottom')
        self.progress_frame.pack(side='left')

        self.widgets['btInfo'].pack(side='top')
        self.widgets['btStop'].pack(side='bottom')
        self.button_frame.pack(side='right')

        self.pack(pady=[0, 10])

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

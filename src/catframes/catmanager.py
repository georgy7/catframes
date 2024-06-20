#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from tkinter import Tk, Toplevel, ttk
from abc import ABC, abstractmethod


# временные глобальные переменные
MAJOR_SCALING: float = 1.0
TTK_THEME: str | None = None


class Lang:
    """Класс языковых настроек.
    Позволяет хранить текущий язык,
    И извлекать его текстовики.

    При добавлении новых языков в словарь data,
    их названия будут сами подтягиваться в поле настроек.
    """

    current_name = 'english'
    current_index = 0

    data = {  # языковые теги (ключи) имеют вид: "окно.элемент"
        'english': {
            'root.title': 'CatFrames',
            'root.lbTest': 'Label 1',
            'root.openSets': 'Settings',
            'root.newTask': 'New task',

            'sets.title': 'Settings',
            'sets.lbLang': 'Language:',
            'sets.btApply': 'Apply',
            'sets.btSave': 'Save',

            'task.title': 'New Task'
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

            'task.title': 'Новая задача'
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


#


class WindowMixin(ABC):
    """Абстрактный класс.
    Упрощает конструкторы окон."""

    all_windows: dict = {}  # общий словарь регистрации для всех окон

    title: Tk.title         # эти атрибуты и методы объекта
    protocol: Tk.protocol   # появятся автоматически при
    destroy: Tk.destroy     # наследовании от Tk или Toplevel

    size: tuple[int, int]   # размеры (ширина, высота) окна
    name: str               # имя окна для словаря всех окон
    widgets: dict[str, ttk.Widget]  # словарь виджетов окна

    # настройка окна, вызывается через super в конце __init__ окна
    def _default_set_up(self):
        self.all_windows[self.name] = self  # регистрация окна в словаре
        self.protocol("WM_DELETE_WINDOW", self.close)  # что выполнять при закрытии

        self._set_style()     # настройка внешнего вида окна
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
            widget.config(text=Lang.read(f'{self.name}.{w_name}'))

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
    def _pack_widgets(self) -> None:
        ...


#


class RootWindow(Tk, WindowMixin):
    """Основное окно"""

    def __init__(self):
        super().__init__()
        self.name = 'root'
        
        self.widgets: dict[str, ttk.Widget] = {}
        self.frames:  dict[str, ttk.Frame] = {}

        self.size = 300, 250
        self.resizable(False, False)  # нельзя растягивать

        super()._default_set_up()

    # при закрытии окна
    def close(self):
        print('TODO проверка незавершённых задач')
        self.destroy()

    # создание и настройка виджетов
    def _init_widgets(self):

        # открытие окна с новой задачей
        def open_new_task():
            if not self.all_windows.get('task'):  # если не нашёл окно в словаре
                NewTaskWindow(root=self)  # создать окно (само добавится в словарь)
            self.all_windows['task'].focus()  # фокусируется на нём

        # открытие окна настроек
        def open_settings():
            if not self.all_windows.get('sets'):
                SettingsWindow(root=self)
            self.all_windows['sets'].focus()

        # создание фреймов
        self.frames['upperBar'] = upperBar = ttk.Frame(self)

        # создание виджетов, привязывание функций
        self.widgets['newTask'] = ttk.Button(upperBar, command=open_new_task)
        self.widgets['openSets'] = ttk.Button(upperBar, command=open_settings)

    # расположение виджетов
    def _pack_widgets(self):
        self.frames['upperBar'].pack(fill='x', padx=15, pady=15)

        self.widgets['newTask'].pack(side='left')
        self.widgets['openSets'].pack(side='right')


#


class SettingsWindow(Toplevel, WindowMixin):
    """Окно настроек"""

    def __init__(self, root: RootWindow):
        super().__init__(master=root)
        self.name = 'sets'

        self.widgets: dict[str, ttk.Widget] = {}

        self.size = 130, 100
        self.resizable(False, False)

        super()._default_set_up()

    # создание и настройка виджетов
    def _init_widgets(self):

        # применение настроек
        def apply_settings():
            Lang.set(index=self.widgets['cmbLang'].current())  # установка языка
            for w in self.all_windows.values():  # перебирает все окна в словаре регистрации
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


#


class NewTaskWindow(Toplevel, WindowMixin):
    """Окно создания новой задачи"""

    def __init__(self, root: RootWindow):
        super().__init__(master=root)
        self.name = 'task'
        self.widgets = {}

        self.size = 200, 150
        self.resizable(False, False)

        super()._default_set_up()

    # создание и настройка виджетов
    def _init_widgets(self):
        pass

    # расположение виджетов
    def _pack_widgets(self):
        pass


if __name__ == "__main__":
    RootWindow().mainloop()

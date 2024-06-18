#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from tkinter import Tk, Toplevel, ttk, font
from abc import ABC, abstractmethod


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

            'sets.title': 'Settings Menu',
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

            'sets.title': 'Меню Настроек',
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


class Styles(ttk.Style):
    """Класс для определения стилей виджетов"""

    def __init__(self, root: Tk):
        super().__init__()
        self.theme_use('alt')  # одна из стандартных тем, для примера
        self.configure(style='TButton', font='14')  # шрифт текста в кнопке
        root.option_add("*Font", font.Font(size=14))  # шрифты остальных виджетов


#


class WindowMixin(ABC):
    """Абстрактный класс.
    Упрощает конструкторы окон."""

    all_windows: dict = {}  # общий словарь регистрации для всех окон

    title: Tk.title         # эти атрибуты и методы объекта
    protocol: Tk.protocol   # появятся автоматически при
    destroy: Tk.destroy     # наследовании от Tk или Toplevel

    name: str               # имя окна для словаря всех окон
    widgets: dict           # словарь виджетов окна

    # настройка окна, вызывается через super в конце __init__ окна
    def _default_set_up(self):
        self.all_windows[self.name] = self  # регистрация окна в словаре
        self.protocol("WM_DELETE_WINDOW", self.close)  # что выполнять при закрытии

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
        self.widgets = {}

        self.geometry("600x500")  # размеры  окна
        self.resizable(False, False)  # нельзя растягивать

        self.styles = Styles(self)
        super()._default_set_up()

    # при закрытии окна
    def close(self):
        print('TODO проверка незавершённых задач')
        self.destroy()

    # создание и настройка виджетов
    def _init_widgets(self):

        # открытие окна с новой задачей
        def open_new_task():
            if self.all_windows.get('task'):  # если нашёл окно в словаре регистрации
                return self.all_windows['task'].focus()  # фокусируется на нём
            self.all_windows['task'] = NewTaskWindow(root=self)  # если не нашёл - создать

        # открытие окна настроек
        def open_settings():
            if self.all_windows.get('sets'):
                return self.all_windows['sets'].focus()
            self.all_windows['sets'] = SettingsWindow(root=self)

        # создание виджетов, привязывание функций
        self.widgets['newTask'] = ttk.Button(self, command=open_new_task)
        self.widgets['openSets'] = ttk.Button(self, command=open_settings)

    # расположение виджетов
    def _pack_widgets(self):
        self.widgets['newTask'].place(x=15, y=15, width=150, height=30)
        self.widgets['openSets'].place(relx=1.0, x=-165, y=15, width=150, height=30)


class SettingsWindow(Toplevel, WindowMixin):
    """Окно настроек"""

    def __init__(self, root: RootWindow):
        super().__init__(master=root)
        self.name = 'sets'
        self.widgets = {}

        self.geometry("260x200")
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
        self.widgets['btApply'] = ttk.Button(self, command=apply_settings)
        self.widgets['btSave'] = ttk.Button(self, command=save_settings)
        self.widgets['lbLang'] = ttk.Label(self)
        self.widgets['cmbLang'] = ttk.Combobox(  # виджет выпадающего списка
            self,
            values=Lang.get_all(),  # вытягивает список языков
            state='readonly'  # запрещает вписывать, только выбирать
        )

    # расположение виджетов
    def _pack_widgets(self):
        self.widgets['lbLang'].place(x=15, y=15, width=110, height=30)
        self.widgets['cmbLang'].place(relx=1.0, x=-125, y=15, width=110, height=30)
        self.widgets['cmbLang'].current(newindex=Lang.current_index)  # подставляем в ячейку текущий язык
        self.widgets['btApply'].place(rely=1.0, x=15, y=-45, width=110, height=30)
        self.widgets['btSave'].place(rely=1.0, relx=1.0, x=-125, y=-45, width=110, height=30)


class NewTaskWindow(Toplevel, WindowMixin):
    """Окно создания новой задачи"""

    def __init__(self, root: RootWindow):
        super().__init__(master=root)
        self.name = 'task'
        self.widgets = {}

        self.geometry("400x300")
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

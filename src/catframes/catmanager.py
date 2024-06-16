#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from tkinter import Tk, Toplevel, ttk, font


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

    def __init__(self, root_window: Tk):
        super().__init__()
        self.theme_use('alt')
        self.configure(style='TButton', font='14')  # имя, шрифт
        root_window.option_add("*Font", font.Font(size=14))


class WindowMixin:
    """Хранит общие для окон методы"""

    title: Tk.title
    # атрибуты ниже нужно имплементировать вручную
    name: str
    widgets: dict

    # обновление текстов всех виджетов, исходя из языка
    def update_texts(self):
        self.title(Lang.read(f'{self.name}.title'))
        for w_name, widget in self.widgets.items():
            widget.config(text=Lang.read(f'{self.name}.{w_name}'))


#


class RootWindow(Tk, WindowMixin):
    """Основное окно"""

    def __init__(self):
        super().__init__()
        self.name = 'root'
        self.widgets: dict = {}

        self.geometry("600x500")
        self.minsize(600, 500)
        self.resizable(False, False)

        self._init_widgets()
        self.update_texts()
        self._pack_widgets()
        self.styles = Styles(self)

        self.settings_window: Toplevel | None = None
        self.new_task_window: Toplevel | None = None

    # создание и настройка виджетов
    def _init_widgets(self):

        def open_new_task():
            if self.new_task_window:
                print('TODO фокусировка')
            print('TODO открытие окна')
        self.widgets['newTask'] = ttk.Button(self, command=open_new_task, style='TButton')

        def open_settings():
            if self.settings_window:
                return self.settings_window.focus()
            self.settings_window = SettingsWindow(root_window=self)
        self.widgets['openSets'] = ttk.Button(self, command=open_settings, style='TButton')

    # расположение виджетов
    def _pack_widgets(self):
        # self.widgets['lbl_1'].place()
        self.widgets['newTask'].place(x=15, y=15, width=150, height=30)
        self.widgets['openSets'].place(relx=1.0, x=-165, y=15, width=150, height=30)


#


class SettingsWindow(Toplevel, WindowMixin):
    """Окно настроек"""

    def __init__(self, root_window: RootWindow):
        super().__init__(master=root_window)
        self.name = 'sets'
        self.widgets: dict = {}

        self.root_window = root_window
        self.protocol("WM_DELETE_WINDOW", self.close)

        self.geometry("260x200")
        self.resizable(False, False)
        self._init_widgets()
        self.update_texts()
        self._pack_widgets()

    # закрытие окна
    def close(self):
        self.master.settings_window = None
        self.destroy()

    # создание и настройка виджетов
    def _init_widgets(self):
        self.widgets['lbLang'] = ttk.Label(self, style='TLabel')
        self.widgets['cmbLang'] = ttk.Combobox(self, values=Lang.get_all(), state='readonly')

        # кнопка применения настроек
        def apply_settings():
            Lang.set(index=self.widgets['cmbLang'].current())
            self.update_texts()
            self.root_window.update_texts()
        self.widgets['btApply'] = ttk.Button(self, command=apply_settings, style='TButton')

        # кнопка сохранения настроек (применение + закрытие)
        def save_settings():
            apply_settings()
            self.close()
        self.widgets['btSave'] = ttk.Button(self, command=save_settings, style='TButton')

    # расположение виджетов
    def _pack_widgets(self):
        self.widgets['lbLang'].place(x=15, y=15, width=110, height=30)
        self.widgets['cmbLang'].place(relx=1.0, x=-125, y=15, width=110, height=30)
        self.widgets['cmbLang'].current(newindex=Lang.current_index)

        self.widgets['btApply'].place(rely=1.0, x=15, y=-45, width=110, height=30)
        self.widgets['btSave'].place(rely=1.0, relx=1.0, x=-125, y=-45, width=110, height=30)


if __name__ == "__main__":
    root = RootWindow()
    root.mainloop()

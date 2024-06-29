from _prefix import *
from sets_utils import Lang
from windows_utils import ScrollableFrame, TaskBar
from task_flows import Task, GuiCallback, TaskManager
from windows_base import WindowMixin, LocalWM


class RootWindow(ThemedTk, WindowMixin):
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
        print('TODO смена виджета на виджет завершенной задачи')
        LocalWM.update_on_task_finish()

    # остановка задачи, смена виджета
    def cancel_task_bar(self, task_id: int) -> None:
        print('TODO смена виджета на виджет отменённой задачи')

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

        self.size = 300, 250
        self.resizable(False, False)

        super()._default_set_up()

    # создание и настройка виджетов
    def _init_widgets(self):
        
        def add_task():
            params: dict = {
                # вытягивание аргументов из виджетов настроек задачи
            }
            task = TaskManager.create(**params)

            # создание бара задачи, получение метода обновления прогресса
            update_progress: Callable = self.master.add_task_bar(task, **params)

            gui_callback = GuiCallback(  # создание колбека
                update_function=update_progress,  # передача методов обновления
                finish_function=self.master.finish_task_bar  # и завершения задачи
            )  

            task.start(gui_callback)  # инъекция колбека для обнволения gui
            self.close()

        self.widgets['btCreate'] = ttk.Button(self, command=add_task)

    # расположение виджетов
    def _pack_widgets(self):
        self.widgets['btCreate'].pack(side='bottom', pady=15)


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

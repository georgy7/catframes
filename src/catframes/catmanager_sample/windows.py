from _prefix import *
from sets_utils import Lang
from windows_utils import ScrollableFrame, TaskBar, ImageCanvas, DirectoryManager
from task_flows import Task, GuiCallback, TaskManager, TaskConfig
from windows_base import WindowMixin, LocalWM


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

        self.widgets: Dict[str, ttk.Widget] = {}

        self.size = 250, 200
        self.resizable(False, False)

        super()._default_set_up()

    # создание и настройка виджетов
    def _init_widgets(self):

        # применение настроек
        def apply_settings():
            Lang.set(index=self.widgets['_cmbLang'].current())  # установка языка
            for w in LocalWM.all():  # перебирает все прописанные в менеджере окна
                w.update_texts()  # для каждого обновляет текст методом из WindowMixin

            ...  # считывание других виджетов настроек, и применение

        # сохранение настроек (применение + закрытие)
        def save_settings():
            apply_settings()
            self.close()

        # создание виджетов, привязывание функций
        self.widgets['lbLang'] = ttk.Label(self)
        self.widgets['_cmbLang'] = ttk.Combobox(  # виджет выпадающего списка
            self,
            values=Lang.get_all(),  # вытягивает список языков
            state='readonly',  # запрещает вписывать, только выбирать
            width=7,
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
        self.widgets['_cmbLang'].grid(row=0, column=1, sticky='ew', padx=(5 ,15))
        self.widgets['_cmbLang'].current(newindex=Lang.current_index)  # подставляем в ячейку текущий язык

        self.widgets['btApply'].grid(row=4, column=0, sticky='ew', padx=(15, 5), ipadx=30)
        self.widgets['btSave'].grid(row=4, column=1, sticky='ew', padx=(5, 15), ipadx=30)


class NewTaskWindow(Toplevel, WindowMixin):
    """Окно создания новой задачи"""

    def __init__(self, root: RootWindow):
        super().__init__(master=root)
        self.name = 'task'
        self.widgets: Dict[str, Widget] = {}
        self.task_config = TaskConfig()
        self.dirlist = []   # временный список директорий. Позже будет структура, аналогичная таскбарам

        self.size = 800, 650
        self.resizable(True, True)

        super()._default_set_up()

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
        update_progress: Callable = self.master.add_task_bar(task)

        gui_callback = GuiCallback(                       # создание колбека
            update_function=update_progress,              # передача методов обновления,
            finish_function=self.master.finish_task_bar,  # завершения задачи
            delete_function=self.master.del_task_bar      # и удаления бара
        )

        task.start(gui_callback)  # инъекция колбека для обнволения gui при старте задачи

    # создание и настройка виджетов
    def _init_widgets(self):            
        self.image_canvas = ImageCanvas(  # создание холста с изображением
            self, 
            width=800, height=400,
            image_link="src/catframes/catmanager_sample/test_static/img.jpg", 
            background='#888888'
        )
        self.bottom_grid = Frame(self)    # создание табличного фрейма ниже холста
        self.dir_manager = DirectoryManager(self.bottom_grid)
        
        def add_task():  # обработка кнопки добавления задачи
            self._collect_task_config()   # сбор данных конфигурации с виджетов
            if not self.dir_manager.validate_dirs(): # если каких-то директорий нет,
                return                    # дальнейшие действия не произойдут
            
            dirs = self.dir_manager.get_dirs()
            self.task_config.set_dirs(dirs)

            if not self._set_filepath():  # если путь сохранения не выбирается,
                return                    #     дальнейшие действия не произойдут
            self._create_task_instance()  # воздание и запуск задачи
            self.close()                  # закрытие окна задачи

        def ask_color():  # вызов системного окна по выбору цвета
            color = colorchooser.askcolor(parent=self)[-1]
            self.image_canvas.update_background_color(color)
            self.task_config.set_color(color)  # установка цвета в конфиге
            self.widgets['_btColor'].configure(background=color, text=color)  # цвет кнопки

        def test():  # тестовая функция, меняет картинку, и выводит строки с холста
            self.image_canvas.update_image(
                image_link="src/catframes/catmanager_sample/test_static/img2.jpg"
            )
            print(self.image_canvas.fetch_entries_text())

        # виджеты столбца описания кнопок
        self.widgets['lbColor'] = ttk.Label(self.bottom_grid)
        self.widgets['lbFramerate'] = ttk.Label(self.bottom_grid)
        self.widgets['lbQuality'] = ttk.Label(self.bottom_grid)

        # виджеты правого столбца (кнопка цвета, комбобоксы и кнопка создания задачи)
        self.widgets['_btColor'] = Button(self.bottom_grid, command=ask_color, text='#888888', width=7)
        self.widgets['_cmbFramerate'] = ttk.Combobox(  # виджет выбора фреймрейта
            self.bottom_grid,
            values=(60, 50, 40, 30, 25, 20, 15, 10, 5), 
            state='readonly',
            justify='center',
            width=8,
        )
        self.widgets['cmbQuality'] = ttk.Combobox(  # виджет выбора качества
            self.bottom_grid,
            state='readonly',
            justify='center',
            width=8,
        )
        self.widgets['btCreate'] = ttk.Button(self.bottom_grid, command=add_task)

    # расположение виджетов
    def _pack_widgets(self):
        # упаковка нижнего фрейма для сетки
        self.bottom_grid.pack(side='bottom', fill='both', expand=True, pady=10, padx=30)

        # настройка веса столбцов
        for i in range(4):
            self.bottom_grid.columnconfigure(i, weight=1)

        # настройка веса строк
        for i in range(6):
            self.bottom_grid.rowconfigure(i, weight=1)

        # заполнение левого столбца
        self.dir_manager.grid(
            row=0, column=0, rowspan=6, columnspan=2
        )

        # заполнение столбца описания кнопок (липнет вправо, к правому столбцу)        
        self.widgets['lbColor'].grid(row=1, column=2, sticky='e', padx=10)
        self.widgets['lbFramerate'].grid(row=2, column=2, sticky='e', padx=10)
        self.widgets['lbQuality'].grid(row=3, column=2, sticky='e', padx=10)

        # заполнение правого столбца (липнет влево, к столбцу описаний)
        ttk.Label(self.bottom_grid).grid(row=0, column=3)
        self.widgets['_btColor'].grid(row=1, column=3, sticky='w', padx=7)
        self.widgets['_cmbFramerate'].grid(row=2, column=3, sticky='w', padx=7)
        self.widgets['_cmbFramerate'].current(newindex=3)
        self.widgets['cmbQuality'].grid(row=3, column=3, sticky='w', padx=7)
        self.widgets['btCreate'].grid(row=4, column=3, sticky='w', padx=7)
        ttk.Label(self.bottom_grid).grid(row=5, column=3)

    # расширение метода обновления текстов
    def update_texts(self) -> None:
        super().update_texts()
        self.dir_manager.update_texts()


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

from _prefix import *
from sets_utils import Lang, PortSets
from windows_utils import ScrollableFrame, TaskBar, ImageCanvas, DirectoryManager, ToolTip, is_dark_color
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
        self.upper_bar.pack(fill=X, padx=15, pady=15)
        self.task_space.pack(fill=BOTH, expand=True)

        self.widgets['newTask'].pack(side=LEFT)
        self.widgets['openSets'].pack(side=RIGHT)
        
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
            justify=CENTER, 
            validate='key', 
            validatecommand=v_numeric  # привязка валидации
        )
        self.widgets['_entrPortLast'] = ttk.Entry(  # поле ввода конечного порта
            self, 
            justify=CENTER, 
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

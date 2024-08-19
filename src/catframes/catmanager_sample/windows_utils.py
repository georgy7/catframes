from _prefix import *
from sets_utils import Lang
from task_flows import Task
from windows_base import LocalWM


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
    def set_error(self):
        self._set_style(2)
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
                widget.config(text=Lang.read(f'{self.name}.{w_name}'))


class ImageCanvas(Canvas):
    """Объект холста с картинкой в окне создания задачи.
    на которой отображаются "умные" поля ввода.
    Если текст не введён - поле будет полупрозрачным."""
    
    def __init__(
            self, 
            master: Tk, 
            veiw_mode: bool,
            resolution: Optional[Tuple[int]] = None, 
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
    def update_resolution(self, resolution) -> int:
        ratio = resolution[0]/resolution[1]  # вычисляет соотношение сторон разрешения рендера
        last_height = self.height            # запоминает предыдущую высоту
        if self.width < self.default_width:
            self.width = self.default_width

        self.height = int(self.width/ratio)  # высота холста растягивается по соотношению
        
        if self.height > 600:                # но если высота больше 600
            self.height = 600                # то высота выставляется в 600
            self.width = int(self.height*ratio)  # а ширина выставляется по соотношению

        self.config(height=self.height, width=self.width)  # установка новых размеров

        self._setup_entries()                # обновляет позиции и настройки всех виджетов
        return self.height-last_height       # возвращает изменение высоты

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


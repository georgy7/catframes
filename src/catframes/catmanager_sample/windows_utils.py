from _prefix import *
from sets_utils import Settings
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

# переводчит base64 картинку в tk
def base64_to_tk(image_base64):
    image_data = base64.b64decode(image_base64)   # декодируем base64
    image = Image.open(io.BytesIO(image_data))    # обрабатываем, как файл
    return ImageTk.PhotoImage(image)              # переводим в тк

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

    try:
        addit = limit - len(f"{shrink[0]}{s}...{s}{s.join(shrink[1:])}")  # вычисляем недостающую длину
        start = len(dirs[-1]) - addit         # берём стартовый индекс для невлазящей директории 
        shrink.insert(1, dirs[-1][start::])   # берём последнюю часть невлазящей директории
    except:
        pass

    # сборка строки нового пути, передача её, если она короче изначальной
    new_path = f"{shrink[0]}{s}...{s.join(shrink[1:])}"
    return new_path if len(new_path) < len(path) else path


class ScrollableFrame(ttk.Frame):
    """Прокручиваемый (умный) фрейм"""

    def __init__(self, root_window, *args, **kwargs):
        super().__init__(root_window, *args, **kwargs, style='Main.TFrame')
        
        self.root = root_window
        self.canvas = Canvas(self, highlightthickness=0)  # объект "холста"
        if not platform.system() == 'Darwin':  # если это не macos, добавить холсту цвет
            self.canvas.config(bg=MAIN_TASKLIST_COLOR)
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
    #     self._empty_sign.config(text=Settings.lang.read('bar.lbEmpty'))

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

    def __init__(self, master: ttk.Frame, task: Task, cancel_def: Callable, **kwargs):
        super().__init__(master, borderwidth=1, padding=5, style='Scroll.Task.TFrame')
        self.name = 'bar'
        self.widgets: Dict[str, Widget] = {}
        self.task: Task = task
        self.cancel_def = cancel_def
        self.progress: float = 0
        self.image: Image
        self.length: int = 520
        self.error: str = None
        self.open_view: Callable = kwargs.get('view')  # достаёт ручку для открытия окна просмотра

        self._init_widgets()
        self.update_texts()
        self._pack_widgets()
        self._update_labels()

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

        img_dir = self.task.config.get_dirs()[0]                # достаём первую директорию
        img_path = find_img_in_dir(img_dir, full_path=True)[0]  # берём первую картинку

        image = Image.open(img_path)
        image_size = (80, 60)
        image = image.resize(image_size, Image.ADAPTIVE)
        self.image_tk = ImageTk.PhotoImage(image)

        self.widgets['_picture'] = ttk.Label(self.left_frame, image=self.image_tk)

        # создании средней части бара
        self.mid_frame = ttk.Frame(self, padding=5)

        bigger_font = font.Font(size=16)

        # надпись в баре
        self.widgets['_lbPath'] = ttk.Label(  
            self.mid_frame, 
            font=bigger_font, padding=5,
            text=shrink_path(self.task.config.get_filepath(), 30), 
        )

        self.widgets['_lbData'] = ttk.Label(
            self.mid_frame, 
            font='14', padding=5,
        )

        # создание правой части бара
        self.right_frame = ttk.Frame(self, padding=5)
        
        # кнопка "отмена"
        self.widgets['btCancel'] = ttk.Button(
            self.right_frame, 
            width=10, 
            command=self.cancel_def
        )
        
        # полоса прогресса
        self.widgets['_progressBar'] = ttk.Progressbar(
            self.right_frame, 
            # length=320,
            maximum=1,
            value=0,
        )

        self._set_style(0)

        # при растягивании фрейма
        def on_resize(event):
            self.length = event.width  # максимальная длина имени директории
            
            self._update_labels()

        self.bind('<Configure>', on_resize)

        # каждый элемент таскбара при нажатии будет вызывать окно просмотра задачи
        self.bind("<Button-1>", lambda x: self.open_view(task_config=self.task.config))
        for w_name, w in self.widgets.items():
            if not 'bt' in w_name:  # привязка действий ко всем виджетам, кроме кнопок
                w.bind("<Button-1>", lambda x: self.open_view(task_config=self.task.config))

    # обновление лейблов пути и информации на виджете
    def _update_labels(self):
        # вычисляем символьную длинну для лейбла пути, ужимаем путь, присваиваем текст
        lb_path_length = int(self.length // 10)-23
        lb_path_text = shrink_path(self.task.config.get_filepath(), lb_path_length)
        self.widgets['_lbPath'].configure(text=lb_path_text)

        # если есть ошибка, то лейбл информации заполняем текстом этой ошибки
        if self.error:
            self.widgets['_lbData'].config(text=Settings.lang.read(f'bar.error.{self.error}'))
            return            

        # если нет ошибки, то создаём локализованую строку "качество: высокое | частота кадров: 50"
        lb_data_list = []
        
        # собираем информацию про качество
        quality = Settings.lang.read('task.cmbQuality')[self.task.config.get_quality()]
        quality_text = f"{Settings.lang.read('bar.lbQuality')} {quality}"
        lb_data_list.append(quality_text)

        # информацию про фреймрейт
        framerate_text = f"{Settings.lang.read('bar.lbFramerate')} {self.task.config.get_framerate()}"
        lb_data_list.append(framerate_text)

        if self.length > 600:  # и если ширина фрейма больше 600, то и информацию про цвет
            color_text = f"{Settings.lang.read('bar.lbColor')} {self.task.config.get_color()}"
            lb_data_list.append(color_text)

        # присваиваем всё это дело лейблу информации через резделитель ' | '
        self.widgets['_lbData'].configure(text=' | '.join(lb_data_list))

    # упаковка всех виджетов бара
    def _pack_widgets(self):
        self.widgets['_picture'].pack(side=LEFT)
        self.left_frame.pack(side=LEFT)

        self.widgets['_lbPath'].pack(side=TOP, fill=X, expand=True)
        self.widgets['_lbData'].pack(side=TOP, fill=X, expand=True)
        self.mid_frame.pack(side=LEFT, fill=X, expand=True)

        self.widgets['_progressBar'].pack(side=TOP, expand=True, fill=X)
        self.widgets['btCancel'].pack(side=BOTTOM, expand=True, fill=X)
        self.right_frame.pack(side=LEFT)

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
        self.error = error
        self.update_texts()  # обновление текста виджетов

    # обновление линии прогресса
    def update_progress(self, progress: float, base64_img: str = ''):
        self.progress = progress
        try:
            self.widgets['_progressBar'].config(value=self.progress)
        except:  # после удаления виджета вылетает ошибка из-за большой вложенности
            pass  # она ни на что не влияет, поэтому отлавливается и гасится

        if base64_img:  # если передана картинка base64
            try:        # пытается преобразовать её в картинку тк
                image_tk = base64_to_tk(base64_img)  # и заменить на баре
                self.widgets['_picture'].config(image=image_tk)
                self.image_tk = image_tk
            except:
                pass

    # удаление бара
    def delete(self):
        self.destroy()

    # обновление текстов виджетов
    def update_texts(self):
        for w_name, widget in self.widgets.items():
            if not w_name.startswith('_'):
                widget.config(text=Settings.lang.read(f'{self.name}.{w_name}'))
        self._update_labels()


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
    def __init__(self, size: Tuple[int]):
        self.size = size
        self.stock = True
        self.pil_orig: Image = None
        self.pil_sized: Image = None
        self.pil_fit: Image = None
        self.set_empty()

    def set_size(self, size):
        self.size = size

    def open(self, image_link: str):
        try:
            self.pil_orig = Image.open(image_link).convert("RGBA")  # открытие изображения по пути
            self.update_size()
            self.stock = False
        except (FileNotFoundError, AttributeError):  # если файл не найден
            self.set_empty()                         # создаёт пустую картинку

    def set_empty(self):
        self.pil_sized = self.pil_fit = self.pil_orig = Image.new("RGBA", self.size, (0, 0, 0, 0))

    # изменение размера картинки, подгонка под холст
    def update_size(self):

        # изменяем размер изображения, создаём прозрачную картинку
        self.pil_sized = self.pil_orig.copy()
        self.pil_sized.thumbnail(self.size, Image.Resampling.LANCZOS)
        self.pil_fit = Image.new("RGBA", self.size, (0, 0, 0, 0))

        # вставляем изображение в центр пустого изображения
        x_offset = (self.size[0] - self.pil_sized.width) // 2
        y_offset = (self.size[1] - self.pil_sized.height) // 2
        self.pil_fit.paste(self.pil_sized, (x_offset, y_offset))

    # получение изображения нужной прозрачности
    def get_alpha(self, alpha: float):
        if self.pil_fit.size != self.size:
            self.update_size()
        
        alpha_img = self.pil_fit.getchannel('A')
        alpha_img = alpha_img.point(lambda i: i * alpha)
        self.modified = self.pil_fit.copy()
        self.modified.putalpha(alpha_img)
        return self.modified


class ImageUnion:
    """Класс для хранения информации о двух картинках,
    их изменениях, и преобразованиях."""

    def __init__(self, master: Canvas):
        self.master = master
        self.stock = True
        self.size = master.width, master.height
        self.shown: Image = None
        self.transition_stage = 1, 0

        self.new = ImageComposite(self.size)
        self.old = ImageComposite(self.size)

        self.tk = ImageTk.PhotoImage(Image.new("RGBA", self.size, (0, 0, 0, 0)))
        self.id = master.create_image(0, 0, anchor='nw', image=self.tk)
        
        # привязка фокусировки на холст при нажатие на изображение, чтобы снять фокус с полей ввода
        self.master.tag_bind(self.id, "<Button-1>", lambda event: self.master.focus_set())

    def set_new(self, image_link: str):
        self.old, self.new = self.new, self.old
        self.new.open(image_link)

    def update_size(self, size: Tuple[int]):
        if self.size == size:
            return
        self.size = size
        self.old.set_size(self.size)
        self.new.set_size(self.size)
        self.transit_delta(*self.transition_stage)

    def update_tk(self, image: Image):
        tk = ImageTk.PhotoImage(image)
        self.master.itemconfig(self.id, image=tk)
        self.tk = tk

    # меняет прозрачность для одного кадра
    def transit_delta(self, alpha_new: float, alpha_old: float):
        if alpha_new > 1:
            alpha_new = 1
        if alpha_old < 0:
            alpha_old = 0
        self.transition_stage = alpha_new, alpha_old
        try:
            new = self.new.get_alpha(alpha_new)
            old = self.old.get_alpha(alpha_old)
            self.shown = Image.alpha_composite(old, new)
            self.update_tk(self.shown)
        except:
            pass

    # расположение картинки на холсте по центру
    def update_coords(self):
        x = self.master.width//2 - self.width//2
        y = self.master.height//2 - self.height//2
        self.master.coords(self.id, x, y)


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

        self.frames = 30  # кол-во кадров изменения прозрачности 
        self.delay = 0.01  # задержка между кадрами (с) 

        self.init_text = None
        self._create_init_text()    # создание пригласительной надписи
        if not veiw_mode:           # и, если это не режим просмотра,
            self._show_init_text()  # показывает надпись

        self.cleared = True
        self.img = ImageUnion(self)

        self.overlays = OverlaysUnion(self, overlays)

    # обновление изображения
    def transit_image(self):            
        alpha_new, alpha_old = 0, 1
        for i in range(self.frames):
            time.sleep(self.delay)
            if i < self.frames/3:
                alpha_new += (1/self.frames)*1.7
            elif i < self.frames/1.5:
                alpha_new += (1/self.frames)*1.5
                alpha_old -= (1/self.frames)*1.5
            else:
                alpha_old -= (1/self.frames)*1.5
            self.img.transit_delta(alpha_new, alpha_old)

            if i == int(self.frames/2):
                self.overlays.update()
        self.img.transit_delta(1, 0)
        self.overlays.update()

    # установка новой картинки
    def update_image(self, image_link: str):
        self.cleared = False
        self._hide_init_text()
        self.img.set_new(image_link)
        self.transit_image()

    # очистка холста от изображений (внешняя ручка)
    def clear_image(self):
        if self.cleared:
            return
        self._show_init_text()
        self.img.set_new('')
        self.transit_image()

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
        x, y = self.coords(elem_id)                     # координаты элемента на холсте
        try:
            if x < 0 or y < 0:
                raise IndexError                        # если координата меньше нуля

            if self.cleared:                     # если картинка спрятана
                raise Exception
            
            color = self.img.shown.getpixel((x, y))   # цвет пикселя картинки на этих координатах
            r, g, b, a = color[0:4]

            if a < 128:                                 # если пиксель на картинке, но прозрачный
                raise Exception
            
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
            self.img.update_size((width, height))       # то пересчитывает

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
            self.itemconfig(self.init_text, text=Settings.lang.read('task.initText'))


class DirectoryManager(ttk.Frame):
    """Менеджер директорий, поле со списком.
    Даёт возможность добавлять, удалять директории, 
    и менять порядок кнопками и перетаскиванием"""

    def __init__(self, master: Union[Tk, ttk.Frame], veiw_mode: bool, dirs: list, on_change: Callable):
        super().__init__(master)
        self.name = 'dirs'

        self.widgets: Dict[str, Widget] = {}
        self._initial_dir: str = '~'
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

        self.top_frame = ttk.Frame(self)

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

        self.button_frame = ttk.Frame(self)

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
        dir_name = filedialog.askdirectory(parent=self, initialdir=self._initial_dir)
        if not dir_name or dir_name in self.dirs:
            return
        if not find_img_in_dir(dir_name):
            return
        self._initial_dir = os.path.dirname(dir_name)
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
            self.listbox.insert(index, Settings.lang.read('dirs.DirNotExists'))
            self.after(2000, self.listbox.delete, index)
            self._remove_directory()

    def update_texts(self):
        for w_name, widget in self.widgets.items():
            if not w_name.startswith('_'):
                widget.config(text=Settings.lang.read(f'{self.name}.{w_name}'))


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
 
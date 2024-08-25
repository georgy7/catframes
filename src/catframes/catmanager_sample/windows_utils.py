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
            justify=CENTER,
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
        self.widgets['_picture'].pack(side=LEFT)
        self.left_frame.pack(side=LEFT)

        self.widgets['_lbPath'].pack(side=TOP, fill=X, expand=True)
        self.widgets['_lbData'].pack(side=TOP, fill=X, expand=True)
        self.mid_frame.pack(side=LEFT)

        self.widgets['_progressBar'].pack(side=TOP, expand=True)
        self.widgets['btCancel'].pack(side=BOTTOM)
        self.right_frame.pack(side=LEFT, expand=True)

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
    def set_error(self, error: str):
        self._set_style(2)
        self.widgets['btDelete'] = self.widgets.pop('btCancel')  # переименование кнопки
        self.widgets['btDelete'].config(
            command=lambda: self.task.delete(),  # переопределение поведения кнопки
        )
        self.widgets['_lbData'].config(text=Lang.read(f'bar.error.{error}'))
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
    """Класс для хранения информации о картинке,
    её изменения, и преобразования."""

    def __init__(self, master: Canvas) -> None:
        self.master = master
        self.stock = True
        self.hidden = True
        self.id: int = None
        self.orig_pil: Image = None
        self.pil: Image = None
        self.tk: ImageTk = None
        self.height: int = None
        self.width: int = None
        self._create_image()
    
    # создание изображения
    def _create_image(self):
        self.set_empty()  # запись пустой картинки
        x, y = self.master.width//2 - self.height//2, 0
        self.id = self.master.create_image(x, y, anchor=NW, image=self.tk)  # передача изображения
        
        # привязка фокусировки на холст при нажатие на изображение, чтобы снять фокус с полей ввода
        self.master.tag_bind(self.id, "<Button-1>", lambda event: self.master.focus_set())

    # изменение размера картинки, подгонка под холст
    def _update_size(self, current_as_base: bool = False):
        canvas_ratio = self.master.width / self.master.height  # соотношение сторон холста
        ratio = self.orig_pil.size[0] / self.orig_pil.size[1]  # соотношение сторон картинки

        if canvas_ratio > ratio:                                      # если холст по соотносшению шире
            size = int(self.master.height*ratio), self.master.height    # упор по высоте
        else:                                                         # а если холст по соотношению выше
            size = self.master.width, int(self.master.width/ratio)      # то упор по высоте

        if (self.width, self.height) == size:  # если размеры не поменялись
            return

        try:
            self.pil = self.orig_pil.resize(size, Image.LANCZOS)  # масштабирование
            self.tk = ImageTk.PhotoImage(self.pil)                # загрузка новой тк-картинки
            self.width, self.height = size                        # сохранение новых размеров

            if current_as_base:           # установка текущего размера картинки
                self.orig_pil = self.pil  # как базового (для оптимизации)
        except Exception:  # если PIL сломается внутри из-за сложного и частого вызова
            pass

    # приобразование ссылки на картинку, наполнение объекта композита
    def open_image(self, image_link: str):
        try:
            self.orig_pil = Image.open(image_link)   # открытие изображения по пути
            self._update_size(current_as_base=True)  # установка размеров картинки базовыми
            self.stock = False
        except (FileNotFoundError, AttributeError):  # если файл не найден
            self.set_empty()                         # создаёт пустую картинку

    # расположение картинки на холсте по центру
    def update_coords(self):
        x = self.master.width//2 - self.width//2
        y = self.master.height//2 - self.height//2
        self.master.coords(self.id, x, y)

    # создание пустого изображения, и надписи "добавьте картинки"
    def set_empty(self):
        self.height, self.width = self.master.height, self.master.width
        self.orig_pil = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))  # пустое изображение
        self.pil = self.orig_pil                           # текущий объект pil будет таким же
        self.tk = ImageTk.PhotoImage(self.orig_pil)        # создаём объект тк
        self.stock = True                                  # установка флага стокового изображения

    # изменение прозрачности картинки
    def change_alpha(self, alpha):
        faded_current_image = self.pil.copy()              # копируем картинку 
        faded_current_image.putalpha(int(alpha * 255))     # применяем альфа-канал 
        self.tk = ImageTk.PhotoImage(faded_current_image)  # создаём тк картинку, сохраняем
        self.master.itemconfig(self.id, image=self.tk)     # обновляем изображения на холсте 

    # перезагрузка картинки на холсте
    def reload(self):
        self._update_size()                                # обновление размера
        self.master.itemconfig(self.id, image=self.tk)     # замена тк-картинки на холсте


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

        self.init_text = None
        self._create_init_text()    # создание пригласительной надписи
        if not veiw_mode:           # и, если это не режим просмотра,
            self._show_init_text()  # показывает надпись

        self.cleared = True
        self.new_img = ImageComposite(self)   # изображения, которые будут
        self.old_img = ImageComposite(self)   # менять прозрачность по очереди

        self.alpha_step = 0.1  # Шаг изменения прозрачности 
        self.delay = 20  # Задержка между кадрами (мс) 

        self.overlays = OverlaysUnion(self, overlays)

    # анимируем смену изображений (рекурсивный метод)
    def _animate_transition(self, alpha: float = 1): 
        if alpha <= 0:                   # если альфа-канал дошёл до нуля
            self.old_img.hidden = True   # расставляем флаги прозрачности
            self.new_img.hidden = False
            self.overlays.update()       # обновляем оверлеи
            self._hide_init_text()       # только в конце прячем текст
            return
        
        if not self.old_img.stock:       # если изображение не стоковое
            self.old_img.change_alpha(alpha)  # делаем его прозрачнее
        self.new_img.change_alpha(1-alpha)    # а новое - наоборот

        # вызываем этот же метод, но уменьшая альфа-канал
        self.master.after(self.delay, self._animate_transition, alpha-self.alpha_step)
            
    # плавное исчезновение картинки (рекурсивный метод)
    def _animate_fadeoff(self, alpha: float = 1):
        if alpha <= 0:                   # если альфа-канал дошёл до нуля
            self.old_img.hidden = True   # ставим флаг прозрачности
            self.overlays.update()       # обновляем оверлеи
            return
        
        if not self.old_img.stock:
            self.old_img.change_alpha(alpha)  # делаем картинку прозрачнее
        self.master.after(self.delay, self._animate_fadeoff, alpha-self.alpha_step)  # рекурсия
        
    # обновление изображения (внешняя ручка)
    def update_image(self, image_link: str):
        self.cleared = False
        self.old_img, self.new_img = self.new_img, self.old_img  # меняем картинки местами
        self.new_img.open_image(image_link)     # открываем картинку
        self.new_img.update_coords()            # устанавливаем её координаты
        self._animate_transition()              # анимируем замену старой

    # очистка холста от изображений (внешняя ручка)
    def clear_image(self):
        if self.cleared:
            return
        self.cleared = True
        self.old_img, self.new_img = self.new_img, self.old_img  # меняем картинки местами
        self._show_init_text()                  # сначала показ пригласительного текста
        self._animate_fadeoff()                 # анимируем исчезновение
        self.new_img.set_empty()                # устанавливаем стоковую картинку
        self.new_img.update_coords()            # позиционируем её

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
        x_shift, y_shift = self.coords(self.new_img.id) # сдвиг картинки от левого края холста
        x, y = self.coords(elem_id)                     # координаты элемента на холсте
        try:
            x -= int(x_shift)                       # поправка, теперь это коорд. элемента на картинке
            y -= int(y_shift)
            if x < 0 or y < 0:
                raise IndexError                        # если координата меньше нуля

            if self.new_img.hidden:                     # если картинка спрятана
                raise Exception
            
            color = self.new_img.pil.getpixel((x, y))   # цвет пикселя картинки на этих координатах
            r, g, b = color[0:3]
        except TypeError:                               # если pillow вернёт не ргб, а яркость пикселя
            return color < 128
        except Exception:                               # если пиксель за пределами картинки
            r, g, b = self.winfo_rgb(self.color)        # задний план будет оцениваться, исходя из
            r, g, b = r/255, g/255, b/255               # выбранного фона холста
        
        brightness = (r*299 + g*587 + b*114) / 1000     # вычисление яркости пикселя по весам
        return brightness < 128                         # сравнение яркости

    # обновляет разрешение холста
    def update_resolution(self, width: int, height: int, resize_image: bool):

        self.width, self.height = width, height
        self.config(height=height, width=width)             # установка новых размеров
        self.overlays.update()                              # обновляет оверлеи
        self.coords(self.init_text, self.width/2, self.height/2)  # позиция прив. текста

        if resize_image:                # если нужен пересчёт картинки
            self.new_img.reload()       # то пересчитывает
        self.new_img.update_coords()    # обновляет координаты картинки

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
        self.update_texts()

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
        self.listbox = Listbox(self.top_frame, selectmode=SINGLE, width=20, height=8)
        self.scrollbar = ttk.Scrollbar(self.top_frame, orient="vertical", command=self.listbox.yview)
        self.listbox.config(yscrollcommand=self.scrollbar.set)

        if not self.veiw_mode:
            self.listbox.bind('<Button-1>', self._start_drag)
            self.listbox.bind('<B1-Motion>', self._do_drag)
        self.listbox.bind('<Double-Button-1>', self._on_double_click)

        self.button_frame = Frame(self)

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
        dir_name = filedialog.askdirectory(parent=self)
        if not dir_name or dir_name in self.dirs:
            return
        if not find_img_in_dir(dir_name):
            return
        self.listbox.insert(END, shrink_path(dir_name, 25))
        self.dirs.append(dir_name)  # добавление в список директорий

    # удаление выбранной директории из списка
    def _remove_directory(self):
        selected = self.listbox.curselection()
        if selected:
            index = selected[0]
            self.listbox.delete(index)
            del self.dirs[index]

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
            self._swap_dirs(self.drag_data["start_index"], new_index, self.drag_data["item"])
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
            self.listbox.insert(index, Lang.read('dirs.DirNotExists'))
            self.after(2000, self.listbox.delete, index)
            self._remove_directory()

    def update_texts(self):
        for w_name, widget in self.widgets.items():
            if not w_name.startswith('_'):
                widget.config(text=Lang.read(f'{self.name}.{w_name}'))


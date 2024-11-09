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
    img_list = [f for f in os.listdir(dir) if f.endswith((".png", ".jpg"))]
    if full_path:
        img_list = list(
            map(lambda x: f"{dir}/{x}", img_list)
        )  # добавляет путь к названию
    return img_list


# переводчит base64 картинку в tk
def base64_to_tk(image_base64: str) -> ImageTk.PhotoImage:
    image_data = base64.b64decode(image_base64)
    image = Image.open(io.BytesIO(image_data))
    return ImageTk.PhotoImage(image)


# сокращает строку пути, расставляя многоточия внутри
def shrink_path(path: str, limit: int) -> str:
    if len(path) < limit:
        return path

    # вычисление разделителя, добавление вначало, если нужно
    s = "/" if "/" in path else "\\"
    dirs = path.split(s)
    if path.startswith(s):
        dirs.pop(0)
        dirs[0] = s + dirs[0]

    # список укороченного пути, первый и последний элементы
    shrink = [dirs.pop(0), dirs.pop()]
    while dirs and len(s.join(shrink) + dirs[-1]) + 4 < limit:
        shrink.insert(1, dirs.pop())  # добавить элемент с конца

    try:
        # вычисляет разницу символов от нужной длины,
        # добавит кусочек имени последней невлезшей директории
        addit = limit - len(f"{shrink[0]}{s}...{s}{s.join(shrink[1:])}")
        start = len(dirs[-1]) - addit
        shrink.insert(1, dirs[-1][start::])
    except:
        pass

    # сборка строки нового пути, передача её, если она короче изначальной
    new_path = f"{shrink[0]}{s}...{s.join(shrink[1:])}"
    return new_path if len(new_path) < len(path) else path


class GlobalStates:
    last_dir = "~"


class ScrollableFrame(ttk.Frame):
    """Прокручиваемый (умный) фрейм"""

    def __init__(self, root_window: Tk, *args, **kwargs):
        super().__init__(root_window, *args, **kwargs, style="Main.TFrame")

        self.root: Tk = root_window
        self.canvas = Canvas(self, highlightthickness=0)

        # если это не macos, добавить холсту цвет
        if not platform.system() == "Darwin":
            self.canvas.config(bg=MAIN_TASKLIST_COLOR)

        # привязываем обработку изменений холста
        self.canvas.bind("<Configure>", self._on_resize_window)

        self.scrollbar = ttk.Scrollbar(
            self,
            orient="vertical",
            command=self.canvas.yview,
        )
        self.scrollable_frame = ttk.Frame(  # фрейм для контента (внутренних виджетов)
            self.canvas, padding=[15, 0], style="Main.TaskList.TFrame"
        )

        # привязка обработки изменений фрейма
        self.scrollable_frame.bind("<Configure>", self._on_frame_update)

        # привязка холста к верхнему левому углу, получение id фрейма
        self.frame_id = self.canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw"
        )
        # передача управления полосы прокрутки, когда холст движется от колёсика
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # упаковка виджетов
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        # привязка и отвязка событий, когда курсор заходит на холст
        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)

        # первичное обновление полосы, чтобы сразу её не было видно
        self._update_scrollbar_visibility()

    # отрабатываывает при добавлении/удалении таскбаров в фрейм
    def _on_frame_update(self, event):
        self._update_scrollbar(event)

    # изменение размеров фрейма внутри холста
    def _on_resize_window(self, event):
        if event.width > 500:  # фильтруем нужные события
            self.canvas.itemconfig(self.frame_id, width=event.width)

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
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


class TaskBar(ttk.Frame):
    """Класс баров задач в основном окне"""

    def __init__(self, master: ttk.Frame, task: Task, cancel_def: Callable, **kwargs):
        super().__init__(master, borderwidth=1, padding=5, style="Scroll.Task.TFrame")
        self.name = "bar"
        self.widgets: Dict[str, Widget] = {}
        self.task: Task = task
        self.cancel_def = cancel_def
        self.progress: float = 0
        self.image: Image
        self.length: int = 520
        self.error: str = None

        # достаёт ручку для открытия окна просмотра
        self.open_view: Callable = kwargs.get("view")

        self._init_widgets()
        self.update_texts()
        self._pack_widgets()
        self._update_labels()

    # установка стиля для прогрессбара
    def _set_style(self, style_id: int):
        styles = ["Running", "Success", "Error"]
        style = styles[style_id]

        for elem in (self, self.left_frame, self.mid_frame, self.right_frame):
            elem.config(style=f"{style}.Task.TFrame")
        self.widgets["_lbData"].config(style=f"{style}.Task.TLabel")
        self.widgets["_lbPath"].config(style=f"{style}.Task.TLabel")
        self.widgets["_progressBar"].config(
            style=f"{style}.Task.Horizontal.TProgressbar"
        )

    # создание и настройка виджетов
    def _init_widgets(self):
        self.left_frame = ttk.Frame(self, padding=5)

        # берёт первую картинку из первой директории
        img_dir = self.task.config.get_dirs()[0]
        img_path = find_img_in_dir(img_dir, full_path=True)[0]

        image = Image.open(img_path)
        image_size = (80, 60)
        image = image.resize(image_size, Image.ADAPTIVE)
        self.image_tk = ImageTk.PhotoImage(image)

        self.widgets["_picture"] = ttk.Label(self.left_frame, image=self.image_tk)

        # создании средней части бара
        self.mid_frame = ttk.Frame(self, padding=5)

        bigger_font = font.Font(size=16)

        # надпись в баре
        self.widgets["_lbPath"] = ttk.Label(
            self.mid_frame,
            font=bigger_font,
            padding=5,
            text=shrink_path(self.task.config.get_filepath(), 30),
        )

        self.widgets["_lbData"] = ttk.Label(
            self.mid_frame,
            font="14",
            padding=5,
        )

        # создание правой части бара
        self.right_frame = ttk.Frame(self, padding=5)

        # кнопка "отмена"
        self.widgets["btCancel"] = ttk.Button(
            self.right_frame, width=10, command=self.cancel_def
        )

        # полоса прогресса
        self.widgets["_progressBar"] = ttk.Progressbar(
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

        self.bind("<Configure>", on_resize)

        # открытие окна просмотра задачи
        def open_view(event):
            self.open_view(task_config=self.task.config)

        # привязка ко всем элементам таскбара, кроме кнопок
        self.bind("<Button-1>", open_view)
        for w_name, w in self.widgets.items():
            if not "bt" in w_name:  #
                w.bind("<Button-1>", open_view)

    # обновление лейблов пути и информации на виджете
    def _update_labels(self):

        # вычисляем символьную длинну для лейбла пути,
        # ужимаем путь, присваиваем текст
        lb_path_length = int(self.length // 10) - 23
        lb_path_text = shrink_path(self.task.config.get_filepath(), lb_path_length)
        self.widgets["_lbPath"].configure(text=lb_path_text)

        # если есть ошибка, то лейбл информации заполняем текстом этой ошибки
        if self.error:
            text = Settings.lang.read(f"bar.error.{self.error}")
            self.widgets["_lbData"].configure(text=text)
            return

        # создаём локализованую строку "качество: высокое | частота кадров: 50"
        lb_data_list = []

        quality = Settings.lang.read("task.cmbQuality")[self.task.config.get_quality()]
        quality_text = f"{Settings.lang.read('bar.lbQuality')} {quality}"
        lb_data_list.append(quality_text)

        framerate_text = f"{Settings.lang.read('bar.lbFramerate')} {self.task.config.get_framerate()}"
        lb_data_list.append(framerate_text)

        # и если ширина фрейма больше 600, то и информацию про цвет
        if self.length > 600:
            color_text = (
                f"{Settings.lang.read('bar.lbColor')} {self.task.config.get_color()}"
            )
            lb_data_list.append(color_text)

        # присваиваем строку информации через резделитель ' | '
        self.widgets["_lbData"].configure(text=" | ".join(lb_data_list))

    # упаковка всех виджетов бара
    def _pack_widgets(self):
        self.widgets["_picture"].pack(side=LEFT)
        self.left_frame.pack(side=LEFT)

        self.widgets["_lbPath"].pack(side=TOP, fill=X, expand=True)
        self.widgets["_lbData"].pack(side=TOP, fill=X, expand=True)
        self.mid_frame.pack(side=LEFT, fill=X, expand=True)

        self.widgets["_progressBar"].pack(side=TOP, expand=True, fill=X)
        self.widgets["btCancel"].pack(side=BOTTOM, expand=True, fill=X)
        self.right_frame.pack(side=LEFT)

        self.pack(pady=[10, 0], fill=X, expand=True)

    # изменение бара на "завершённое" состояние
    def finish(self):
        # в словаре виджетов ключ кнопки переименовывается,
        # и меняется поведение кнопки переопределяется

        self._set_style(1)
        self.widgets["btDelete"] = self.widgets.pop("btCancel")
        self.widgets["btDelete"].config(command=lambda: self.task.delete())
        self.update_texts()

    # изменение бара на состояние "ошибки"
    def set_error(self, error: str):

        self._set_style(2)
        self.widgets["btDelete"] = self.widgets.pop("btCancel")
        self.widgets["btDelete"].config(command=lambda: self.task.delete())
        self.error = error
        self.update_texts()

    # обновление линии прогресса
    def update_progress(self, progress: float, base64_img: str = ""):
        self.progress = progress
        try:
            self.widgets["_progressBar"].config(value=self.progress)
        except:
            pass

        if base64_img:
            try:
                image_tk = base64_to_tk(base64_img)  # и заменить на баре
                self.widgets["_picture"].config(image=image_tk)
                self.image_tk = image_tk
            except:
                pass

    # удаление бара
    def delete(self):
        self.destroy()

    # обновление текстов виджетов
    def update_texts(self):
        for w_name, widget in self.widgets.items():
            if not w_name.startswith("_"):
                widget.config(text=Settings.lang.read(f"{self.name}.{w_name}"))
        self._update_labels()


class ResizingField(Text):
    """Поле, переводящее курсор по нажатию Enter,
    и изменяющее свой размер по количеству строк"""

    def __init__(self, master: Canvas, horizontal_pos: str, vertical_pos: str):
        super().__init__(
            master,
            width=10,
            font=("Arial", 14),
            wrap=NONE,
            undo=True,
            highlightthickness=2,
        )
        self.default_width: int = 10
        self.extra_width: int = 0
        self.num_lines: int = 0

        self.vertical_pos: str = vertical_pos
        self.horizontal_pos: str = horizontal_pos

        # смещения от начальных координат
        self.vertical_shift: int = 0
        self.horisontal_shift: int = 0

        self.id_on_canvas: Optional[int] = None
        self.default_coords: Optional[list] = None

        self.bind("<Escape>", self._on_escape)
        self.bind("<<Modified>>", self._on_text_change)

        # начальная высота 1 строка и перенос по словам
        self.configure(height=1, wrap="word")

    # получение всего текста в поле
    def get_text(self) -> str:
        try:
            return self.get("1.0", "end-1c").strip("\n ")
        except:
            return ""

    # установка текста в поле
    def set_text(self, text):
        self.delete("1.0", END)
        self.insert(END, text)

    # получение id себя на холсте
    def bind_self_id(self, id):
        self.id_on_canvas = id
        x, y = self.master.coords(id)
        self.default_coords = x, y - self.vertical_shift
        self._update_height()

    # фокусировка на объект холста, чтобы убрать это поле ввода
    def _on_escape(self, event):
        self.master.focus_set()

    def _on_text_change(self, event):
        self._update_width()
        self._update_height()
        self._update_coords()
        self.master.overlays.update()

        # сбрасываем статус изменения текста,
        # чтобы событие могло срабатывать повторно
        self.edit_modified(False)

    # обновление ширины, исходя из самой длинной строки
    def _update_width(self):
        lines = self.get_text().split("\n")
        longest = len(max(lines, key=lambda i: len(i)))

        self.extra_width = 0
        if longest >= self.default_width:
            self.extra_width = longest + 2 - self.default_width

        # рассчитывает модуль горизонтального смещения,
        # и устанавливает смещение в нужную сторону
        y_shift_abs = self.extra_width * 5
        if self.horizontal_pos == RIGHT:
            self.horisontal_shift = -y_shift_abs
        if self.horizontal_pos == LEFT:
            self.horisontal_shift = y_shift_abs

    # обновление высоты, исходя из количества строк
    def _update_height(self):
        self.num_lines = int(self.index("end-1c").split(".")[0])

        # рассчитывает модуль вертикального смещения,
        # и устанавливает смещение в нужную сторону
        x_shift_abs = (self.num_lines - 1) * 11
        if self.vertical_pos == BOTTOM:
            self.vertical_shift = -x_shift_abs
        if self.vertical_pos == TOP:
            self.vertical_shift = x_shift_abs

    # движение по вертикали при изменении количества строк
    def _update_coords(self):
        # если поле ввода ещё не размещено
        if not self.default_coords:
            return

        self.master.coords(
            self.id_on_canvas,
            self.default_coords[0] + self.horisontal_shift,
            self.default_coords[1] + self.vertical_shift,
        )
        self.config(width=self.default_width + self.extra_width, height=self.num_lines)


class Overlay:
    """Единичный оверлей на холсте, как сущность из
    прозрачного квадрата, лейбла, и поля ввода."""

    def __init__(
        self, master: Canvas, text: str, horizontal_pos: str, vertical_pos: str
    ):

        self.master = master
        self.view_mode: bool = master.view_mode
        self.horizontal_pos: str = horizontal_pos

        self.empty: bool = bool(text)

        # настройи прозрачного квадрата
        self.sq_size: int = 20
        sq_color = "#ffffff"
        sq_alpha = 0 if self.view_mode else 0.5

        # создание и добавление прозрачного квадрата
        self.alpha_square: PhotoImage = self._create_alpha_square(
            self.sq_size, sq_color, sq_alpha
        )
        self.square_id: int = self.master.create_image(
            0, 0, image=self.alpha_square, anchor="nw"
        )

        # добавление текста
        self.label_id: int = self.master.create_text(
            0, 0, text=text, font=("Arial", 24), justify=horizontal_pos
        )
        self.vertical_shift: int = 0
        self.horizontal_shift: int = 0

        # инициализация поля ввода
        self.entry: ResizingField = ResizingField(
            self.master, horizontal_pos, vertical_pos
        )
        self.entry_id: int = self.master.create_window(
            0, 0, window=self.entry, state="hidden", anchor=CENTER
        )
        self.entry.bind_self_id(self.entry_id)
        self.entry.set_text(text)

        # привязка события скрытия и показа поля ввода
        if not self.view_mode:
            self.master.tag_bind(self.label_id, "<Button-1>", self._show_entry)
            self.entry.bind("<FocusOut>", self._hide_entry)

    # обновление смещений текста
    def _update_shifts(self):
        self.vertical_shift = self.entry.vertical_shift

        # центральным полям смещение не нужно
        if self.horizontal_pos == CENTER:
            self.horizontal_shift = 0
            return

        # узнаём ширину лейбла на холсте
        bbox = self.master.bbox(self.label_id)
        text_object_width = bbox[2] - bbox[0]

        # при наличии текста, вычисляем смещение
        if self.entry.get_text():
            shift_abs = text_object_width // 2
            shift_abs -= self.sq_size / 2
            shift_abs -= self.master.width // 20
        else:
            shift_abs = 0

        # устанавливает смещение в нужную сторону
        if self.horizontal_pos == RIGHT:
            self.horizontal_shift = shift_abs
        if self.horizontal_pos == LEFT:
            self.horizontal_shift = -shift_abs

    # обновляет текст лейбла и видимость квадрата
    def update_label(self):
        text = "+"  # дефолтные значения, когда поле ввода пустое
        font = ("Arial", 24)
        square_state = "normal"
        label_color = "black"

        # при наличии текста в поле ввода, разместит его в лейбле,
        # проверит цвет фона, и выберет контрастный цвет, скроет квадрат
        if self.entry.get_text() or self.view_mode:
            text = self.entry.get_text()
            font = ("Arial", 16)
            square_state = "hidden"

            dark_background = self.master.is_dark_background(self.label_id)
            label_color = "white" if dark_background else "black"

        try:
            self.master.itemconfig(
                self.label_id, text=text, font=font, fill=label_color
            )
            self.master.itemconfig(self.square_id, state=square_state)
        except TclError:
            pass

    def get_text(self) -> str:
        return self.entry.get_text()

    # установка кординат для квадрата и лейбла
    def set_coords(self, coords: Tuple[int]):
        self._update_shifts()
        self.master.coords(
            self.square_id, coords[0] - self.sq_size / 2, coords[1] - self.sq_size / 2
        )
        self.master.coords(
            self.label_id,
            coords[0] - self.horizontal_shift,
            coords[1] + self.vertical_shift,
        )

    # создаёт картинку прозрачного квадрата
    def _create_alpha_square(self, size: int, fill: str, alpha: float):
        alpha = int(alpha * 255)
        fill = self.master.winfo_rgb(fill) + (alpha,)
        image = Image.new("RGBA", (size, size), fill)
        return ImageTk.PhotoImage(image)

    # отображает поле ввода
    def _show_entry(self, event):
        label_coords = self.master.coords(self.label_id)
        self.master.coords(self.entry_id, *label_coords)
        self.entry.bind_self_id(self.entry_id)
        self.master.itemconfig(self.entry_id, state="normal")  # скрывает поле ввода
        self.entry.focus_set()

    # прячет поле ввода, меняет текст в лейбле
    def _hide_entry(self, event):

        # стрипает текст в поле ввода
        text = self.entry.get_text()
        self.entry.set_text(text)

        self.master.itemconfig(self.entry_id, state="hidden")
        self.update_label()


class OverlaysUnion:
    """Группа из восьми оверлеев, расположенных на холсте.
    Этот класс занимается их инициализацией и агрегацией."""

    def __init__(self, master: Canvas, default_texts: Optional[List[str]]):
        self.master: Canvas = master
        self.view_mode: bool = master.view_mode
        self.default_texts: Optional[List] = default_texts

        self.overlays: list = []

        self._create_entries()
        self.update()

    # инициализация полей ввода
    def _create_entries(self):

        # выравнивания виджетов, относительно расположения
        c, l, r, t, b = CENTER, LEFT, RIGHT, TOP, BOTTOM
        horizontal_pos = (l, c, r, r, r, c, l, l)  # 8 позиций горизонтали
        vertical_pos = (t, t, t, c, b, b, b, c)  # 8 позиций вертикали

        # создание каждого оверлея
        for i in range(8):
            text = self.default_texts[i] if self.view_mode else ""
            overlay = Overlay(self.master, text, horizontal_pos[i], vertical_pos[i])
            self.overlays.append(overlay)

    # позиционирует и привязывает обработчики позиций
    def update(self):
        x_pad = int(self.master.width / 8)
        y_pad = int(self.master.height / 8)

        # расположение восьми позиций оверлеев
        # с верхнего левого по часовой стрелке
        positions = [
            (x_pad, y_pad),
            (self.master.width // 2, y_pad),
            (self.master.width - x_pad, y_pad),
            (self.master.width - x_pad, self.master.height // 2),
            (self.master.width - x_pad, self.master.height - y_pad),
            (self.master.width // 2, self.master.height - y_pad),
            (x_pad, self.master.height - y_pad),
            (x_pad, self.master.height // 2),
        ]

        try:  # позиционирует каждый виджет и обновляет текст
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
    """Класс для хранения картинки в разных видах, и состояниях"""

    def __init__(self, size: Tuple[int]):
        self.size: tuple = size
        self.stock: bool = True
        self.pil_orig: Image = None
        self.pil_sized: Image = None
        self.pil_fit: Image = None
        self.set_empty()

    def set_size(self, size):
        self.size = size

    # откроет картинку, либо создаст пустую
    def open(self, image_link: str):
        try:
            self.pil_orig = Image.open(image_link).convert("RGBA")
            self.update_size()
            self.stock = False
        except (FileNotFoundError, AttributeError):
            self.set_empty()

    def set_empty(self):
        self.pil_sized = self.pil_fit = self.pil_orig = Image.new(
            "RGBA", self.size, (0, 0, 0, 0)
        )

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

        alpha_img = self.pil_fit.getchannel("A")
        alpha_img = alpha_img.point(lambda i: i * alpha)
        self.modified = self.pil_fit.copy()
        self.modified.putalpha(alpha_img)
        return self.modified


class ImageUnion:
    """Класс для хранения информации о двух картинках,
    их изменениях, и преобразованиях."""

    def __init__(self, master: Canvas):
        self.master: Canvas = master
        self.stock: bool = True
        self.size: tuple = master.width, master.height
        self.shown: Image = None
        self.transition_stage: tuple = 1, 0

        self.new = ImageComposite(self.size)
        self.old = ImageComposite(self.size)

        self.tk: ImageTk.PhotoImage = ImageTk.PhotoImage(
            Image.new("RGBA", self.size, (0, 0, 0, 0))
        )
        self.id: int = master.create_image(0, 0, anchor="nw", image=self.tk)

        # привязка фокусировки на холст при нажатие на изображение,
        # чтобы снять фокус с полей ввода
        self.master.tag_bind(
            self.id, "<Button-1>", lambda event: self.master.focus_set()
        )

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
        x = self.master.width // 2 - self.width // 2
        y = self.master.height // 2 - self.height // 2
        self.master.coords(self.id, x, y)


# проверка, тёмный цвет, или светлый
def is_dark_color(r: int, g: int, b: int) -> bool:

    # если палитра 16 бит, конвертирует в 8 бит
    if r > 256 or g > 256 or b > 256:
        r, g, b = r // 256, g // 256, b // 256

    # вычисление яркости пикселя по весам
    brightness = (r * 299 + g * 587 + b * 114) / 1000
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
        background: str = DEFAULT_CANVAS_COLOR,
    ):

        self.default_width = self.width = 800
        self.default_height = self.height = 400

        # создаёт объект холста
        super().__init__(
            master,
            width=self.width,
            height=self.height,
            highlightthickness=0,
            background=background,
        )
        self.pack()

        self.view_mode: bool = veiw_mode
        self.color: str = background

        # настройка плавности смены картинок
        self.frames: int = 30
        self.delay: float = 0.01

        self.init_text_id: Optional[int] = None
        self._create_init_text()
        if not veiw_mode:
            self._show_init_text()

        self.cleared: bool = True
        self.img: ImageUnion = ImageUnion(self)

        self.overlays = OverlaysUnion(self, overlays)

    # обновление изображения
    def transit_image(self):
        alpha_new, alpha_old = 0, 1
        for i in range(self.frames):
            time.sleep(self.delay)
            if i < self.frames / 3:
                alpha_new += (1 / self.frames) * 1.7
            elif i < self.frames / 1.5:
                alpha_new += (1 / self.frames) * 1.5
                alpha_old -= (1 / self.frames) * 1.5
            else:
                alpha_old -= (1 / self.frames) * 1.5
            self.img.transit_delta(alpha_new, alpha_old)

            if i == int(self.frames / 2):
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
        self.img.set_new("")
        self.transit_image()

    # создание объекта пригласительного текста
    def _create_init_text(self):
        self.init_text_id = self.create_text(
            self.width / 2,
            self.height / 2,
            font=("Arial", 24),
            justify=CENTER,
            state="hidden",
            fill="#cccccc",
        )
        self.update_texts()

    # показывает пригласительный текст
    def _show_init_text(self):
        self.itemconfig(self.init_text_id, state="normal")

    # прячет пригласительный текст
    def _hide_init_text(self):
        self.itemconfig(self.init_text_id, state="hidden")

    # проверка, тёмный ли фон на картинке за элементом канваса
    def is_dark_background(self, elem_id: int) -> bool:
        x, y = self.coords(elem_id)
        try:
            if x < 0 or y < 0:
                raise IndexError

            if self.cleared:
                raise Exception

            # цвет пикселя картинки на этих координатах
            color = self.img.shown.getpixel((x, y))
            r, g, b, a = color[0:4]

            # если пиксель на картинке, но прозрачный
            if a < 128:
                raise Exception

        # если pillow вернёт не ргб, а яркость пикселя
        except TypeError:
            return color < 128

        # если пиксель за пределами картинки, оценивается фон холста
        except Exception:
            r, g, b = self.winfo_rgb(self.color)

        return is_dark_color(r, g, b)

    # обновляет разрешение холста
    def update_resolution(self, width: int, height: int, resize_image: bool):

        self.width, self.height = width, height
        self.config(height=height, width=width)
        self.overlays.update()
        self.coords(self.init_text_id, self.width / 2, self.height / 2)

        if resize_image:
            self.img.update_size((width, height))

    # формирует список из восьми строк, введённых в полях
    def fetch_entries_text(self) -> list:
        return self.overlays.get_text()

    # обновляет цвета отступов холста
    def update_background_color(self, color: str):
        self.color = color
        self.config(background=color)
        self.overlays.update()

    def update_texts(self):
        if self.init_text_id:
            self.itemconfig(self.init_text_id, text=Settings.lang.read("task.initText"))


class DirectoryManager(ttk.Frame):
    """Менеджер директорий, поле со списком.
    Даёт возможность добавлять, удалять директории,
    и менять порядок кнопками и перетаскиванием"""

    def __init__(
        self,
        master: Union[Tk, ttk.Frame],
        veiw_mode: bool,
        dirs: list,
        on_change: Callable,
    ):
        super().__init__(master)
        self.name: str = "dirs"

        self.widgets: Dict[str, Widget] = {}
        self.drag_data: dict = {"start_index": None, "item": None}
        self.on_change: Callable = on_change

        self.veiw_mode: bool = veiw_mode
        self._init_widgets()
        self._pack_widgets()
        self.update_texts()

        self.dirs: list = dirs
        self._update_listbox(max_length=30)

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

    def _init_widgets(self):

        self.top_frame = ttk.Frame(self)

        self.widgets["lbDirList"] = ttk.Label(self.top_frame)

        # при растягивании фрейма
        def on_resize(event):
            max_length = int(event.width // 8)
            self._update_listbox(max_length)

        # создание списка и полосы прокрутки
        self.listbox = Listbox(self.top_frame, selectmode=SINGLE, width=20, height=8)
        self.scrollbar = ttk.Scrollbar(
            self.top_frame, orient="vertical", command=self.listbox.yview
        )
        self.listbox.config(yscrollcommand=self.scrollbar.set)

        # в режиме просмотра не будет возможности
        # изменение порядка элементов в списке,
        # поэтому, привязка нажатия не произойдёт
        if not self.veiw_mode:
            self.listbox.bind("<Button-1>", self._start_drag)
            self.listbox.bind("<B1-Motion>", self._do_drag)

        self.top_frame.bind("<Configure>", on_resize)
        self.listbox.bind("<Double-Button-1>", self._on_double_click)

        self.button_frame = ttk.Frame(self)

        self.widgets["btAddDir"] = ttk.Button(
            self.button_frame, width=8, command=self._add_directory
        )
        self.widgets["btRemDir"] = ttk.Button(
            self.button_frame, width=8, command=self._remove_directory
        )

    def _pack_widgets(self):
        self.top_frame.pack(side=TOP, fill=BOTH, expand=True)
        self.widgets["lbDirList"].pack(side=TOP, anchor="w")
        self.listbox.pack(side=LEFT, fill=BOTH, expand=True)
        self.scrollbar.pack(side=LEFT, fill=Y)

        self.button_frame.pack(side=TOP, anchor="w", padx=(0, 15), pady=10, fill=X)

        if not self.veiw_mode:
            self.widgets["btAddDir"].pack(side=LEFT, anchor="e", padx=5, expand=True)
            self.widgets["btRemDir"].pack(side=RIGHT, anchor="w", padx=5, expand=True)

    # добавление директории
    def _add_directory(self):
        dir_name = filedialog.askdirectory(parent=self, initialdir=GlobalStates.last_dir)
        if not dir_name:
            return
        if not find_img_in_dir(dir_name):
            return
        GlobalStates.last_dir = os.path.dirname(dir_name)
        self.listbox.insert(END, shrink_path(dir_name, 25))
        self.dirs.append(dir_name)
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

    # меняет местами две директории в списке
    def _swap_dirs(self, index_old: int, index_new: int, text: str = None):
        if not text:
            text = self.listbox.get(index_old)

        self.listbox.delete(index_old)
        self.listbox.insert(index_new, text)

        self.dirs[index_old], self.dirs[index_new] = (
            self.dirs[index_new],
            self.dirs[index_old],
        )
        self.listbox.select_set(index_new)

    # процесс перетаскивания элемента
    def _do_drag(self, event):
        new_index = self.listbox.nearest(event.y)
        if new_index != self.drag_data["start_index"]:
            self._swap_dirs(
                self.drag_data["start_index"], new_index, self.drag_data["item"]
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
            if platform.system() == "Windows":
                os.startfile(dir_to_open)
            elif platform.system() == "Linux":
                os.system(f"xdg-open {dir_to_open}")
            else:
                os.system(f"open -- {dir_to_open}")
        except:
            self.listbox.delete(index)
            self.listbox.insert(index, Settings.lang.read("dirs.DirNotExists"))
            self.after(2000, self.listbox.delete, index)
            self._remove_directory()

    def update_texts(self):
        for w_name, widget in self.widgets.items():
            if not w_name.startswith("_"):
                widget.config(text=Settings.lang.read(f"{self.name}.{w_name}"))


class ToolTip:
    """Подсказка при наведении на виджет.
    Лейбл с текстом поверх всего,
    коорый появляется при наведении,
    и исчизает при уходе курсора"""

    def __init__(self, widget: Widget, get_text: Callable):
        self.tip_window: Optional[Toplevel] = None

        # функция, по которой получим текст подсказки,
        # и виджет, к которому привязывается подсказка
        self.get_text: Callable = get_text
        self.widget: Widget = widget
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    # показать "подсказку"
    def show_tip(self, event=None):
        text = self.get_text()
        if not text:
            return

        # вычисляем координаты окна
        x_shift = len(text) * 2
        x = self.widget.winfo_rootx() - x_shift
        y = self.widget.winfo_rooty() + 30

        # создание окна для подсказки
        # без системной рамки окна
        self.tip_window = Toplevel(self.widget)
        self.tip_window.wm_overrideredirect(True)
        self.tip_window.wm_geometry(f"+{x}+{y}")

        label = Label(self.tip_window, text=text, relief="solid", borderwidth=1)
        label.pack()

    # спрятать подсказку
    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


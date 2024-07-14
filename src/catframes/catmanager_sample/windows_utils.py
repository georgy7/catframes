from _prefix import *
from sets_utils import Lang
from task_flows import Task


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


class ScrollableFrame(ttk.Frame):
    """Прокручиваемый (умный) фрейм"""

    def __init__(self, root_window, *args, **kwargs):
        super().__init__(root_window, *args, **kwargs)
        
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
            self._update_scrollbar,  # прокрутки менялась, когда обновляется фрейм 
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

        # первичное обновление полосы, чтобы сразу её не было видно
        self._update_scrollbar_visibility()

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

    def __init__(self, master: ttk.Frame, task: Task):
        super().__init__(master, borderwidth=1, padding=5, style='Task.TFrame')
        self.widgets: dict = {}
        self.task: Task = task
        self.progress: float = 0

        self._init_widgets()
        self.update_texts()
        self._pack_widgets()

    # создание и настрйока виджетов
    def _init_widgets(self):
        self.left_frame = ttk.Frame(self, padding=5, style='Task.TFrame')

        image = Image.open("src/catframes/catmanager_sample/test_static/img.jpg")
        image_size = (80, 60)
        image = image.resize(image_size, Image.ADAPTIVE)
        image_tk = ImageTk.PhotoImage(image)

        self.widgets['_picture'] = ttk.Label(self.left_frame, image=image_tk)
        self.widgets['_picture'].image = image_tk


        # создании средней части бара
        self.mid_frame = ttk.Frame(self, padding=5, style='Task.TFrame')

        bigger_font = font.Font(size=16)

        # надпись в баре
        self.widgets['_lbPath'] = ttk.Label(  
            self.mid_frame, 
            font=bigger_font, padding=5,
            text=f"/usr/tester/movies/render{self.task.id}.mp4", 
            style='Task.TLabel'
        )

        self.widgets['_lbData'] = ttk.Label(  
            self.mid_frame, 
            font='14', padding=5,
            text=f"test label for options description in task {self.task.id}", 
            style='Task.TLabel'
        )


        # создание правой части бара
        self.right_frame = ttk.Frame(self, padding=5, style='Task.TFrame')
       
        # кнопка "отмена"
        self.widgets['btCancel'] = ttk.Button(self.right_frame, width=8, command=lambda: self.task.cancel())
        
        # полоса прогресса
        self.widgets['_progressBar'] = ttk.Progressbar(
            self.right_frame, 
            # length=320,
            maximum=1,
            value=0,
            style='Task.Horizontal.TProgressbar'
        )

    # упаковка всех виджетов бара
    def _pack_widgets(self):
        self.widgets['_picture'].pack(side='left')
        self.left_frame.pack(side='left')

        self.widgets['_lbPath'].pack(side='top', fill='x', expand=True)
        self.widgets['_lbData'].pack(side='top', fill='x', expand=True)
        self.mid_frame.pack(side='left')

        self.widgets['btCancel'].pack(side='bottom', expand=True)
        self.widgets['_progressBar'].pack(side='bottom', expand=True)
        self.right_frame.pack(side='left', expand=True)

        self.pack(pady=[0, 10])

    # обновление кнопки "отмена" после завершения задачи
    def update_cancel_button(self):
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
                widget.config(text=Lang.read(f'bar.{w_name}'))


class ImageCanvas(Canvas):
    """Объект холста с картинкой в окне создания задачи.
    на которой отображаются "умные" поля ввода.
    Если текст не введён - поле будет полупрозрачным."""
    
    def __init__(self, master: Tk, width: int, height: int, image_link: str = '', background: str = '#000'):

        # создаёт объект холста
        super().__init__(master, width=width, height=height, highlightthickness=0, background=background)
        self.height, self.width = height, width
        self.pack()

        self.img = None
        self.img_id = None
        self._create_image(image_link)
        self._create_entries()

    # инициализация полупрозрачнях треугольников и полей ввода
    def _create_entries(self):

        self.rects = []     # список полупрозрачных прямоугольников
        self.entries = []   # список всех полей ввода
        self.shown = []     # список отображаемых на холсте полей

        # переменные для расположения полей ввода
        rect_x_pad = 120
        rect_y_pad = 50
        rect_width = 186
        rect_height = 24

        # позиции прямоугольников и полей ввода на холсте, с левого верхнего по часовой стрелке
        positions = [
            (rect_x_pad, rect_y_pad),                            # верхний левый
            (self.width // 2, rect_y_pad),                            # верхний
            (self.width - rect_x_pad, rect_y_pad),               # верхний правый
            (self.width - rect_x_pad, self.height // 2),              # правый
            (self.width - rect_x_pad, self.height - rect_y_pad), # нижний правый
            (self.width // 2, self.height - rect_y_pad),              # нижний
            (rect_x_pad, self.height - rect_y_pad),              # нижний левый
            (rect_x_pad, self.height // 2),                           # левый
        ]

        # настройка и расположение прямоугольника и виджета для каждой позиции
        for pos in positions:
            rect = self.create_rectangle(            # инициализация прямоугольника
                pos[0] - (rect_width/2), 
                pos[1] - (rect_height/2), 
                pos[0] + (rect_width/2), 
                pos[1] + (rect_height/2),
                fill="white",                        # заливка
                stipple="gray25",                    # прозрачность
                tags="rect"
            )
            entry = Entry(self, font=("Arial", 12))  # инициализация поля ввода

            # наполнение объявленных выше списков
            self.rects.append(rect)
            self.entries.append(entry) 
            self.shown.append(None)

            # привязка события отображения поля ввода при нажатии на прямоугольник
            self.tag_bind(rect, "<Button-1>", lambda event, pos=pos, entry=entry: self._show_entry(event, pos, entry))

            # привязка события проверки и скрытия поля ввода, когда с него снят фокус
            entry.bind("<FocusOut>", lambda event, entry=entry: self._hide_entry_if_empty(event, entry))

    # отображает поле ввода
    def _show_entry(self, event, pos, entry):
        index = self.entries.index(entry)
        entry_window = self.create_window(pos, window=entry, anchor=CENTER)
        self.shown[index] = entry_window
        entry.focus_set()

    # прячет поле ввода, если в нём пусто
    def _hide_entry_if_empty(self, event, entry):
        if entry.get() == '':
            index = self.entries.index(entry)
            self.delete(self.shown[index])

    # приобразование ссылки на картинку в объект
    def _open_image(self, image_link: str):
        try:
            img = Image.open(image_link)                        # открытие изображения по пути
            img_ratio = img.size[0] / img.size[1]               # оценка соотношения сторон картинки
            img = img.resize(
                (int(self.height*img_ratio), self.height),      # масштабирование с учётом соотношения
                Image.LANCZOS
            )  
            self.img = ImageTk.PhotoImage(img)                  # загрузка картинки и создание виджета

        except FileNotFoundError:                                                 # если файл не найден
            self.img = ImageTk.PhotoImage(                                        # создаёт пустое изображение
                Image.new("RGBA", (self.width, self.height), (255, 255, 255, 0))  # с прозрачным фоном
            )

    # создание изображения
    def _create_image(self, image_link: str):
        self._open_image(image_link)
        self.img_id = self.create_image((self.width//2)-(self.img.width()//2), 0, anchor=NW, image=self.img)

    # обновление изображения 
    def update_image(self, image_link: str):
        self._open_image(image_link)
        self.itemconfig(self.img_id, image=self.img)                            # замена изображения
        self.coords(self.img_id, (self.width // 2)-(self.img.width() // 2), 0)  # повторное задание координат

    # формирует список из восьми строк, введённых в полях
    def fetch_entries_text(self) -> list:
        entries_text = map(lambda entry: entry.get(), self.entries)
        return list(entries_text)
    
    # обновляет цвета отступов холста
    def update_background_color(self, color: str):
        self.config(background=color)

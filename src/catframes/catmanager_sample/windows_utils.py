from _prefix import *
from sets_utils import TTK_THEME, Lang
from task_flows import Task


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

        image = Image.open("src/catframes/catmanager_sample/test_static/img.png")
        image_size = (80, 60)
        image = image.resize(image_size, Image.ADAPTIVE)
        image_tk = ImageTk.PhotoImage(image)

        self.widgets['_picture'] = ttk.Label(self.left_frame, image=image_tk)
        self.widgets['_picture'].image = image_tk


        # создании средней части бара
        self.mid_frame = ttk.Frame(self, padding=5, style='Task.TFrame')

        # надпись в баре
        self.widgets['_lbPath'] = ttk.Label(  
            self.mid_frame, 
            font='18', padding=5,
            text=f"/usr/tester/movies/renger{self.task.id}.mp4", 
            style='Task.TLabel'
        )

        self.widgets['_lbData'] = ttk.Label(  
            self.mid_frame, 
            font='14', padding=5,
            text=f"test label for options in task {self.task.id}", 
            style='Task.TLabel'
        )


        # создание правой части бара
        self.right_frame = ttk.Frame(self, padding=5, style='Task.TFrame')
       
        # кнопка "стоп"
        self.widgets['btStop'] = ttk.Button(self.right_frame, width=8, command=lambda: self.task.stop())
        
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

        self.widgets['btStop'].pack(side='bottom', expand=True)
        self.widgets['_progressBar'].pack(side='bottom', expand=True)
        self.right_frame.pack(side='left', expand=True)

        self.pack(pady=[0, 10])

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

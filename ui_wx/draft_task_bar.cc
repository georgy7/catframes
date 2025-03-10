/*

"""
Объект бара задачи это фрейм, в котором разные виджеты, относящиеся 
к описанию параметров задачи (картинка, лейблы для пути и параметров),
бар прогресса выполнения задачи, и кнопку отмены/удаления.

Название TaskBar сбивает с толку. Надо будет переименовать.
Необходимость в ScrollableFrame пропала ввиду наличия wxScrolledWindow.
"""

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
        self.error: Union[str, None] = None

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

        self.pack(pady=(10, 0), fill=X, expand=True)

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

*/

/*

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
        logger = logging.getLogger('catmanager')
        logger.info(f'Ask directory: initialdir = {GlobalStates.last_dir}')
        dir_name = filedialog.askdirectory(parent=self, initialdir=GlobalStates.last_dir, mustexist=True)
        logger.info(f'Ask directory result is {type(dir_name)}')
        logger.info(f'Ask directory returned {dir_name}')

        if not dir_name:
            logger.info(f'The folder is not defined.')
            return
        if not find_img_in_dir(dir_name):
            logger.info(f'Asked directory does not contain images.')
            msg_window_name = 'emptyFolder'

            message = Settings.lang.read(f'{msg_window_name}.theFollowingFolders')
            message += '\n\n'
            message += f'    • {dir_name}\n'

            LocalWM.open(TextDialog,
                         msg_window_name,
                         LocalWM.call('task'),
                         window_name=msg_window_name,
                         text=message).focus()
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

*/

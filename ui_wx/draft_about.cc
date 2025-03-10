/*
class AboutWindow(Toplevel, WindowMixin):
    """Окно информации о программе"""

    def __init__(self, root: RootWindow):
        super().__init__(master=root)
        self.name: str = "about"

        self.widgets: Dict[str, ttk.Widget] = {}
        self.texts: Dict[str, Text] = {}

        self.size: Tuple[int, int] = (570, 300)
        self.resizable(True, True)

        super()._default_set_up()

    # создание и настройка виджетов
    def _init_widgets(self):
        smaller_font = font.Font(size=11)

        self.main_frame = ttk.Frame(self)

        # виджет, позволяющий создавать вкладки
        self.notebook = ttk.Notebook(self.main_frame)

        self.app_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.app_tab, text="Приложение")

        self.app_bottom_field = ttk.Frame(self.app_tab)
        self.app_top_field = ttk.Frame(self.app_tab)
        self.app_left_table = ttk.Frame(self.app_top_field, relief=SOLID, borderwidth=1)

        self.texts["_txtTableLeft"] = Text(
            self.app_left_table,
            font=smaller_font,
            wrap=WORD,
            height=7,
            width=10,
            border=0,
            padx=8,
            pady=8
        )
        self.texts["_txtTableRight"] = Text(
            self.app_left_table,
            font=smaller_font,
            wrap=WORD,
            height=7,
            width=20,
            border=0,
            padx=5,
            pady=8
        )

        self.app_right_field = ttk.Frame(self.app_top_field)

        self.letter_image = base64_to_tk(LETTER_ICON_BASE64)
        self.widgets["_btMail"] = ttk.Button(
            self.app_right_field,
            image=self.letter_image,
            compound="left",
            command=lambda: webbrowser.open(EMAIL_ADRESS)
        )

        def copy_mail():
            self.clipboard_clear()
            self.clipboard_append(EMAIL_ADRESS)

        context_menu = Menu(self, tearoff=0)
        context_menu.add_command(label=Settings.lang.read("about.copyMail"), command=copy_mail)
        self.widgets["_btMail"].bind("<Button-3>", lambda e: context_menu.post(e.x_root, e.y_root))

        self.planet_image = base64_to_tk(PLANET_ICON_BASE64)
        self.widgets["_btSite"] = ttk.Button(
            self.app_right_field,
            image=self.planet_image,
            compound="left",
            command=lambda: webbrowser.open(WEBSITE_URL)
        )
        self.app_bottom_container = ttk.Frame(self.app_bottom_field, relief=SOLID, borderwidth=1)
        self.texts["_txtAbout"] = Text(
            self.app_bottom_container, 
            font=smaller_font,
            wrap=WORD,
            height=200,
            width=10,
            border=0,
            padx=15,
            pady=15
        )

        self.story_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.story_tab, text="История")

        self.story_container = ttk.Frame(self.story_tab, relief=SOLID, borderwidth=1)
        self.texts["txtChangeLog"] = Text(self.story_container, wrap=WORD, height=200, width=200, border=0)


    # расположение виджетов
    def _pack_widgets(self):
        self.main_frame.pack(expand=True, fill=BOTH)
        self.notebook.pack(expand=True, fill=BOTH, padx=10, pady=10)
        self.story_container.pack(expand=True, fill=BOTH, padx=10, pady=10)
        self.texts["txtChangeLog"].pack(expand=True, fill=BOTH)
        self._pack_app_tab()


    # упаковка виджетов вкладки "Приложение"
    def _pack_app_tab(self):
        self.app_left_table.pack(expand=True, fill=BOTH, side=LEFT, padx=10, pady=10, anchor=W)
        self.app_top_field.pack(expand=True, fill=BOTH, side=TOP)

        self.texts["_txtTableLeft"].pack(side=LEFT, padx=(0, 1))
        self.texts["_txtTableRight"].pack(side=RIGHT, expand=True, fill=X)

        self.app_right_field.pack(side=TOP, anchor=W, pady=5, padx=(0, 7))
        self.widgets["_btMail"].pack(side=TOP, pady=5)
        self.widgets["_btSite"].pack(side=TOP, pady=5)

        self.app_bottom_field.pack(side=LEFT, expand=True, fill=BOTH, padx=10, pady=(0, 10))
        self.app_bottom_container.pack(expand=True, fill=BOTH)
        self.texts["_txtAbout"].pack(expand=True, fill=BOTH)


    def update_texts(self) -> None:
        super().update_texts()

        def name_to_text(text_name):
            return Settings.lang.read(f"{self.name}.{text_name}")

        def get_complex_text(text_names: Tuple) -> str:
            texts = map(name_to_text, text_names)
            return "\n".join(texts)

        def set_text_and_lock(widget: Widget, text: str):
            widget.config(state=NORMAL)
            widget.delete("1.0", END)
            widget.insert("1.0", text)
            widget.config(state=DISABLED)

        # обёртывает текст в пробелы,
        # чтобы он занимал одинаковое расстояние на кнопке.  
        def wrap_spaces(name: str) -> str:
            text = name_to_text(name)
            spaces = " " * (8 - len(text))
            return spaces + text + spaces

        self.widgets["_btMail"].configure(text=wrap_spaces("btMail"))
        self.widgets["_btSite"].configure(text=wrap_spaces("btSite"))

        self.notebook.add(self.app_tab, text=name_to_text("appTab"))
        self.notebook.add(self.story_tab, text=name_to_text("storyTab"))

        left_text = get_complex_text(("txtName", "txtDesc", "txtVersion", "txtLicense"))
        set_text_and_lock(self.texts["_txtTableLeft"], left_text)

        right_text = get_complex_text(("txtNameContent", "txtDescContent", "txtVersionContent", "txtLicenseContent"))
        set_text_and_lock(self.texts["_txtTableRight"], right_text)

        set_text_and_lock(self.texts["_txtAbout"], name_to_text("txtAbout"))
*/

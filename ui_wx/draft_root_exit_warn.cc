/*

class WarningWindow(Toplevel, WindowMixin):
    """Окно предупреждения при выходе"""

    def __init__(self, root: RootWindow, **kwargs):
        super().__init__(master=root)
        self.name = "warn"
        self.type: str = kwargs.get("type")
        self.accept_def: Callable = kwargs.get("accept_def")

        self.widgets: Dict[str, Widget] = {}
        self.size = 260, 150
        self.resizable(False, False)

        super()._default_set_up()

    def _init_widgets(self):
        self.main_frame = ttk.Frame(self)

        # два лейбла предупреждения (с крупным текстом, и обычным)
        self.widgets["lbWarn"] = ttk.Label(
            self.main_frame, padding=[0, 20, 0, 5], font=font.Font(size=16)
        )
        self.widgets["lbText"] = ttk.Label(self.main_frame, padding=0)

        # кнопки "назад" и "выйти"
        self.choise_frame = ttk.Frame(self.main_frame)

        def accept():
            self.accept_def()
            self.close()

        self.widgets["btAccept"] = ttk.Button(self.choise_frame, command=accept)
        self.widgets["btDeny"] = ttk.Button(self.choise_frame, command=self.close)

    def _pack_widgets(self):
        self.main_frame.pack(expand=True, fill=BOTH)

        self.widgets["lbWarn"].pack(side=TOP)
        self.widgets["lbText"].pack(side=TOP)

        self.widgets["btAccept"].pack(side=LEFT, anchor="w", padx=5)
        self.widgets["btDeny"].pack(side=LEFT, anchor="w", padx=5)
        self.choise_frame.pack(side=BOTTOM, pady=10)

    def update_texts(self):
        for w_name, widget in self.widgets.items():
            new_text_data = Settings.lang.read(f"{self.name}.{self.type}.{w_name}")
            widget.config(text=new_text_data)

*/

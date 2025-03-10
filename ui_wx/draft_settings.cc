/*

class SettingsWindow(Toplevel, WindowMixin):
    """Окно настроек"""

    def __init__(self, root: RootWindow):
        super().__init__(master=root)
        self.name: str = "sets"

        self.widgets: Dict[str, ttk.Widget] = {}

        self.size: Tuple[int, int] = (250, 150)
        self.resizable(False, False)
        self.transient(root)

        self.bind("<FocusOut>", self._on_focus_out)

        super()._default_set_up()

    # при потере фокуса окна, проверяет, не в фокусе ли его виджеты
    def _on_focus_out(self, event):
        try:
            if not self.focus_get():
                return self.close()
        except:  # ловит ошибку, которая возникает при фокусе на комбобоксе
            pass

    # создание и настройка виджетов
    def _init_widgets(self):
        self.main_frame = ttk.Frame(self)
        self.content_frame = ttk.Frame(self.main_frame)

        # виджет и комбобокс языка
        self.widgets["lbLang"] = ttk.Label(self.content_frame)
        self.widgets["_cmbLang"] = ttk.Combobox(
            self.content_frame,
            values=Settings.lang.get_all(),  # вытягивает список языков
            state="readonly",
            width=9,
        )

        def open_logs():
            log_paths = TempLog.get_paths()
            if (log_paths is not None) and ('catmanager' in log_paths):
                log_file_path = Path(log_paths['catmanager'])
                logs_path = str(log_file_path.parent)
                my_system = platform.system()

                if my_system == 'Windows':
                    subprocess.run(['explorer', logs_path])
                elif my_system == 'Linux':
                    subprocess.run(['xdg-open', logs_path])
                elif my_system == 'Darwin':
                    subprocess.run(['open', '--', logs_path])

        self.widgets['btOpenLogs'] = ttk.Button(self.content_frame, command=open_logs)

        # виджет и комбобокс тем
        self.widgets["lbTheme"] = ttk.Label(self.content_frame)
        self.widgets["_cmbTheme"] = ttk.Combobox(
            self.content_frame,
            values=ttk.Style().theme_names(),
            state="readonly",
            width=9,
        )

        # применение настроек
        def apply_settings(event):
            current_theme = self.widgets["_cmbTheme"].current()
            Settings.theme.set(index=current_theme)
            current_lang = self.widgets["_cmbLang"].current()
            Settings.lang.set(index=current_lang)
            Settings.save()

            for window in LocalWM.all():
                window.update_texts()

        # привязка применения настроек к выбору нового значения в комбобоксах
        self.widgets["_cmbLang"].bind("<<ComboboxSelected>>", apply_settings)
        self.widgets["_cmbTheme"].bind("<<ComboboxSelected>>", apply_settings)

    # расположение виджетов
    def _pack_widgets(self):
        self.main_frame.pack(expand=True, fill=BOTH)
        self.content_frame.pack(padx=10, pady=30)

        self.widgets["lbLang"].grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.widgets["_cmbLang"].grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.widgets["_cmbLang"].current(
            newindex=Settings.lang.current_index
        )  # подставляем в ячейку текущий язык

        self.widgets["lbTheme"].grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.widgets["_cmbTheme"].grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        self.widgets["_cmbTheme"].current(newindex=Settings.theme.current_index)

        self.widgets['btOpenLogs'].grid(row=2, column=0, sticky='e', padx=5, pady=10)
        self.geometry("")

*/

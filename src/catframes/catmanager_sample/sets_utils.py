from _prefix import *


"""
Класс языковых настроек содержит большой словарь, 
в котором для каждого языка есть соответсвия названия
виджета, и текста, который в этом виджете расположен.

Добавление нового ключа в этот словарь должно быть с
добавлением всех внутренних ключей по аналогии с другими.

Если в процессе будет допущена ошибка, или gui запросит
текст для виджета, который не прописан, в качестве текста
вернётся строка из прочерков "-----" для быстрого обнаружения. 
"""


class Lang:
    """Класс языковых настроек.
    Позволяет хранить текущий язык,
    И извлекать его текстовики.

    При добавлении новых языков в словарь data,
    их названия будут сами подтягиваться в поле настроек.
    """

    data = {  # языковые теги (ключи) имеют вид: "область.виджет"
        "english": {
            "root.title": "Catmanager",
            "root.openSets": "Settings",
            "root.newTask": "Create",
            "bar.active": "processing",
            "bar.inactive": "complete",
            "bar.btInfo": "Info",
            "bar.btCancel": "Cancel",
            "bar.btDelete": "Delete",
            "bar.lbEmpty": "Your projects will appear here",
            "bar.error.noffmpeg": "Error! FFmpeg not found!",
            "bar.error.nocatframes": "Error! Catframes not found!",
            "bar.error.internal": "Internal process error!",
            "bar.error.failed": "Error! Process start failed!",
            "bar.lbQuality": "Quality:",
            "bar.lbFramerate": "Framerate:",
            "bar.lbColor": "Color:",
            "sets.title": "Settings",
            "sets.lbLang": "Language:",
            "sets.lbTheme": "Theme:",
            "sets.btApply": "Apply",
            "sets.btSave": "Save",
            "sets.btOpenLogs": "Show logs",
            "task.title": "New Task",
            "task.title.view": "Task settings view",
            "task.initText": "Add a directory\nof images",
            "task.lbColor": "Background:",
            "task.lbFramerate": "Framerate:",
            "task.lbQuality": "Quality:",
            "task.cmbQuality": ("high", "medium", "poor"),
            "task.lbResolution": "Render resolution:",
            "task.lbSaveAs": "Save as:",
            "task.btCreate": "Create",
            "task.btPathChoose": "choose",
            "task.lbCopy": "Copy cli:",
            "task.btCopyBash": "Bash",
            "task.btCopyWin": "Win",
            "task.cmbTime": ("1 sec", "2 sec", "3 sec", "4 sec", "5 sec"),
            "task.btPrevCancel": "Cancel",
            "task.lbPrevSign": "Processing preview...",
            "dirs.lbDirList": "List of source directories:",
            "dirs.btAddDir": "Add",
            "dirs.btRemDir": "Remove",
            "dirs.DirNotExists": "Doesn't exists. Removing...",
            "warn.exit.title": "Warning",
            "warn.exit.lbWarn": "Warning!",
            "warn.exit.lbText": "Incomplete tasks!",
            "warn.exit.btAccept": "Leave",
            "warn.exit.btDeny": "Back",
            "warn.cancel.title": "Warning",
            "warn.cancel.lbWarn": "Are you sure",
            "warn.cancel.lbText": "You want to cancel the task?",
            "warn.cancel.btAccept": "Yes",
            "warn.cancel.btDeny": "Back",
            "noti.title": "Error",
            "noti.lbWarn": "Invalid port range!",
            "noti.lbText": "The acceptable range is from 10240 to 65025",
            "noti.lbText2": "The number of ports is at least 100",
            "checker.title": "Necessary modules check",

            "emptyFolder.title": "Empty folder",
            "emptyFolder.theFollowingFolders": "The following folders do not contain images.\nTherefore, they were not added.",
        },
        "русский": {
            "root.title": "Catmanager",
            "root.openSets": "Настройки",
            "root.newTask": "Создать",
            "bar.lbActive": "обработка",
            "bar.lbInactive": "завершено",
            "bar.btInfo": "Инфо",
            "bar.btCancel": "Отмена",
            "bar.btDelete": "Удалить",
            "bar.lbEmpty": "Здесь появятся Ваши проекты",
            "bar.error.noffmpeg": "Ошибка! FFmpeg не найден!",
            "bar.error.nocatframes": "Ошибка! Catframes не найден!",
            "bar.error.internal": "Внутренняя ошибка процесса!",
            "bar.error.failed": "Ошибка при старте процесса!",
            "bar.lbQuality": "Качество:",
            "bar.lbFramerate": "Частота:",
            "bar.lbColor": "Цвет:",
            "sets.title": "Настройки",
            "sets.lbLang": "Язык:",
            "sets.lbTheme": "Тема:",
            "sets.btApply": "Применить",
            "sets.btSave": "Сохранить",
            "sets.btOpenLogs": "Показать логи",
            "task.title": "Новая задача",
            "task.title.view": "Просмотр настроек задачи",
            "task.initText": "Добавьте папку\nс изображениями",
            "task.lbColor": "Цвет фона:",
            "task.lbFramerate": "Частота кадров:",
            "task.lbQuality": "Качество:",
            "task.cmbQuality": ("высокое", "среднее", "низкое"),
            "task.lbResolution": "Разрешение рендера:",
            "task.lbSaveAs": "Сохранить как:",
            "task.btCreate": "Создать",
            "task.btPathChoose": "выбрать",
            "task.lbCopy": "Копировать cli:",
            "task.btCopyBash": "Bash",
            "task.btCopyWin": "Win",
            "task.cmbTime": ("1 сек", "2 сек", "3 сек", "4 сек", "5 сек"),
            "task.btPrevCancel": "Отмена",
            "task.lbPrevSign": "Создание предпросмотра...",
            "dirs.lbDirList": "Список директорий источников:",
            "dirs.btAddDir": "Добавить",
            "dirs.btRemDir": "Удалить",
            "dirs.DirNotExists": "Не существует. Удаление...",
            "warn.exit.title": "Внимание",
            "warn.exit.lbWarn": "Внимание!",
            "warn.exit.lbText": "Задачи не завершены!",
            "warn.exit.btAccept": "Выйти",
            "warn.exit.btDeny": "Назад",
            "warn.cancel.title": "Внимание",
            "warn.cancel.lbWarn": "Вы уверены,",
            "warn.cancel.lbText": "Что хотите отменить задачу?",
            "warn.cancel.btAccept": "Да",
            "warn.cancel.btDeny": "Назад",
            "noti.title": "Ошибка",
            "noti.lbWarn": "Неверный диапазон портов!",
            "noti.lbText": "Допустимы значения от 10240 до 65025",
            "noti.lbText2": "Количество портов не менее 100",
            "checker.title": "Проверка необходимых модулей",

            "emptyFolder.title": "Пустая директория",
            "emptyFolder.theFollowingFolders": "Следующие папки не были добавлены, т.к. не содержат изображений.",
        },
    }

    def __init__(self):
        self.current_name = "english"
        self.current_index = 0

    # получение всех доступных языков
    def get_all(self) -> tuple:
        return tuple(self.data.keys())

    # установка языка по имени или индексу
    def set(self, name: str = None, index: int = None) -> None:

        if name and name in self.data:
            self.current_index = self.get_all().index(name)
            self.current_name = name

        elif isinstance(index, int) and 0 <= index < len(self.data):
            self.current_name = self.get_all()[index]
            self.current_index = index

    # получение текста по тегу
    def read(self, tag: str) -> Union[str, tuple]:
        try:
            return self.data[self.current_name][tag]
        except KeyError:  # если тег не найден
            return "-----"


class Theme:
    """Класс настроек ttk темы"""

    master: Tk
    style: ttk.Style
    data: tuple
    current_name: str
    current_index: int

    # вызывается после создания главного окна
    def lazy_init(self, master: Tk):
        self.master = master
        self.style = ttk.Style()
        self.data = self.style.theme_names()
        self.set()

    def set_name(self, name: str):
        self.current_name = name

    def get_all(self):
        return self.data

    def set(self, index: Optional[int] = None):
        if not hasattr(self, "master"):
            return

        if index == None:
            self.current_index = self.data.index(self.current_name)
        else:
            self.current_name = self.data[index]
            self.current_index = index

        self.style.theme_use(self.current_name)
        self.set_styles()

        _font = font.Font(size=12)
        self.style.configure(style=".", font=_font)  # шрифт текста в кнопке
        self.master.option_add("*Font", _font)  # шрифты остальных виджетов

    def set_styles(self):
        self.style.configure("Main.TaskList.TFrame", background=MAIN_TASKLIST_COLOR)
        self.style.configure("Main.ToolBar.TFrame", background=MAIN_TOOLBAR_COLOR)

        # создание стилей фона таскбара для разных состояний
        for status, color in MAIN_TASKBAR_COLORS.items():
            self.style.configure(f"{status}.Task.TFrame", background=color)
            self.style.configure(f"{status}.Task.TLabel", background=color)
            self.style.configure(
                f"{status}.Task.Horizontal.TProgressbar", background=color
            )

        self.style.map(
            "Create.Task.TButton",
            background=[("active", "blue"), ("!disabled", "blue")],
        )


class UtilityLocator:
    """Ищет утилиты в системе по имени"""

    def __init__(self):
        self.use_ffmpeg_from_system_path: bool = False
        self.use_catframes_from_system_path: bool = False

        self.ffmpeg_full_path: Union[str, None] = None
        self.catframes_full_path: Union[str, None] = None

    def set_ffmpeg(self, is_in_sys_path: bool, full_path: str):
        self.use_ffmpeg_from_system_path = is_in_sys_path
        self.ffmpeg_full_path = full_path

    def set_catframes(self, is_in_sys_path: bool, full_path: str):
        self.use_catframes_from_system_path = is_in_sys_path
        self.catframes_full_path = full_path

    # метод для поиска ffmpeg в системе
    def find_ffmpeg(self) -> Union[str, None]:
        self.use_ffmpeg_from_system_path = self.find_in_sys_path('ffmpeg')
        self.ffmpeg_full_path = self.find_full_path('ffmpeg', self.use_ffmpeg_from_system_path)
        return self.ffmpeg_full_path

    # такой же, но для catframes
    def find_catframes(self) -> Union[str, None]:
        self.use_catframes_from_system_path = self.find_in_sys_path('catframes')
        self.catframes_full_path = self.find_full_path('catframes', self.use_catframes_from_system_path)
        return self.catframes_full_path

    # ищет полный путь для утилиты
    # если она есть в path, то ищет консолью
    @staticmethod
    def find_full_path(utility_name: str, is_in_sys_path: bool) -> Optional[str]:
        if is_in_sys_path:
            return UtilityLocator.find_by_console(utility_name)

        paths_to_check = UtilityLocator._get_paths(utility_name)
        for path in paths_to_check:
            if os.path.isfile(path):
                return path

    # ниходит полный путь утилиты при помощи консоли,
    # если она есть в системном path
    @staticmethod
    def find_by_console(utility_name) -> list:
        command = "where" if platform.system()== "Windows" else "which"
        result = subprocess.run(
            [command, utility_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        paths = result.stdout.decode()
        paths = map(lambda x: x.strip('\r '), paths.split('\n'))

        if platform.system() == "Windows":
            paths = filter(lambda x: x.endswith('.exe'), paths)

        paths = list(paths)
        return paths[0] if paths else None

    # возвращает пути, по которым может быть утилита, исходя из системы
    @staticmethod
    def _get_paths(utility_name: str) -> List[str]:
        system = platform.system()

        if system == "Windows":
            return [
                os.path.join(
                    os.environ.get("ProgramFiles", ""),
                    utility_name,
                    "bin",
                    f"{utility_name}.exe",
                ),
                os.path.join(
                    os.environ.get("ProgramFiles(x86)", ""),
                    utility_name,
                    "bin",
                    f"{utility_name}.exe",
                ),
            ]
        elif system == "Linux":
            return [
                "/usr/bin/" + utility_name,
                "/usr/local/bin/" + utility_name,
            ]
        elif system == "Darwin":
            return [
                "/usr/local/bin/" + utility_name,
                "/opt/homebrew/bin/" + utility_name,
            ]

    # проверка, есть ли утилита в системном path
    @staticmethod
    def find_in_sys_path(utility_name) -> bool:
        try:
            result = subprocess.run(
                [utility_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            output = ''
            for i in range(3):
                output += result.stderr.decode()
            if result.returncode == 0 or ("usage" in output):
                return True
        except FileNotFoundError:
            pass
        return False


class IniConfig:
    """Создание, чтение, и изменение внешнего файла конфига"""

    def __init__(self):
        self.file_path = os.path.join(os.path.expanduser("~"), CONFIG_FILENAME)
        self.file_exists = os.path.isfile(self.file_path)
        self.config = configparser.ConfigParser()

        if self.file_exists:
            self.config.read(self.file_path)
        else:
            self.set_default()

    # создание стандартного конфиг файла
    def set_default(self):
        self.config["Settings"] = {
            "Language": "english",
            "UseSystemPath": "yes",
            "TtkTheme": "vista" if platform.system() == "Windows" else "default",
        }
        self.config["AbsolutePath"] = {
            "FFmpeg": "",
            "Catframes": "",
        }
        self.config["SystemPath"] = {
            "FFmpeg": "",
            "Catframes": "",
        }

    # редактирование ключа в секции конфиг файла
    def update(self, section: str, key: str, value: Union[str, int]):
        if section in self.config:
            self.config[section][key] = value

    def save(self):
        with open(self.file_path, "w") as configfile:
            self.config.write(configfile)
        self.file_exists = True


class Settings:
    """Содержит объекты всех классов настроек"""

    lang = Lang()
    theme = Theme()
    util_locatior = UtilityLocator()
    conf = IniConfig()

    @classmethod
    def save(cls):
        cls.conf.update("Settings", "Language", cls.lang.current_name)
        cls.conf.update("Settings", "TtkTheme", cls.theme.current_name)
        cls.conf.save()

    @classmethod
    def restore(cls):
        cls.lang.set(cls.conf.config["Settings"]["Language"])
        cls.theme.set_name(cls.conf.config["Settings"]["TtkTheme"])
        cls.util_locatior.set_ffmpeg(
            is_in_sys_path=cls.conf.config["SystemPath"]["FFmpeg"]=='yes',
            full_path=cls.conf.config["AbsolutePath"]["FFmpeg"]
        )
        cls.util_locatior.set_catframes(
            is_in_sys_path=cls.conf.config["SystemPath"]["Catframes"]=='yes',
            full_path=cls.conf.config["AbsolutePath"]["Catframes"]
        )

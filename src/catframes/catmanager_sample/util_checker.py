from _prefix import *
from windows_base import *
from sets_utils import *
from windows_utils import *


class SingleCheck(ttk.Frame):

    def __init__(self, master: ttk.Frame, util_name: str, search_method: Callable):
        super().__init__(master)
        self.widgets: Dict[str, ttk.Widget] = {}
        self.util_name = util_name
        self.search_method = search_method
        self._init_widgets()
        self._pack_widgets()

    @abstractmethod
    def search_method() -> str:
        ...

    def _init_widgets(self):
        big_font = font.Font(size=20)
        mid_font = font.Font(size=14)
        self.top_frame = ttk.Frame()
        self.bottom_frame = ttk.Frame()

        self.widgets["main_label"] = ttk.Label(
            self.top_frame, font=big_font, text=f"{self.util_name}"
        )
        self.widgets["status_image"] = ttk.Label(
            self.top_frame, width=3, font=big_font, text="[--]"
        )
        self.widgets["bottom_label"] = ttk.Label(
            self.bottom_frame, font=mid_font, text = f"searching..."
        )

    def _pack_widgets(self):
        self.top_frame.pack(expand=True, fill=X, pady=(50, 0))
        self.bottom_frame.pack(expand=True, fill=X, pady=(0, 10))
        self.widgets["main_label"].pack(side=LEFT, padx=20)
        self.widgets["status_image"].pack(side=RIGHT, padx=20)
        self.widgets["bottom_label"].pack(side=LEFT, padx=20)

    def check(self):
        self.found: str = self.search_method()
        if self.found:
            text = shrink_path(self.found, 40)
            self.widgets["bottom_label"].configure(text=text)
            self.widgets["status_image"].configure(text="[++]")
        else:
            self.widgets["bottom_label"].configure(text="Not found")
            self.widgets["status_image"].configure(text="[XX]")


class UtilChecker(Tk, WindowMixin):
    """Окно, в котором происходит первичная проверка необходимых утилит"""

    def __init__(self):
        super().__init__()
        self.name: str = "checker"

        self.widgets: Dict[str, ttk.Widget] = {}

        self.size: Tuple[int] = 400, 400
        self.resizable(False, False)

        self.all_modules_checked = True

        super()._default_set_up()
        self.after(1000, self.start_check)

    def _init_widgets(self): 
        self.main_frame = ttk.Frame(self)
        
        def pil_search():
            if PIL_FOUND_FLAG:
                return "Installed in the current environment."
            
        self.pil = SingleCheck(self.main_frame, "Pillow", pil_search)
        self.ffmpeg = SingleCheck(
            self.main_frame, "FFmpeg", Settings.util_locatior.find_ffmpeg
        )
        self.catframes = SingleCheck(
            self.main_frame, "Catframes", Settings.util_locatior.find_catframes
        )

    def _pack_widgets(self):
        self.main_frame.pack(expand=True, padx=50, pady=100)
        self.pil.pack(expand=True)
        self.ffmpeg.pack(expand=True)
        self.catframes.pack(expand=True)

    def start_check(self):
        100, self.pil.check()
        1500, self.ffmpeg.check()
        2000, self.catframes.check()

    def close(self):
        if self.all_modules_checked:
            Settings.save()
            self.destroy()
        else:
            exit()

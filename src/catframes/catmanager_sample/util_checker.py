from _prefix import *
from windows_base import *
from sets_utils import *


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

    def _init_widgets(self):
        pass

    def _pack_widgets(self):
        pass

    def close(self):
        if self.all_modules_checked:
            Settings.save()
            self.destroy()
        else:
            exit()
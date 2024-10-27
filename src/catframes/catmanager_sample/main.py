from windows import RootWindow
from windows_base import LocalWM
from sets_utils import Settings
from _prefix import *
from util_checker import *


def check_utils():
    checker = UtilChecker()
    checker.mainloop()


def start_catmanager():
    root = LocalWM.open(RootWindow, "root")  # открываем главное окно
    root.mainloop()


def main():
    Settings.restore()
    if not Settings.conf.file_exists:
        check_utils()
    start_catmanager()


if __name__ == "__main__":
    main()

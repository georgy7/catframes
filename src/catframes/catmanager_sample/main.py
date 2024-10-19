from windows import RootWindow
from windows_base import LocalWM
from sets_utils import Settings


def main():
    Settings.restore()
    if not Settings.conf.file_exists:
        print("TODO вызов первичной проверки утилит")
    root = LocalWM.open(RootWindow, "root")  # открываем главное окно
    root.mainloop()


if __name__ == "__main__":
    main()

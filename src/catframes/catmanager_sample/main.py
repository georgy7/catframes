from windows import RootWindow
from windows_base import LocalWM


def main():
    root = LocalWM.open(RootWindow, "root")  # открываем главное окно
    root.mainloop()


if __name__ == "__main__":
    main()

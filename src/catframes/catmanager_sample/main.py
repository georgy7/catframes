from windows import RootWindow
from windows_base import LocalWM
# from task_flows import CatframesProcess


def main():
    # error = CatframesProcess.check_error()
    # if error:
    #     messagebox.showerror("Error", error)
    #     return
    root = LocalWM.open(RootWindow, 'root')  # открываем главное окно
    root.mainloop()

if __name__ == "__main__":
    main()

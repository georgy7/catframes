from _prefix import *
from windows import RootWindow
from windows_base import LocalWM
# from task_flows import CatframesProcess
from templog import TempLog


def main():
    # error = CatframesProcess.check_error()
    # if error:
    #     messagebox.showerror("Error", error)
    #     return
    with TempLog('catmanager'):
        logger = logging.getLogger('catmanager')
        logger.info('Logging is on.')
        root = LocalWM.open(RootWindow, 'root')  # открываем главное окно
        root.mainloop()

if __name__ == "__main__":
    main()

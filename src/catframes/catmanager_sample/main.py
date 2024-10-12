from _prefix import *
from windows import RootWindow
from windows_base import LocalWM
# from task_flows import CatframesProcess
from templog import TempLog, has_console


def main():
    # error = CatframesProcess.check_error()
    # if error:
    #     messagebox.showerror("Error", error)
    #     return
    with TempLog('catmanager'):
        logger = logging.getLogger('catmanager')
        logger.info('Logging is on.')

        logger.info(f'Executable: {sys.executable}')
        logger.info(f'File: {__file__}')
        logger.info(f'Console: {has_console()}')

        root = LocalWM.open(RootWindow, 'root')  # открываем главное окно
        root.mainloop()

if __name__ == "__main__":
    main()

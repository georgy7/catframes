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

        logger.info(f'sys.argv[0]: {sys.argv[0]}')
        logger.info(f'Executable: {sys.executable}')
        logger.info(f'File: {__file__}\n')

        compiled: bool = '__compiled__' in globals()
        logger.info(f"'__compiled__' in globals(): {compiled}\n")
        if compiled:
            logger.info(f"__compiled__: {globals()['__compiled__']}\n")

        logger.info(f'platform.system(): {platform.system()}')
        logger.info(f'sys.platform: {sys.platform}\n')

        logger.info(f'Console: {has_console()}')
        logger.info(f'Standard input type: {type(sys.stdin)}')
        logger.info(f'Standard output type: {type(sys.stdout)}\n')

        root = LocalWM.open(RootWindow, 'root')  # открываем главное окно
        root.mainloop()

if __name__ == "__main__":
    main()

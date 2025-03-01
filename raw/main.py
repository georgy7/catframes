from _prefix import *
from windows import RootWindow
from windows_base import LocalWM
from sets_utils import Settings
from util_checker import *
from templog import TempLog, has_console, compiled


def check_utils():
    checker = UtilChecker()
    checker.mainloop()


def start_catmanager():
    root = LocalWM.open(RootWindow, "root")  # открываем главное окно
    root.mainloop()


def main():
    with TempLog('catmanager'):
        logger = logging.getLogger('catmanager')
        logger.info('Logging is on.')

        logger.info(f'sys.argv[0]: {sys.argv[0]}')
        logger.info(f'Executable: {sys.executable}')
        logger.info(f'File: {__file__}\n')

        logger.info(f'platform.system(): {platform.system()}')
        logger.info(f'sys.platform: {sys.platform}\n')

        logger.info(f'Console: {has_console()}')
        logger.info(f'Compiled: {compiled()}\n')

        Settings.restore()
        if not Settings.conf.file_exists:
            check_utils()
        start_catmanager()


if __name__ == "__main__":
    main()

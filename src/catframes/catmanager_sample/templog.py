from _prefix import *


class TempLog:
    """
    Logging into a temporary folder.
    Use it as follows.

    .. code-block:: python

        def example_function():
            logger = logging.getLogger('mylog')
            logger.info('Something happened.')

        def main():
            with TempLog('mylog'):
                # everything that runs
                # in the main application thread
            # Now the temporary folder removed.

    You can also get paths of its openned files,
    using the class method `get_paths`.
    """
    _paths: Dict[str, Path] = {}

    @classmethod
    def get_paths(cls) -> Dict[str, Path]:
        return cls._paths.copy()

    def __init__(self, logger_name: str):
        self.logger_name: str = logger_name
        self._tmp_dir: Union[tempfile.TemporaryDirectory, None] = None
        self._file_handler: Union[WatchedFileHandler, None] = None

    def __enter__(self) -> None:
        self._tmp_dir = tempfile.TemporaryDirectory(prefix="catmanager_")
        filepath = Path(self._tmp_dir.__enter__()) / (self.logger_name + '_debug.log')

        self._file_handler = WatchedFileHandler(filepath)
        self._file_handler.setLevel(logging.DEBUG)

        logger = logging.getLogger(self.logger_name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(self._file_handler)

        self._paths[self.logger_name] = filepath

    def __exit__(self, exc_type, exc_value, traceback):
        del self._paths[self.logger_name]

        if self._file_handler:
            logger = logging.getLogger(self.logger_name)
            logger.removeHandler(self._file_handler)
            self._file_handler.flush()
            self._file_handler.close()
            self._file_handler = None

        if self._tmp_dir:
            self._tmp_dir.__exit__(exc_type, exc_value, traceback)

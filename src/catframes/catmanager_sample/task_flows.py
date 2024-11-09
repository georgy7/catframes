from _prefix import *


"""
Слой задач полностью отделён от gui.

Задачи создаются с помощью TaskManager, который
выдаёт им уникальные номера, и регистрирует их статусы.

При создании задачи, ей передаюётся нужная конфигурация,
которая представляет собой объект класса TaskConfig.
Атрибутами этого объекта являются все возможные параметры,
которые есть у консольной версии приложения catframes.
Этот объект имеет метод конвертирования в консольную команду,
которая и будет запущена самим процессом задачи при старте.

Чтобы в процессе обработки, задача могла как-то делиться
своим статусом с интерфейсом, реализован паттерн "наблюдатель".
При старте задачи, ей передаётся объект класса GuiCallback.
При инициализации, объект коллбэка принимает внешние зависимости,
чтобы у задачи была возможность обновлять свои статусы в gui.
"""


class TaskConfig:
    """Настройка и хранение конфигурации задачи.
    Создаётся и настраивается на слое gui.
    Позволяет конвертировать в команду catframes."""

    overlays_names = [
        "--top-left",
        "--top",
        "--top-right",
        "--right",
        "--bottom-right",
        "--bottom",
        "--bottom-left",
        "--left",
    ]

    quality_names = ("high", "medium", "poor")

    def __init__(self) -> None:

        self._dirs: List[str] = []
        self._overlays: Dict[str, str] = {}
        self._color: str = DEFAULT_CANVAS_COLOR
        self._framerate: int = 30
        self._quality: str = "medium"
        self._quality_index: int = 1
        self._limit: Optional[int] = None
        self._filepath: str = ""
        self._rewrite: bool = False

    def set_dirs(self, dirs: List[str]) -> list:
        self._dirs = dirs

    def set_overlays(self, overlays_texts: List[str]):
        self._overlays = dict(zip(self.overlays_names, overlays_texts))

    def set_color(self, color: str):
        self._color = color

    def set_preview_params(self, limit: int, path: str):
        self._limit = limit
        self._filepath = path

    # установка частоты кадров, качества и лимита
    def set_specs(self, framerate: int, quality: int, limit: int = None):
        self._framerate = framerate
        self._quality_index = quality
        self._quality = self.quality_names[quality]
        self._limit = limit

    def set_filepath(self, filepath: str):
        self._filepath = filepath

    def get_filepath(self) -> str:
        return self._filepath

    def get_dirs(self) -> list:
        return self._dirs[:]

    def get_quality(self) -> int:
        return self._quality_index

    def get_framerate(self) -> int:
        return self._framerate

    def get_overlays(self) -> List[str]:
        return list(self._overlays.values())

    def get_color(self) -> str:
        return self._color

    @staticmethod
    def to_user_format(text: str, bash: bool) -> str:
        text = text.replace("\n", "\\n")
        text = text.replace("\r", "\\r")
        text = text.replace("\t", "\\t")
        return TaskConfig.wrap_quots(text, bash)
    
    @staticmethod
    def wrap_quots(text: str, bash: bool) -> str:
        q = "'" if bash else '"'
        return q + text + q

    # создание консольной команды в виде списка
    def convert_to_command(
        self, for_user: bool = False, bash: bool = True
    ) -> List[str]:
        command = ["catframes"]

        for position, text in self._overlays.items():
            if text:
                if for_user:
                    text = self.to_user_format(text, bash)
                    command.append(f"{position}={text}")
                else:
                    command.append(position)
                    command.append(text)

        color = self._color
        if for_user:
            color = self.wrap_quots(color, bash)
        command.append(f"--margin-color={color}")
        command.append(f"--frame-rate={self._framerate}")
        command.append(f"--quality={self._quality}")

        if os.path.isfile(self._filepath):  # флаг перезаписи, если файл уже есть
            command.append("--force")

        for dir in self._dirs:  # добавление директорий с изображениями
            if for_user:
                dir = self.to_user_format(dir, bash)
            command.append(dir)

        if for_user:
            # добавление полного пути файла в кавычках
            command.append(self.to_user_format(self._filepath, bash))  
        else:
            command.append(self._filepath)
            command.append("--live-preview")

        if self._limit:
            command.append(f"--limit={self._limit}")

        return command


class GuiCallback:
    """Интерфейс для инъекции внешних методов от gui.
    Позволяет из задачи обновлять статус на слое gui."""

    def __init__(
        self,
        update_function,
        finish_function,
        error_function,
        delete_function,
    ):
        self.update = update_function
        self.finish = finish_function
        self.set_error = error_function
        self.delete = delete_function

    @staticmethod  # метод из TaskBar
    def update(progress: float, base64_img: str = ""):
        """обновление полосы прогресса и превью в окне"""
        ...

    @staticmethod  # метод из RootWindow
    def finish(id: int):
        """сигнал о завершении задачи"""
        ...

    @staticmethod
    def set_error(id: int, error: str):
        """сигнал об ошибке в выполнении"""
        ...

    @staticmethod  # метод из RootWindow
    def delete(id: int):
        """сигнал об удалении задачи"""
        ...


class CatframesProcess:
    """Создаёт подпроцесс с запущенным catframes,
    создаёт отдельный поток для чтения порта api,
    чтобы не задерживать обработку gui программы.
    По запросу может сообщать данные о прогрессе.
    """

    def __init__(self, command):
        if sys.platform == "win32":
            # Обработка сигналов завершения в Windows выглядит как большой беспорядок.
            # Если убрать этот флаг, CTRL+C будет отправляться как в дочерний, так и в родительский процесс.
            # Если использовать этот флаг, CTRL+C не работает вообще, зато работает CTRL+Break.
            # Этот флаг обязателен к использованию также и согласно документации Python, если мы хотим
            # отправлять в подпроцесс эти два сигнала:
            # https://docs.python.org/3/library/subprocess.html#subprocess.Popen.send_signal
            os_issues = {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP}
        else:
            os_issues = {}

        self.process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, **os_issues
        )

        self.error: Optional[str] = None
        self._progress = 0.0
        self._image_base64 = ""
        threading.Thread(
            target=self._update_progress, daemon=True
        ).start()  # запуск потока обновления прогресса из вывода stdout

    def _update_progress(self):  # обновление прогресса, чтением вывода stdout
        progress_pattern = re.compile(r"Progress: +[0-9]+")
        image_base64_pattern = re.compile(r"Preview: [a-zA-Z0-9+=/]+")

        # читает строки вывода процесса
        for line in io.TextIOWrapper(self.process.stdout):
            if "FFmpeg not found" in line:
                self.error = NO_FFMPEG_ERROR

            # ищет в строке процент прогресса
            progress_data = re.search(progress_pattern, line)

            if progress_data:
                # если находит, забирает число
                progress_percent = int(progress_data.group().split()[1])

                # если процент 100 - предерживает его
                if self._progress != 100:
                    self._progress = progress_percent / 100

            image_data = re.search(image_base64_pattern, line)
            if image_data:
                self._image_base64 = image_data.group().split()[1]


        ret_code = self.process.poll()
        while None == ret_code:
            ret_code = self.process.poll()

        # если процесс завершился некорректно
        if ret_code != 0 and not self.error:
            self.error = INTERNAL_ERROR  # текст последней строки

        self._progress == 1.0

    def get_progress(self):
        return self._progress

    def get_image_base64(self):
        return self._image_base64

    # убивает процесс (для экстренной остановки)
    def kill(self):
        if sys.platform == "win32":
            # CTRL_C_EVENT is ignored for process groups
            # https://learn.microsoft.com/ru-ru/windows/win32/procthread/process-creation-flags
            os.kill(self.process.pid, signal.CTRL_BREAK_EVENT)
        else:
            os.kill(self.process.pid, signal.SIGTERM)

        # Раз уж удаление делается не через callback или Promise, нужно сделать это синхронно.
        # Мы не можем полагаться на удачу. Мы должны всегда получить одинаковое поведение
        # (удаление видео в случае отмены).
        while None == self.process.poll():
            time.sleep(0.1)


class Task:
    """Класс самой задачи, связывающейся с catframes"""

    def __init__(self, id: int, task_config: TaskConfig) -> None:
        self.config: TaskConfig = task_config
        self.command: list = task_config.convert_to_command()

        self._process_thread: CatframesProcess = None
        self.id: int = id

        self.done: bool = False  # флаг завершённости
        self.stop_flag: bool = False  # требование остановки

    # запуск задачи
    def start(self, gui_callback: GuiCallback):  # инъекция колбека
        self.gui_callback = gui_callback
        TaskManager.reg_start(self)

        try:  # запуск фонового процесса catframes
            self._process_thread = CatframesProcess(self.command)

        except FileNotFoundError:  # если catframes не найден
            return self.handle_error(NO_CATFRAMES_ERROR)

        except Exception as e:  # если возникла другая ошибка, обработает её
            return self.handle_error(START_FAILED_ERROR)

        # запуск потока слежения за прогрессом
        threading.Thread(target=self._progress_watcher, daemon=True).start()

    # спрашивает о прогрессе, обновляет прогрессбар, обрабатывает завершение
    def _progress_watcher(self):
        progress: float = 0.0

        while progress < 1.0 and not self.stop_flag:  # пока прогрес не завершён
            time.sleep(0.2)
            progress = self._process_thread.get_progress()
            image = self._process_thread.get_image_base64()

            self.gui_callback.update(progress, base64_img=image)

            if self._process_thread.error and not self.stop_flag:
                return self.handle_error(self._process_thread.error)

        self.finish()

    # обработка ошибки процесса
    def handle_error(self, error: str):
        TaskManager.reg_finish(self)
        self.gui_callback.set_error(self.id, error=error)

    # обработка финиша задачи
    def finish(self):
        self.done = True
        TaskManager.reg_finish(self)
        self.gui_callback.finish(self.id)

    # остановка задачи
    def cancel(self):
        self.stop_flag = True
        TaskManager.reg_finish(self)
        self._process_thread.kill()
        self.delete_file()
        self.gui_callback.delete(self.id)

    # удаляет файл в системе
    def delete_file(self):
        file = self.config.get_filepath()
        try:
            os.remove(file)
        except:
            # Just in case someone opened the video in a player
            # while it was being encoded or something.
            pass

    def delete(self):
        TaskManager.wipe(self)
        self.gui_callback.delete(self.id)


class TaskManager:
    """Менеджер задач.
    Позволяет регистрировать задачи,
    и управлять ими."""

    _last_id: int = 0  # последний номер задачи
    _all_tasks: dict = {}  # словарь всех задач
    _running_tasks: dict = {}  # словарь активных задач

    # фабричный метод, создания задачи с уникальным id
    @classmethod
    def create(cls, task_config: TaskConfig) -> Task:
        cls._last_id += 1
        unic_id = cls._last_id

        task = Task(unic_id, task_config)
        cls._reg(task)
        return task

    # регистрация задачи
    @classmethod
    def _reg(cls, task: Task) -> None:
        cls._all_tasks[task.id] = task

    # регистрация запуска задачи
    @classmethod
    def reg_start(cls, task: Task) -> None:
        cls._running_tasks[task.id] = task

    # удаление регистрации запуска задачи
    @classmethod
    def reg_finish(cls, task: Task) -> None:
        if task.id in cls._running_tasks:
            cls._running_tasks.pop(task.id)

    # получение списка активных задач
    @classmethod
    def running_list(cls) -> list:
        return list(cls._running_tasks.values())

    # удаление задачи
    @classmethod
    def wipe(cls, task: Task) -> None:
        cls.reg_finish(task)
        if task.id in cls._all_tasks:
            cls._all_tasks.pop(task.id)

    # получение списка всех задач
    @classmethod
    def all_list(cls) -> list:
        return list(cls._all_tasks.values())

    # проверка существования задачи
    @classmethod
    def check(cls, task_id: int) -> bool:
        return task_id in cls._all_tasks

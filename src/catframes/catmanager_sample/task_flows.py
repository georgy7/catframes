from _prefix import *


class TaskConfig:
    """Хранение конфигурации текущей задачи.
    Позволяет конвертировать в команду catframes,
    проверив валидность каждого из параметров."""

    def __init__(self) -> None:
        self.dirs: list = []                      # пути к директориям с изображениями
        self.sure_flag: bool = False                 # флаг для предотвращения ошибок, если нет директории
        self.overlays: dict = {}                     # словрь надписей {'--left-top': 'надпись'}
        self.margin_color: str = '#000'              # цвет отступов и фона
        self.frame_rate: int = 30                    # частота кадров (от 1 до 60)
        self.quality: str = 'medium'                 # качество видео (poor, medium, high)
        self.limit: Optional[int]                    # предел видео в секундах
        self.force_flag: bool = False                # перезапись конечного файла, если существует
        self.port_range: Optional[Tuple[int, int]]   # диапазон портов для связи с ffmpeg
        self.path: str = '.'                         # путь к директории сохранения
        self.file_name: str = 'unknown'               # имя файла
        self.extension: str = 'mp4'                  # расширение файла

    # проверка каждого атрибута на валидность, создание консольной команды
    def convert_to_command(self) -> str:
        command = 'catframes'
        invalid_characters = ('\\', '"', '\'', '$', '(', ')', '[', ']')

        # if self.sure_flag:
        #     command += ' -s'
        
        # проверка текстовых оверлеев
        for position, text in self.overlays.items():
            if position not in (
                'left',
                'right',
                'top',
                'bottom',
                'left-top',
                'left-bottom',
                'right-top',
                'right-bottom',
                'top-left',
                'top-right',
                'bottom-left',
                'bottom-right',
            ): raise AttributeError('overlay_position')
            if invalid_characters in text:
                raise AttributeError('overlay_text')
            command += f" --{position} '{text}'"
        
        # проверка корректности строки с rgb
        rgb_pattern = re.compile(r'^#([a-fA-F0-9]{3}|[a-fA-F0-9]{6})$')
        if not rgb_pattern.match(self.margin_color):
            raise AttributeError(
                f'incorrect color: {self.margin_color}'
            )
        command += f" --margin-color {self.margin_color}"

        # проверка выбора частоты кадров
        if self.frame_rate < 1 or self.frame_rate > 60:
            raise AttributeError('frame_rate')
        command += f" --frame-rate {self.frame_rate}"

        # проверка выбора качества рендера
        if self.quality not in ['poor', 'medium', 'high']:
            raise AttributeError('quality')
        command += f" --quality {self.quality}"

        # проверка наличия и валидности ограничения времени
        if hasattr(self, 'limit'):
            if self.limit < 1:
                raise AttributeError('limit')
            command += f" --limit {self.limit}"

        # проверка флага перезаписи
        if self.force_flag:
            command += f" --force"

        # проверка наличия и валидности ограничения портов
        if hasattr(self, 'port_range'):
            if self.port_range[0] > self.port_range[1]:
                raise AttributeError('port_range')
            if self.port_range[1] < 10240 or self.port_range[0] > 65535:
                raise AttributeError('port_range')
            command += f" --port-range {self.port_range[0]}:{self.port_range[1]}"
        
        # проверка наличия директорий с зображениями
        for dir in self.dirs:
            if not os.path.isdir(dir):
                raise AttributeError('dirs')
            command += f" {dir}"

        # проверка на наличие запрещённых символов
        for c in invalid_characters:
            if c in self.file_name:
                raise AttributeError('filename')

        # проверка на наличие директории конечного файла
        if not os.path.isdir(self.path):
            raise AttributeError('path')
        
        # проверка валидности выбора расширения файла
        if self.extension not in ('mp4', 'webm'):
            raise AttributeError('extension')

        # сборка полного пути файла        
        full_file_path = f"{self.path}/{self.file_name}.{self.extension}"
        command += f" {full_file_path}"

        # проверка, есть ли такой файл, если не установлен флаг перезаписи
        if os.path.isfile(full_file_path) and not self.force_flag:
            return AttributeError('exists')
        
        return command  # возврат полной собранной команды


class GuiCallback:
    """Интерфейс для инъекции внешних методов от gui.
    Позволяет из задачи обновлять статус на слое gui."""

    def __init__(
            self,
            update_function,
            finish_function,
            delete_function,
            ):
        self.update = update_function
        self.finish = finish_function
        self.delete = delete_function
        
    
    @staticmethod  # метод из TaskBar
    def update(progress: float, delta: bool = False):
        """обновление полосы прогресса в окне"""
        ...

    @staticmethod  # метод из RootWindow
    def finish(id: int):
        """сигнал о завершении задачи"""
        ...

    @staticmethod  # метод из RootWindow
    def delete(id: int):
        """сигнал об удалении задачи"""
        ...


class Task:
    """Класс самой задачи, связывающейся с catframes"""

    def __init__(self, id: int, task_config: TaskConfig) -> None:
        self.config = task_config
        self.id = id  # получение уникального номера
        self.done = False  # флаг завершённости
        self.stop_flag = False  # требование остановки

    # запуск задачи (тестовый)
    def start(self, gui_callback: GuiCallback):  # инъекция зависимосей 
        self.gui_callback = gui_callback         # для оповещения наблюдателя

        # запуск фоновой задачи (дальше перепишется через subprocess)
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()
        TaskManager.reg_start(self)

    # поток задачи (тестовый)
    def run(self):
        for i in range(21):
            if self.stop_flag:
                return
            self.gui_callback.update(i/20)
            time.sleep(0.2)
        self.done = True
        TaskManager.reg_finish(self)
        self.gui_callback.finish(self.id)  # сигнал о завершении задачи

    # остановка задачи (тестовая)
    def cancel(self):
        self.stop_flag = True
        TaskManager.reg_finish(self)
        self.gui_callback.delete(self.id)  # сигнал о завершении задачи

    def delete(self):
        TaskManager.wipe(self)
        self.gui_callback.delete(self.id)  # сигнал об удалении задачи


class TaskManager:
    """Менеджер задач.
    Позволяет регистрировать задачи,
    и управлять ими."""

    _last_id: int = 0          # последний номер задачи
    _all_tasks: dict = {}      # словарь всех задач
    _running_tasks: dict = {}  # словарь активных задач

    @classmethod
    def create(cls, task_config: TaskConfig) -> Task:
        cls._last_id += 1  # увеличение последнего номера задачи
        unic_id = cls._last_id  # получение уникального номера

        task = Task(unic_id, task_config)  # создание задачи
        cls._reg(task)  # регистрация в менеджере
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
    
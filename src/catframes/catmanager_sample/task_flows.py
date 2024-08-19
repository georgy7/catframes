from _prefix import *
from sets_utils import PortSets


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
        '--top-left',
        '--top',
        '--top-right',
        '--right',
        '--bottom-right',
        '--bottom',
        '--bottom-left',
        '--left',
    ]

    quality_names = ('high', 'medium', 'poor')

    def __init__(self) -> None:
                
        self._dirs: List[str] = []                    # пути к директориям с изображениями
        self._overlays: Dict[str, str] = {}           # словарь надписей
        self._color: str = DEFAULT_COLOR              # цвет отступов и фона
        self._framerate: int                          # частота кадров
        self._quality: str                            # качество видео
        self._quality_index: int = 0                  # номер значения качества
        self._limit: int                              # предел видео в секундах
        self._filepath: str                           # путь к итоговому файлу
        self._rewrite: bool = False                   # перезапись файла, если существует
        self._ports = PortSets.get_range()            # диапазон портов для связи с ffmpeg
        self._resolution = None                       # разрешение рендера (нужно для режима просмотра)

    # установка директорий
    def set_dirs(self, dirs) -> list:
        self._dirs = dirs

    # установка оверлеев
    def set_overlays(self, overlays_texts: List[str]):
        # if any(s == "" for s in overlays_texts):
        #     empty = overlays_texts.index("")
        #     overlays_texts[empty] = "warn"

        self._overlays = dict(zip(self.overlays_names, overlays_texts))

    # установка цвета
    def set_color(self, color: str):
        self._color = color

    # установка частоты кадров, качества и лимита
    def set_specs(self, framerate: int, quality: int, limit: int = None):
        self._framerate = framerate
        self._quality_index = quality
        self._quality = self.quality_names[quality]
        self._limit = limit

    def set_resolution(self, width: int, height: int):
        self._resolution = width, height

    # установка пути файла
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
    
    def get_resolution(self) -> Optional[Tuple[int]]:
        return self._resolution

    def convert_to_resolution_command(self) -> str:
        command = 'catframes'
        if sys.platform == "win32":
            command = 'catframes.exe'

        for dir in self._dirs:                              # добавление директорий с изображениями
            command += f' "{dir}"'

        command += ' --resolutions'
        return command

    # создание консольной команды в виде списка
    def convert_to_command(self) -> List[str]:
        command = ['catframes']
        if sys.platform == "win32":
            command = ['catframes.exe']
    
        # добавление текстовых оверлеев
        for position, text in self._overlays.items():
            if text:
                command.append(f'{position}="{text}"')
        
        command.append(f'--margin-color={self._color}')     # параметр цвета
        command.append(f"--frame-rate={self._framerate}")   # частота кадров
        command.append(f"--quality={self._quality}")        # качество рендера

        if self._limit:                                     # ограничение времени, если есть
            command.append(f"--limit={self._limit}")

        if os.path.isfile(self._filepath):                  # флаг перезаписи, если файл уже есть
            command.append("--force")

        command.append(f"--port-range={self._ports[0]}:{self._ports[1]}")  # диапазон портов
        
        for dir in self._dirs:                              # добавление директорий с изображениями
            command.append(dir)
        
        command.append(self._filepath)                      # добавление полного пути файла    
        return command                                      # возврат собранной команды


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
    def update(progress: float, delta: bool = False):
        """обновление полосы прогресса в окне"""
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
    """ Создаёт подпроцесс с запущенным catframes,
    создаёт отдельный поток для чтения порта api, 
    чтобы не задерживать обработку gui программы.
    По запросу может сообщать данные о прогрессе.
    """

    def __init__(self, command):

        # в зависимости от системы, дополнительные аргументы при создании процесса
        if sys.platform == 'win32':
            # для windows создание отдельной группы, чтобы завершить всё
            os_issues = {'creationflags': subprocess.CREATE_NEW_PROCESS_GROUP}
        else:
            # для unix создание процесса с новой сессией
            os_issues = {'preexec_fn': os.setsid}

        self.process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, **os_issues)  # запуск catframes

        self.error_flag = False
        self._progress = 0.0
        threading.Thread(target=self._update_progress, daemon=True).start()  # запуск потока обновления прогресса из вывода stdout
        # self._port = 0
        # threading.Thread(target=self._recognize_port, daemon=True).start()  # запуск потока распознования порта

    def _update_progress(self):  # обновление прогресса, чтением вывода stdout
        pattern = re.compile(r'Progress: +[0-9]+')

        for line in io.TextIOWrapper(self.process.stdout):  # читает строки вывода процесса
            data = re.search(pattern, line)                 # ищет в строке процент прогресса
            if data:
                progress_percent = int(data.group().split()[1])  # если находит, забирает число
                if self._progress != 100:                  # если процент 100 - предерживает его
                    self._progress = progress_percent/100  # переводит чистый процент в сотые

        if self.process.poll() != 0:  # если процесс завершился некорректно
            self.error_flag = True    # ставит флаг ошибки

        self._progress == 1.0         # полный прогресс только после завершения скрипта

    def get_progress(self):
        return self._progress

    # # получение порта api процесса
    # def _recognize_port(self):
    #     while not self._port:
    #         text = self.process.stdout.readline()
    #         if not 'port' in text:
    #             continue
    #         self._port = int(text.replace('port:', '').strip())

    # # возвращает прогресс (от 0.0 до 1.0), полученный от api процесса
    # def get_progress(self) -> float:
    #     if not self._port:  # если порт ещё не определён
    #         return 0.0

    #     try: # делает запрос на сервер, возвращает прогресс
    #         data = requests.get(f'http://127.0.0.1:{self._port}/progress', timeout=1).json()        
    #         return data['framesEncoded'] / data['framesTotal']
    #     except Exception:  # если сервер закрылся, возвращает единицу, т.е. процесс завершён
    #         return 1.0
        
    # убивает процесс (для экстренной остановки)
    def kill(self):
        if sys.platform == 'win32':  # исходя из системы, завершает семейство процессов
            self.process.send_signal(signal.CTRL_BREAK_EVENT)
        else:
            parent_pid = self.process.pid
            os.killpg(os.getppid(parent_pid), signal.SIGTERM)


class Task:
    """Класс самой задачи, связывающейся с catframes"""

    def __init__(self, id: int, task_config: TaskConfig) -> None:
        self.config = task_config
        self.command = task_config.convert_to_command()
        # print(self.command)

        # # !!! команда тестового api, а не процесса catframes
        # run_dir = os.path.dirname(os.path.abspath(__file__))
        # self.command = f'python {run_dir}/test_api/test_catframes_api.py'

        self._process_thread: CatframesProcess = None
        self.id = id  # получение уникального номера
        self.done = False  # флаг завершённости
        self.stop_flag = False  # требование остановки

    # запуск задачи
    def start(self, gui_callback: GuiCallback):  # инъекция зависимосей 
        self.gui_callback = gui_callback         # для оповещения наблюдателя
        TaskManager.reg_start(self)              # регистрация запуска

        try:  # запуск фонового процесса catframes
            self._process_thread = CatframesProcess(self.command)
        
        except Exception as e:  # если возникла ошибка, обработает её
            self.handle_error(f'процесс не смог запуститься ({e})')
            return

        # запуск потока слежения за прогрессом
        threading.Thread(target=self._progress_watcher, daemon=True).start()

    # спрашивает о прогрессе, обновляет прогрессбар, обрабатывает завершение
    def _progress_watcher(self):
        progress: float = 0.0
        while progress < 1.0 and not self.stop_flag:          # пока прогрес не завершён
            time.sleep(0.2)
            progress = self._process_thread.get_progress()    # получить инфу от потока с процессом
            self.gui_callback.update(progress)                # через ручку коллбека обновить прогрессбар

            if self._process_thread.error_flag and not self.stop_flag:      # если процесс прервался не из-за юзера
                return self.handle_error('процесс завершился некорректно')  # обработает ошибку             
                
        # если всё завершилось корректно
        self.finish()  # обработает завершение

    # обработка ошибки процесса
    def handle_error(self, text):
        TaskManager.reg_finish(self)   # регистрация завершения
        self.gui_callback.set_error(   # сигнал об ошибке в ходе выполнения
            self.id,
            error=text
        )

    # обработка финиша задачи
    def finish(self):
        self.done = True  # ставит флаг завершения задачи
        TaskManager.reg_finish(self)       # регистрация завершения
        self.gui_callback.finish(self.id)  # сигнал о завершении задачи

    # остановка задачи
    def cancel(self):
        self.stop_flag = True
        TaskManager.reg_finish(self)
        self._process_thread.kill()        # убивает процесс
        self.gui_callback.delete(self.id)  # сигнал о завершении задачи

    def delete(self):
        TaskManager.wipe(self)
        self.gui_callback.delete(self.id)  # сигнал об удалении задачи


# выясняет у catframes, какого разрешения будет рендер
def find_resolution(task_config: TaskConfig) -> Tuple[int]:
    return 800, 500  # временно возвращает статическое разрешение
    # command = task_config.convert_to_resolution_command()
    # process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)

    # # поиск нужной строки в stdout процесса
    # pattern = r'Decision: [x0-9]+'
    # for line in io.TextIOWrapper(process.stdout):
    #     data = re.search(pattern, line)

    #     if data:  # когда нашёл, превращает "Decision: 123x234" в (123, 234)
    #         resolution = data.group().split()[1].split('x')
    #         return tuple(map(int, resolution))
    

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
    
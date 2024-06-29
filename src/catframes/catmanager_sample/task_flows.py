from _prefix import *


class GuiCallback:
    """Интерфейс для инъекции внешних методов от gui.
    Позволяет из задачи обновлять статус на слое gui."""

    def __init__(
            self,
            update_function,
            finish_function,
            ):
        self.update = update_function
        self.finish = finish_function
        
    
    @staticmethod  # метод из TaskBar
    def update(progress: float, delta: bool = False):
        """обновление полосы прогресса в окне"""
        ...

    @staticmethod  # метод из RootWindow
    def finish(task_number: int):
        """сигнал о завершении задачи"""
        ...


class Task:
    """Класс самой задачи, связывающейся с catframes"""

    all_tasks: dict = {}  # общий словарь для регистрации всех задач
    last_task_num: int = 0

    def __init__(self, **params) -> None:

        Task.last_task_num += 1
        self.number = Task.last_task_num  # получение уникального номера
        Task.all_tasks[self.number] = self  # регистрация в словаре

        self.done = False  # флаг завершённости
        self.stop_flag = False  # требование остановки

    # запуск задачи (тестовый)
    def start(self, gui_callback: GuiCallback):  # инъекция зависимости gui

        self.gui_callback = gui_callback

        # запуск фоновой задачи (дальше перепишется через subprocess)
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    # поток задачи (тестовый)
    def run(self):
        for i in range(21):
            if self.stop_flag:
                return
            self.gui_callback.update(i/20)
            time.sleep(0.2)
        self.done = True

    # остановка задачи (тестовая)
    def stop(self):
        self.stop_flag = True
        self.thread.join()
        self.gui_callback.finish(self.number)
        del Task.all_tasks[self.number]

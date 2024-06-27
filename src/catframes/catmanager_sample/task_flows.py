import time
import threading
from typing import Callable


class Task:
    all_tasks: dict = {}  # общий словарь для регистрации всех задач
    last_task_num: int = 0

    def __init__(self, master, **params) -> None:
        self.master = master

        Task.last_task_num += 1
        self.number = Task.last_task_num  # получение уникального номера
        Task.all_tasks[self.number] = self  # регистрация в словаре

        self.done = False  # флаг завершённости
        self.stop_flag = False  # требование остановки

    # запуск задачи (тестовый)
    def start(self, update_progress: Callable):
        # получение метода обновления полосы прогресса
        self.update_progress = update_progress

        # запуск фоновой задачи (дальше перепишется через subprocess)
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    # поток задачи (тестовый)
    def run(self):
        for i in range(101):
            if self.stop_flag:
                return
            self.update_progress(i/100)
            time.sleep(0.02)
        self.done = True

    # остановка задачи (тестовая)
    def stop(self):
        self.stop_flag = True
        self.thread.join()
        self.master.del_task_bar(self.number)
        del Task.all_tasks[self.number]

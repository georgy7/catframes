from task_flows import CatframesProcessThread
import os
import time


"""Проверка обработчика процесса для тестового api"""


run_dir = os.path.dirname(os.path.abspath(__file__))            # узнаёт екущую директорию
command = f'python {run_dir}/test_api/test_catframes_api.py'    # собирает команду запуска тестового api

process_thread = CatframesProcessThread(command)

# вытягивает прогресс
while True:
    time.sleep(0.5)
    print(process_thread.get_progress())

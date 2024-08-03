import time
from flask import Flask
from threading import Thread
from random import randint

# структура ответа
progress = {
    "phase": "encoding",
    "framesTotal": 1000,
    "framesEncoded": 0
}

# поток обновления прогресса
def update_progress():
    while progress["framesEncoded"] < progress["framesTotal"]:
        time.sleep(0.5)
        progress["framesEncoded"] += 50

# инициализация приложения
app = Flask('__main__')

# роут для апи
@app.route('/progress')
def get_progress():
    return progress

# запуск сервера с рандомным портом
def run_server():
    port = randint(5000, 6000)
    print('port:', port)  # отписывает порт в консоль
    app.run(port=port)


# запуск двух потоков, сервер - демоном (завершится сам, когда все остальные потоки завершатся)
Thread(target=update_progress).start()
Thread(target=run_server, daemon=True).start()

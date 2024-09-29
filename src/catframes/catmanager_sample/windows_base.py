from _prefix import *
from sets_utils import Settings
from task_flows import TaskManager


"""
Управление окнами происходит локальным менеджером окон.

Любое открытие окна происходит именно через него.
если окно уже прописано в его локальном словаре, 
оно не будет открыто повторно, будет возвращён его объект.

Если где угодно в коде нужно открыть/закрыть/сфокусировать
любое другое окно, через LocalWM можно получить его объект.
Также, можно получить список всех окон, например, для итерации.

WindowMixin - это абстрактный класс, от которого наследуются
все классы окон. В нём прописана базовая логика поведения окна.
Также, в нём есть инициализация стилей окна, и должны быть методы,
касающиеся пользовательских настроек, чтобы итерацией по всем окнам,
и вызове метода обновления для каждого окна, они применились везде.
К примеру, метод "update_texts" обновляет текст на всех виджетах окна.
"""



class LocalWM:
    """Класс для работы с окнами.
    Позволяет регистрировать окна,
    И управлять ими."""

    _all_windows: dict = {}  # общий словарь регистрации для окон

    # проверка, зарегистрировано ли окно
    @classmethod
    def check(cls, name: str) -> bool:
        return name in cls._all_windows

    # открытие окна
    @classmethod                                         # принимает класс окна, имя окна
    def open(cls, window_cls, name: str, master: Optional[Tk] = None, **kwargs) -> Tk:    
        if not cls.check('root'):                        # проверяем, есть ли или корневое окно
            return cls._reg(window_cls(), 'root')        # регистрируем окно как корневое

        if not master:                                   # если мастер не был передан
            master = cls.call('root')                    # мастером будет корневое окно

        if not cls.check(name):                          # проверяем, зарегистрировано ли окно
            window = window_cls(root=master, **kwargs)   # создаём окно, передаём мастера
            cls._reg(window, name)                       # регистрируем окно
        return cls.call(name)
    

    # регистрация окна
    @classmethod
    def _reg(cls, window: Tk, name: str = None) -> None:
        if not name:  
            name = window.name
        if not cls.check(name):
            cls._all_windows[name] = window
        return window

    # получение окна
    @classmethod
    def call(cls, name: str) -> Optional[Tk]:
        if cls.check(name):
            return cls._all_windows[name]

    # удаление окна
    @classmethod
    def wipe(cls, name: str) -> None:
        if cls.check(name):
            cls._all_windows.pop(name)

    # получение списка всех окон
    @classmethod
    def all(cls) -> list:
        return list(cls._all_windows.values())
    
    # переключение фокуса на окно
    @classmethod
    def focus(cls, name: str) -> None:
        if cls.check(name):
            cls._all_windows[name].focus()

    # обновление открытых окон после завершения задачи
    @classmethod
    def update_on_task_finish(cls):
        if cls.check('warn') and not TaskManager.running_list():
            cls._all_windows['warn'].destroy()
            cls._all_windows.pop('warn')
        ...
    

class WindowMixin(ABC):
    """Абстрактный класс.
    Упрощает конструкторы окон."""

    title: Tk.wm_title        # эти атрибуты и методы объекта
    protocol: Tk.wm_protocol  # появятся автоматически при
    destroy: Tk.destroy       # наследовании от Tk или Toplevel

    size: Tuple[int, int]     # размеры (ширина, высота) окна
    name: str                 # имя окна для словаря всех окон
    widgets: Dict[str, ttk.Widget]  # словарь виджетов окна

    # настройка окна, вызывается через super в конце __init__ окна
    def _default_set_up(self):
        self.protocol("WM_DELETE_WINDOW", self.close)  # что выполнять при закрытии

        self._set_size()     # настройка внешнего вида окна
        self._to_center()     # размещение окна в центре экрана
        if self.name == 'root':
            Settings.theme.lazy_init(master=self)
        self.after(1, self._init_widgets)  # создание виджетов
        self.after(2, self.update_texts)   # установка текста нужного языка
        self.after(3, self._pack_widgets)  # расстановка виджетов

    # закрытие окна
    def close(self) -> None:
        # удаляет регистрацию окна из менеджера
        LocalWM.wipe(self.name)
        self.destroy()  # закрывает окно

    # обновление текстов всех виджетов окна, исходя из языка
    def update_texts(self) -> None:
        self.title(Settings.lang.read(f'{self.name}.title'))

        for w_name, widget in self.widgets.items():

            if w_name.startswith('_'):  # если виджет начинается с "_", его обходит
                continue

            new_text_data = Settings.lang.read(f'{self.name}.{w_name}')

            if w_name.startswith('cmb'): # если виджет это комбобокс
                widget.config(values=new_text_data)   
                widget.current(newindex=0)   
                continue    
            
            widget.config(text=new_text_data)

    # размещение окна в центре экрана (или родительского окна)
    def _to_center(self) -> None:
        border_gap = 30  # минимальный отступ от края окна при открытии

        screen_size = self.winfo_screenwidth(), self.winfo_screenheight()

        # если это не побочное окно, то размещаем по центру экрана
        if not isinstance(self, Toplevel):
            x = (screen_size[0] - self.size[0]) / 2
            y = (screen_size[1] - self.size[1]) / 2
            self.geometry(f'+{int(x)}+{int(y)}')
            return

        # далее для побочных окон:
        master_size = self.master.winfo_width(), self.master.winfo_height()
        x = self.master.winfo_x() + master_size[0]/2 - self.size[0]/2  # размещаем по центру
        y = self.master.winfo_y() + master_size[1]/2 - self.size[1]/2  # главного окна

        # если окно вышло за левый край экрана
        if x < border_gap:  
            x = border_gap

        # если окно вышло за правый край экрана
        if x+self.size[0]+border_gap > screen_size[0]:
            x = screen_size[0]-self.size[0]-border_gap

        # если окно вышло за верхнюю границу
        if y < border_gap:  
            y = border_gap

        # если окно вышло за низнюю границу экрана
        if y+self.size[1]+(border_gap*3) > screen_size[1]:  # отступ больше в три раза, 
            y = screen_size[1]-self.size[1]-(border_gap*3)  # учитывая панель задач или dock

        self.geometry(f'+{int(x)}+{int(y)}')

    def _set_size(self):

        x, y = self.size                   # забираем объявленные размеры окна
        self.geometry(f'{x}x{y}')          # и присваиваем их окну
        self.minsize(x, y)                 # и устанавливаем как минимальные
        try:
            x, y = self.size_max               # если есть максимальные размеры
            self.maxsize(x, y)
        except AttributeError:
            pass



    # метод для создания и настройки виджетов
    @abstractmethod
    def _init_widgets(self) -> None:
        ...

    # метод для расположения виджетов
    @abstractmethod
    def _pack_widgets(self, ) -> None:
        ...

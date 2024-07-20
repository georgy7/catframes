from _prefix import *
from sets_utils import Lang
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
    @classmethod
    def open(cls, window_cls, name: str) -> Tk:    # принимает класс окна, имя окна
        if not cls.check('root'):                        # проверяем, есть ли корневое окно
            return cls._reg(window_cls(), 'root')        # регистрируем окно как корневое

        if not cls.check(name):                          # проверяем, зарегистрировано ли окно
            window = window_cls(root=cls.call('root'))   # создаём окно, передаём корневое окно
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

    title: Tk.title         # эти атрибуты и методы объекта
    protocol: Tk.protocol   # появятся автоматически при
    destroy: Tk.destroy     # наследовании от Tk или Toplevel

    size: Tuple[int, int]   # размеры (ширина, высота) окна
    name: str               # имя окна для словаря всех окон
    widgets: Dict[str, ttk.Widget]  # словарь виджетов окна

    # настройка окна, вызывается через super в конце __init__ окна
    def _default_set_up(self):
        self.protocol("WM_DELETE_WINDOW", self.close)  # что выполнять при закрытии

        self._set_style()     # настройка внешнего вида окна
        self._to_center()     # размещение окна в центре экрана
        self._init_widgets()  # создание виджетов
        self.update_texts()   # установка текста нужного языка
        self._pack_widgets()  # расстановка виджетов

    # закрытие окна
    def close(self) -> None:
        # удаляет регистрацию окна из менеджера
        LocalWM.wipe(self.name)
        self.destroy()  # закрывает окно

    # обновление текстов всех виджетов окна, исходя из языка
    def update_texts(self) -> None:
        self.title(Lang.read(f'{self.name}.title'))

        for w_name, widget in self.widgets.items():

            if w_name.startswith('_'):  # если виджет начинается с "_", его обходит
                continue

            new_text_data = Lang.read(f'{self.name}.{w_name}')

            if w_name.startswith('cmb'): # если виджет это комбобокс
                if new_text_data == '-----':
                    new_text_data = ('-----',)
                widget.config(values=new_text_data)   
                widget.current(newindex=0)   
                continue    
            
            widget.config(text=new_text_data)

    # размещение окна в центре экрана (или родительского окна)
    def _to_center(self) -> None:

        # если это побочное окно
        if isinstance(self, Toplevel):
            x = self.master.winfo_x() + self.master.winfo_width()/2 - self.size[0]/2  # размещаем по центру
            y = self.master.winfo_y() + self.master.winfo_height()/2 - self.size[1]/2  # главного окна

        # а если это главное окно    
        else:  # размещаем по центру экрана
            x = (self.winfo_screenwidth() - self.size[0]) / 2
            y = (self.winfo_screenheight() - self.size[1]) / 2

        self.geometry(f'+{int(x)}+{int(y)}')


    # настройка стиля окна, исходя из разрешения экрана
    def _set_style(self) -> None:

        # screen_height = self.winfo_screenheight()  # достаём высоту экрана
        # scale = (screen_height/540)                # индекс масштабирования
        # scale *= MAJOR_SCALING                     # домножаем на глобальную

        style=ttk.Style()
        # if TTK_THEME: style.theme_use(TTK_THEME)   # применение темы, если есть
        _font = font.Font(
            # family= "helvetica", 
            size=12, 
            weight='bold'
        )
        style.configure(style='.', font=_font)  # шрифт текста в кнопке
        self.option_add("*Font", _font)  # шрифты остальных виджетов

        # task_background = '#94d0eb'
        task_background = '#c4f0ff'
        style.configure('Task.TFrame', background=task_background)
        style.configure('Task.TLabel', background=task_background)
        style.configure('Task.Horizontal.TProgressbar', background=task_background)

        x, y = self.size                   # забираем объявленные размеры окна
        # x, y = int(x*scale), int(y*scale)  # масштабируем их
        self.geometry(f'{x}x{y}')          # и присваиваем их окну
        self.minsize(x, y)                 # и устанавливаем как минимальные
        try:
            x, y = self.size_max               # если есть максимальные размеры
            # x, y = int(x*scale), int(y*scale)  # масштабируем их
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

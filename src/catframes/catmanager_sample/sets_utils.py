from _prefix import *


"""
Класс языковых настроек содержит большой словарь, 
в котором для каждого языка есть соответсвия названия
виджета, и текста, который в этом виджете расположен.

Добавление нового ключа в этот словарь должно быть с
добавлением всех внутренних ключей по аналогии с другими.

Если в процессе будет допущена ошибка, или gui запросит
текст для виджета, который не прописан, в качестве текста
вернётся строка из прочерков "-----" для быстрого обнаружения. 
"""


class Lang:
    """Класс языковых настроек.
    Позволяет хранить текущий язык,
    И извлекать его текстовики.

    При добавлении новых языков в словарь data,
    их названия будут сами подтягиваться в поле настроек.
    """

    current_name = 'english'
    current_index = 0

    data = {  # языковые теги (ключи) имеют вид: "область.виджет"
        'english': {
            'root.title': 'CatFrames',
            'root.lbTest': 'Label 1',
            'root.openSets': 'Settings',
            'root.newTask': 'New task',

            'bar.active': 'processing',
            'bar.inactive': 'complete', 
            'bar.btInfo': 'Info',
            'bar.btCancel': 'Cancel',
            'bar.btDelete': 'Delete',

            'sets.title': 'Settings',
            'sets.lbLang': 'Language:',
            'sets.lbPortRange': 'System ports range:',
            'sets.btApply': 'Apply',
            'sets.btSave': 'Save',

            'task.title': 'New Task',
            'task.lbColor': 'Background:',
            'task.lbFramerate': 'Framerate:',
            'task.lbQuality': 'Quality:',
            'task.cmbQuality': ('high', 'medium', 'poor'),
            'task.btCreate': 'Create',

            'dirs.lbDirList': 'List of source directories:',
            'dirs.btAddDir': 'Add',
            'dirs.btRemDir': 'Remove',

            'warn.title': 'Warning',
            'warn.lbWarn': 'Warning!',
            'warn.lbText': 'Incomplete tasks!',
            'warn.btBack': 'Back',
            'warn.btExit': 'Leave',

            'noti.title': 'Error',
            'noti.lbWarn': 'Invalid port range!',
            'noti.lbText': 'The acceptable range is from 10240 to 65025',
            'noti.lbText2': 'The number of ports is at least 100'
        },
        'русский': {
            'root.title': 'CatFrames',
            'root.lbTest': 'Строка 1',
            'root.openSets': 'Настройки',
            'root.newTask': 'Новая задача',

            'bar.lbActive': 'обработка',
            'bar.lbInactive': 'завершено', 
            'bar.btInfo': 'Инфо',
            'bar.btCancel': 'Отмена',
            'bar.btDelete': 'Удалить',

            'sets.title': 'Настройки',
            'sets.lbLang': 'Язык:',
            'sets.lbPortRange': 'Диапазон портов системы:',
            'sets.btApply': 'Применить',
            'sets.btSave': 'Сохранить',

            'task.title': 'Новая задача',
            'task.lbColor': 'Цвет фона:',
            'task.lbFramerate': 'Частота кадров:',
            'task.lbQuality': 'Качество:',
            'task.cmbQuality': ('высокое', 'среднее', 'низкое'),
            'task.btCreate': 'Создать',

            'dirs.lbDirList': 'Список директорий источников:',
            'dirs.btAddDir': 'Добавить',
            'dirs.btRemDir': 'Удалить',
            
            'warn.title': 'Внимание',
            'warn.lbWarn': 'Внимание!',
            'warn.lbText': 'Задачи не завершены!',
            'warn.btBack': 'Назад',
            'warn.btExit': 'Выйти',

            'noti.title': 'Ошибка',
            'noti.lbWarn': 'Неверный диапазон портов!',
            'noti.lbText': 'Допустимы значения от 10240 до 65025',
            'noti.lbText2': 'Количество портов не менее 100'
        },
    }

    @staticmethod  # получение всех доступных языков
    def get_all() -> tuple:
        return tuple(Lang.data.keys())

    @staticmethod  # установка языка по имени или индексу
    def set(name: str = None, index: int = None) -> None:

        if name and name in Lang.data:
            Lang.current_index = Lang.get_all().index(name)
            Lang.current_name = name

        elif isinstance(index, int) and 0 <= index < len(Lang.data):
            Lang.current_name = Lang.get_all()[index]
            Lang.current_index = index

    @staticmethod  # получение текста по тегу
    def read(tag) -> Union[str, tuple]:
        try:
            return Lang.data[Lang.current_name][tag]
        except KeyError:  # если тег не найден
            return '-----'
            

class PortSets:
    """Класс настроек диапазона портов
    системы для связи с ffmpeg."""

    min_port: int = 10240
    max_port: int = 65535

    @classmethod
    def set_range(cls, min_port: int, max_port: int) -> None:
        cls.min_port = min_port
        cls.max_port = max_port

    @classmethod
    def get_range(cls) -> Tuple:
        return cls.min_port, cls.max_port
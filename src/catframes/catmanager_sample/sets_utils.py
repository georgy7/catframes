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
            'root.openSets': 'Settings',
            'root.newTask': 'Create',

            'bar.active': 'processing',
            'bar.inactive': 'complete', 
            'bar.btInfo': 'Info',
            'bar.btCancel': 'Cancel',
            'bar.btDelete': 'Delete',
            'bar.lbEmpty': 'Your projects will appear here',
            'bar.error.noffmpeg': 'Error! FFmpeg not found!',
            'bar.error.nocatframes': 'Error! Catframes not found!',
            'bar.error.internal': 'Internal process error!',
            'bar.error.failed': 'Error! Process start failed!',
            'bar.lbQuality': 'Quality:',
            'bar.lbFramerate': 'Framerate:',
            'bar.lbColor': 'Color:',

            'sets.title': 'Settings',
            'sets.lbLang': 'Language:',
            'sets.lbPortRange': 'System ports range:',
            'sets.btApply': 'Apply',
            'sets.btSave': 'Save',

            'task.title': 'New Task',
            'task.title.view': 'Task settings view',
            'task.initText': 'Add a directory\nof images',
            'task.lbColor': 'Background:',
            'task.lbFramerate': 'Framerate:',
            'task.lbQuality': 'Quality:',
            'task.cmbQuality': ('high', 'medium', 'poor'),
            'task.lbResolution': 'Render resolution:',
            'task.lbSaveAs': 'Save as:',
            'task.btCreate': 'Create',
            'task.btPathChoose': 'choose',
            'task.lbCopy': 'Сli command:',
            'task.btCopy': 'Copy',

            'dirs.lbDirList': 'List of source directories:',
            'dirs.btAddDir': 'Add',
            'dirs.btRemDir': 'Remove',
            'dirs.DirNotExists': "Doesn't exists. Removing...",

            'warn.title': 'Warning',
            'warn.lbWarn': 'Warning!',
            'warn.lbText': 'Incomplete tasks!',
            'warn.btBack': 'Back',
            'warn.btExit': 'Leave',

            'noti.title': 'Error',
            'noti.lbWarn': 'Invalid port range!',
            'noti.lbText': 'The acceptable range is from 10240 to 65025',
            'noti.lbText2': 'The number of ports is at least 100',
            
        },
        'русский': {
            'root.title': 'CatFrames',
            'root.openSets': 'Настройки',
            'root.newTask': 'Создать',

            'bar.lbActive': 'обработка',
            'bar.lbInactive': 'завершено', 
            'bar.btInfo': 'Инфо',
            'bar.btCancel': 'Отмена',
            'bar.btDelete': 'Удалить',
            'bar.lbEmpty': 'Здесь появятся Ваши проекты',
            'bar.error.noffmpeg': 'Ошибка! FFmpeg не найден!',
            'bar.error.nocatframes': 'Ошибка! Catframes не найден!',
            'bar.error.internal': 'Внутренняя ошибка процесса!',
            'bar.error.failed': 'Ошибка при старте процесса!',
            'bar.lbQuality': 'Качество:',
            'bar.lbFramerate': 'Частота:',
            'bar.lbColor': 'Цвет:',

            'sets.title': 'Настройки',
            'sets.lbLang': 'Язык:',
            'sets.lbPortRange': 'Диапазон портов системы:',
            'sets.btApply': 'Применить',
            'sets.btSave': 'Сохранить',

            'task.title': 'Новая задача',
            'task.title.view': 'Просмотр настроек задачи',
            'task.initText': 'Добавьте папку\nс изображениями',
            'task.lbColor': 'Цвет фона:',
            'task.lbFramerate': 'Частота кадров:',
            'task.lbQuality': 'Качество:',
            'task.cmbQuality': ('высокое', 'среднее', 'низкое'),
            'task.lbResolution': 'Разрешение рендера:',
            'task.lbSaveAs': 'Сохранить как:',
            'task.btCreate': 'Создать',
            'task.btPathChoose': 'выбрать',
            'task.lbCopy': 'Команда cli:',
            'task.btCopy': 'Копировать',

            'dirs.lbDirList': 'Список директорий источников:',
            'dirs.btAddDir': 'Добавить',
            'dirs.btRemDir': 'Удалить',
            'dirs.DirNotExists': 'Не существует. Удаление...',
            
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
    max_port: int = 65000

    @classmethod
    def set_range(cls, min_port: int, max_port: int) -> None:
        cls.min_port = min_port
        cls.max_port = max_port

    @classmethod
    def get_range(cls) -> Tuple:
        return cls.min_port, cls.max_port
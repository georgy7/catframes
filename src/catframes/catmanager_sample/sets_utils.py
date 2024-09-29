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
            'task.lbCopy': 'Copy cli:',
            'task.btCopyBash': 'Bash',
            'task.btCopyWin': 'Win',

            'dirs.lbDirList': 'List of source directories:',
            'dirs.btAddDir': 'Add',
            'dirs.btRemDir': 'Remove',
            'dirs.DirNotExists': "Doesn't exists. Removing...",

            'warn.exit.title': 'Warning',
            'warn.exit.lbWarn': 'Warning!',
            'warn.exit.lbText': 'Incomplete tasks!',
            'warn.exit.btAccept': 'Leave',
            'warn.exit.btDeny': 'Back',

            'warn.cancel.title': 'Warning',
            'warn.cancel.lbWarn': 'Are you sure',
            'warn.cancel.lbText': 'You want to cancel the task?',
            'warn.cancel.btAccept': 'Yes',
            'warn.cancel.btDeny': 'Back',

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
            'task.lbCopy': 'Копировать cli:',
            'task.btCopyBash': 'Bash',
            'task.btCopyWin': 'Win',

            'dirs.lbDirList': 'Список директорий источников:',
            'dirs.btAddDir': 'Добавить',
            'dirs.btRemDir': 'Удалить',
            'dirs.DirNotExists': 'Не существует. Удаление...',
            
            'warn.exit.title': 'Внимание',
            'warn.exit.lbWarn': 'Внимание!',
            'warn.exit.lbText': 'Задачи не завершены!',
            'warn.exit.btAccept': 'Выйти',
            'warn.exit.btDeny': 'Назад',

            'warn.cancel.title': 'Внимание',
            'warn.cancel.lbWarn': 'Вы уверены,',
            'warn.cancel.lbText': 'Что хотите отменить задачу?',
            'warn.cancel.btAccept': 'Да',
            'warn.cancel.btDeny': 'Назад',

            'noti.title': 'Ошибка',
            'noti.lbWarn': 'Неверный диапазон портов!',
            'noti.lbText': 'Допустимы значения от 10240 до 65025',
            'noti.lbText2': 'Количество портов не менее 100'
        },
    }

    def __init__(self):
        self.current_name = 'english'
        self.current_index = 0

    # получение всех доступных языков
    def get_all(self) -> tuple:
        return tuple(Lang.data.keys())

    # установка языка по имени или индексу
    def set(self, name: str = None, index: int = None) -> None:

        if name and name in Lang.data:
            self.current_index = self.get_all().index(name)
            self.current_name = name

        elif isinstance(index, int) and 0 <= index < len(Lang.data):
            self.current_name = self.get_all()[index]
            self.current_index = index

    # получение текста по тегу
    def read(self, tag: str) -> Union[str, tuple]:
        try:
            return Lang.data[self.current_name][tag]
        except KeyError:  # если тег не найден
            return '-----'


class IniConfig:
    """Создание, чтение, и изменение внешнего файла конфига"""

    def __init__(self):
        self.file_path = os.path.join(
            os.path.expanduser('~'), CONFIG_FILENAME
        )

        self.config = configparser.ConfigParser()

        if not os.path.isfile(self.file_path):
            self.set_default()
        self.config.read(self.file_path)            

    # создание стандартного конфиг файла
    def set_default(self):
        self.config['Settings'] = {
            'Language': 'english',
            'UseSystemPath': 'yes',
            'TtkTheme': 'default'
        }
        self.config['AbsolutePath'] = {
            'Python': '',
            'FFmpeg': '',
            'Catframes': '',
        }
        self.save()

    # редактирование ключа в секции конфиг файла
    def update(self, section: str, key: str, value: Union[str, int]):
        if section in self.config:
            self.config[section][key] = value
    
    def save(self):
        with open(self.file_path, 'w') as configfile:
            self.config.write(configfile)


class Settings:
    """Содержит объекты всех классов настроек"""

    lang = Lang()
    conf = IniConfig()

    @classmethod
    def save(cls):
        cls.conf.update('Settings', 'Language', cls.lang.current_name)
        cls.conf.save()

    @classmethod
    def restore(cls):
        cls.lang.set(cls.conf.config['Settings']['Language'])

Settings.restore()

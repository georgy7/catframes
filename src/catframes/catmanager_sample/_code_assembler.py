import os


"""
Эта внутренняя утилита собирает все модули в один большой файл.

Все внешние импорты в модулях желательно пробрасывать через _prefix.py.
То есть, прописывать их там, а уже оттуда импортировать в нужный модуль.
В дальнейшем, это избавит от необходимости искать потеряные импорты.

Все косвенные импорты обязательно прописывать без псевдонимов, то есть:
"from window_utils import WindowMixin"          - так нужно делать.
"from window_utils import WindowMixin as wm"    - так не нужно.
Все импорты модулей игнорируются, а значит, эти элиасы работать не будут.

Если появляются новые модули, помимо указаных в FILE_NAMES, 
нужно проследить порядок импортов, и в таком же порядке дописать их, 
чтобы объекты и конструкции объявлялись выше точек их использования.
"""


DIRECTORY = "src/catframes/catmanager_sample"  # путь к сборочным файлам
OUTPUT_FILE = "src/catframes/catmanager.py"  # путь к выходному файлу

FILE_NAMES = [  # порядок файлов для сборки
    "sets_utils.py",
    "task_flows.py",
    "windows_base.py",
    "windows_utils.py",
    "windows.py",
    "util_checker.py",
    "main.py",
]


# сборка всех строк кода, есть флаг игнорирования строк импортов
def collect_code(file_path, ignore_imports: bool) -> list:
    code_lines = []
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            # если стоит флаг, то игнорируем строки с импортами
            if ignore_imports:
                if line.strip().startswith("import ") or line.strip().startswith(
                    "from "
                ):
                    continue
            code_lines.append(line)

    return code_lines


# запись всех строк кода в файл
def write_to_file(output_file: str, code_lines: list) -> None:
    with open(output_file, "w", encoding="utf-8") as f:
        f.writelines(code_lines)


def main():

    # добавление в начало строк из префикса
    all_code_lines = collect_code(
        os.path.join(DIRECTORY, "_prefix.py"),  # сборка пути и имени файла
        ignore_imports=False,  # импорты не игнорируются
    )

    for fn in FILE_NAMES:
        all_code_lines += ["\n"] * 2  # строки отступов
        all_code_lines += f"\n    #  из файла {fn}:"

        all_code_lines += collect_code(
            os.path.join(DIRECTORY, fn),  # сборка пути и имени файла
            ignore_imports=True,  # теперь импорты игнорируются
        )

        all_code_lines += ["\n"] * 2  # строки отступов

    write_to_file(OUTPUT_FILE, all_code_lines)  # создание выходного файла


if __name__ == "__main__":
    main()

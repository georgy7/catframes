#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from subprocess import run, CompletedProcess
from dataclasses import dataclass
from functools import partial
from typing import Callable, Union, List
import shutil


@dataclass
class QualityGate:
    """A quality gate and its result (ok field).
    Optional quality gates do not affect the script exit code.
    """
    name: str
    optional: bool
    code: Callable[[], bool]
    ok: Union[bool, None] = None


def run_gate(cg: QualityGate):
    assert None == cg.ok
    print()
    print('=' * 27)
    print('== Starting...')
    print('== ' + cg.name)
    print('=' * 27)
    print()
    cg.ok = cg.code()
    print(cg.name + ': ' + ('OK' if cg.ok else 'FAILED'))
    print('\n')


def is_command_ok(args: List[str]) -> bool:
    r: CompletedProcess = run(args, capture_output=True, text=True)
    print(r.stdout)
    print(r.stderr)
    return 0 == r.returncode


def is_types_ok(folder: str) -> bool:
    if not shutil.which('mypy'):
        print('mypy not found\n')
        return False
    return is_command_ok([
        'mypy', '--config-file', os.path.join(folder, 'pyproject.toml'), folder
    ])


def has_console() -> bool:
    return (sys.stdin is not None) and sys.stdin.isatty()


def check_pil():
    try:
        from PIL import Image
    except:
        print('Warning: Pillow not found!')


def check_tkinter():
    try:
        from tkinter import ttk
    except:
        print('Warning: Tkinter not found!')


def main() -> None:
    if not has_console():
        sys.exit(1)

    version = sys.version_info
    if (version[0] < 3) or ((3 == version[0]) and (version[1] < 7)):
        print('Python 3.7 or later required.')
        print('It does not make any sense to test it on earlier versions.')
        sys.exit(400)

    print()
    check_pil()
    check_tkinter()

    python: str = sys.executable
    here: str = os.path.dirname(os.path.realpath(sys.argv[0]))
    modules: str = os.path.join(here, 'src', 'catframes')

    test_args: List[str] = [python, '-m', 'unittest', 'discover', modules, '-p']

    quality_gates: List[QualityGate] = [
        QualityGate(
            name='Catframes unit tests',
            optional=False,
            code=partial(is_command_ok, test_args + ['catframes.py']),
        ),
        QualityGate(
            name='Catmanager unit tests',
            optional=False,
            code=partial(is_command_ok, test_args + ['catmanager.py']),
        ),
        QualityGate(
            name='Type checking',
            optional=(not shutil.which('mypy')),
            code=partial(is_types_ok, here),
        )
    ]

    for cg in quality_gates:
        run_gate(cg)


if __name__ == "__main__":
    main()

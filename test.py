#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from subprocess import run, CompletedProcess
from dataclasses import dataclass
from functools import partial
from typing import Callable, Union, List
import shutil
import subprocess


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
    assert cg.ok is None
    print()
    print('=' * 27)
    print('== Starting...')
    print('== ' + cg.name)
    print('=' * 27)
    print()
    cg.ok = cg.code()
    print(cg.name + ': ' + ('OK' if cg.ok else 'FAILED'))
    print('\n')


def run_gates(cgs: List[QualityGate]):
    for cg in cgs:
        run_gate(cg)


def have_been_successful(quality_gates: List[QualityGate]):
    return all(cg.ok for cg in quality_gates if not cg.optional)


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
    except ImportError:
        print('Error: Pillow not found!')
        sys.exit(400)


def check_tkinter():
    try:
        from tkinter import ttk
    except ImportError:
        print('Warning: Tkinter not found!')


def print_summary(quality_gates: List[QualityGate]) -> bool:
    print()
    print('-' * 40)
    print('Summary')
    print('-' * 40)

    for cg in quality_gates:
        status = 'OK' if cg.ok else 'FAILED' + (' (optional)' if cg.optional else '')
        print('{0: <23}'.format(cg.name + ': ') + status)

    print('-' * 40)

    everything_ok: bool = have_been_successful(quality_gates)
    print('Result' + ': ' + ('OK\n' if everything_ok else 'FAILED\n'))
    return everything_ok


def main() -> None:
    if not has_console():
        sys.exit(400)

    version = sys.version_info
    if (version[0] < 3) or ((3 == version[0]) and (version[1] < 7)):
        print('Python 3.7 or later required.')
        print('It does not make any sense to test it on earlier versions.')
        sys.exit(400)

    print()
    check_pil()
    # check_tkinter()

    python: str = sys.executable
    here: str = os.path.dirname(os.path.realpath(sys.argv[0]))
    modules: str = os.path.join(here, 'src', 'catframes')

    test_args: List[str] = [python, '-m', 'unittest', 'discover', modules, '-p']
    cat_args: List[str] = [python, os.path.join(modules, 'catframes.py')]

    basic_common: List[QualityGate] = [
        QualityGate(
            name='Catframes unit tests',
            optional=False,
            code=partial(is_command_ok, test_args + ['catframes.py']),
        ),
        QualityGate(
            name='Type checking',
            optional=(not shutil.which('mypy')),
            code=partial(is_types_ok, here),
        ),
        QualityGate(
            name='Smoke test',
            optional=False,
            code=partial(is_command_ok, cat_args + ['--help']),
        )
    ]

    basic_ui: List[QualityGate] = [
        QualityGate(
            name='Catmanager unit tests',
            optional=False,
            code=partial(is_command_ok, test_args + ['catmanager.py']),
        )
    ]

    further_cli: List[QualityGate] = [
    ]

    # run_gates(basic_ui)
    run_gates(basic_common)

    if not have_been_successful(basic_common):
        print('\nBasic CLI tests failed. Further testing is pointless.')
        # print_summary(basic_ui + basic_common)
        print_summary(basic_common)
        sys.exit(1)

    if not shutil.which('ffmpeg'):
        # print_summary(basic_ui + basic_common)
        print_summary(basic_common)
        print('Could not continue: FFmpeg not found.\n')
        sys.exit(450)

    python_executable = sys.executable
    this_folder = os.path.dirname(os.path.normpath(__file__))

    subprocess.run([
        python_executable,
        os.path.join(this_folder, 'utils', 'gen_images.py'),
        os.path.join(this_folder, 'DATA')
    ], check=True)

    run_gates(further_cli)

    # ok: bool = print_summary(basic_ui + basic_common + further_cli)
    ok: bool = print_summary(basic_common + further_cli)

    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()

from _prefix import *


def has_console() -> bool:
    return (sys.stdin is not None) and sys.stdin.isatty()


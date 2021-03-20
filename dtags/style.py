import sys
from pathlib import Path
from typing import Optional, Set

TTY = sys.stdout.isatty()

BLUE = "\033[38;5;39m"
RED = "\033[38;5;009m"
GREEN = "\033[38;5;154m"
BOLD = "\033[1m"
CLEAR = "\033[0m"

TAG_PREFIX = "@"
CMD_PREFIX = "$"


def command(value: str, tty: bool = TTY) -> str:
    return f"{BOLD}{CMD_PREFIX} {value}{CLEAR}" if tty else f"{CMD_PREFIX} {value}"


def path(value: Path, tty: bool = TTY) -> str:
    return f"{BLUE}{value.as_posix()}{CLEAR}" if tty else value.as_posix()


def tag(value: str, tty: bool = TTY) -> str:
    return f"{BOLD}{TAG_PREFIX}{CLEAR}{value}" if tty else f"{TAG_PREFIX}{value}"


def mapping(dirpath: Path, tags: Set[str], tty: bool = TTY) -> str:
    buffer = [path(dirpath)]
    if tty:
        buffer.extend(f"{BOLD}{TAG_PREFIX}{CLEAR}{t}" for t in sorted(tags))
    else:
        buffer.extend(f"{TAG_PREFIX}{t}" for t in sorted(tags))

    return " ".join(buffer)


def diff(
    dirpath: Path,
    add_tags: Optional[Set[str]] = None,
    del_tags: Optional[Set[str]] = None,
    tty: bool = TTY,
) -> str:
    buffer = [path(dirpath)]
    if add_tags:
        if tty:
            buffer.extend(f"{GREEN}+{TAG_PREFIX}{t}{CLEAR}" for t in sorted(add_tags))
        else:
            buffer.extend(f"+{TAG_PREFIX}{t}" for t in sorted(add_tags))

    if del_tags:
        if tty:
            buffer.extend(f"{RED}-{TAG_PREFIX}{t}{CLEAR}" for t in sorted(del_tags))
        else:
            buffer.extend(f"-{TAG_PREFIX}{t}" for t in sorted(del_tags))

    return " ".join(buffer)

import os
import sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from distutils.util import strtobool
from functools import wraps
from pathlib import Path
from typing import Callable, Dict, List, Optional, Set

from pkg_resources import get_distribution
from slugify import slugify

from dtags.exceptions import DtagsError

is_windows = os.name == "nt"
is_mingw = is_windows and bool(os.environ.get("DTAGS_GIT_BASH"))

DtagsCommandType = Callable[[Optional[List[str]]], None]


def fix_color_for_windows() -> None:  # pragma no cover
    if is_windows:
        os.system("")


def dtags_command(func: DtagsCommandType) -> DtagsCommandType:
    @wraps(func)
    def wrapped(args: Optional[List[str]] = None) -> None:
        try:
            fix_color_for_windows()
            func(args)
        except DtagsError as err:
            print(str(err), file=sys.stderr)
            sys.exit(1)

        except KeyboardInterrupt:  # pragma no cover
            print()
            sys.exit(130)

    return wrapped


def get_argparser(prog: str, desc: str, usage: str) -> ArgumentParser:
    parser = ArgumentParser(
        prog=prog,
        description=desc,
        usage=usage,
        formatter_class=RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=get_distribution("dtags").version,
        help="show version",
    )
    return parser


def get_mingw_path(value: str) -> Optional[Path]:  # pragma no cover
    """Sanitize paths with MINGW mounted drives. Example: /c/... -> c:/..."""
    if (
        is_mingw
        and len(value) >= 3
        and value[0] == value[2] == "/"
        and value[1].isalpha()
    ):
        path = Path(f"{value[1]}:{value[2:]}")
        if path.is_dir():
            return path.resolve()
    return None


def prompt_user() -> bool:  # pragma no cover
    while True:
        print("\nApply changes? [y/n] ", end="")
        try:
            return strtobool(input().lower())
        except ValueError:
            print('Please respond with "y" or "n"')


def reverse_map(config: Dict[Path, Set[str]]) -> Dict[str, Set[Path]]:
    result: Dict[str, Set[Path]] = {}

    for dirpath, tags in config.items():
        for tag in tags:
            if tag in result:
                result[tag].add(dirpath)
            else:
                result[tag] = {dirpath}

    return result


def normalize_dir(value: str) -> Optional[Path]:
    path = Path(value).expanduser()
    return path.resolve() if path.is_dir() else get_mingw_path(value)


def normalize_dirs(values: Optional[List[str]]) -> Set[Path]:
    return set() if not values else set(d for d in map(normalize_dir, values) if d)


def normalize_tag(value: str) -> str:
    return slugify(value, lowercase=False, regex_pattern=r"[^-a-zA-Z0-9]+")


def normalize_tags(values: Optional[List[str]]) -> Set[str]:
    return set() if not values else set(t for t in map(normalize_tag, values) if t)

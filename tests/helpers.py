import re
from typing import List

from dtags.files import COMP_FILE, DEST_FILE, get_file_path

ANSI_ESCAPE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")


def clean_str(value: str) -> str:
    return ANSI_ESCAPE.sub("", value)


def load_completion() -> List[str]:
    with open(get_file_path(COMP_FILE)) as fp:
        return sorted(tag for tag in fp.read().split(" ") if tag)


def load_destination() -> str:
    with open(get_file_path(DEST_FILE)) as fp:
        return fp.read().strip()

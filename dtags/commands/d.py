import sys
from pathlib import Path
from typing import List, Optional

from dtags import style
from dtags.commons import dtags_command, get_argparser
from dtags.exceptions import DtagsError
from dtags.files import load_config_file, save_destination_file

USAGE = "d [-t] DEST"
DESCRIPTION = f"""
Change directory by path or tag.

Tag names are automatically slugified (e.g "foo bar" to "foo-bar").
Paths take precedence over tags on name collisions.

examples:

  # change directory by path
  {style.command("d /home/user/foo")}

  # change directory by tag
  {style.command("d my-tag")}

  # use -t/--tag to always interpret the argument as a tag
  {style.command("d -t foo")}
"""


@dtags_command
def execute(args: Optional[List[str]] = None) -> None:
    parser = get_argparser(prog="d", desc=DESCRIPTION, usage=USAGE)
    parser.add_argument(
        "destination",
        metavar="DEST",
        help="directory path or tag",
    )
    parser.add_argument(
        "-t",
        "--tag",
        action="store_true",
        dest="tag",
        help="assume the argument is a tag",
    )
    parsed_args = parser.parse_args(sys.argv[1:] if args is None else args)

    if parsed_args.destination:
        change_directory(parsed_args.destination, parsed_args.tag)


def change_directory(dest: str, is_tag: bool = False) -> None:
    config = load_config_file()
    tag_config = config["tags"]

    dirpaths = {dirpath for dirpath, tags in tag_config.items() if dest in tags}

    if not is_tag:
        path = Path(dest).expanduser()
        if path.is_dir():
            dirpaths.add(path.resolve())

    if not dirpaths:
        raise DtagsError(f"Invalid destination: {dest}")
    elif len(dirpaths) == 1:
        save_destination_file(dirpaths.pop())
    else:  # pragma: no cover
        save_destination_file(prompt_user_selection(sorted(dirpaths)))


def prompt_user_selection(dirpaths: List[Path]) -> Path:  # pragma: no cover
    for index, dirpath in enumerate(dirpaths, start=1):
        print(f"{index}. {style.path(dirpath)}")

    while True:
        print(f"\nSelect directory [1 - {len(dirpaths)}]: ", end="")
        try:
            return dirpaths[int(input()) - 1]

        except (ValueError, IndexError):
            print(f"Please select an integer from 1 to {len(dirpaths)}")

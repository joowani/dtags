import argparse
import subprocess
import sys
from typing import List, Optional

from dtags import style
from dtags.commons import (
    dtags_command,
    fix_color_for_windows,
    get_argparser,
    normalize_dir,
    normalize_tag,
    reverse_map,
)
from dtags.files import load_config_file

USAGE = "run DEST [DEST ...] -c ..."
DESCRIPTION = f"""
Execute a command in one or more directories.

Target directories are iterated in alphabetical order.
Paths take precedence over tags on name collisions.
The command is run only once per directory in subprocesses.

examples:

  # run "git status" in all directories tagged "work"
  {style.command("run work -c git status")}

  # run "git status" in directories ~/foo and ~/bar
  {style.command("run ~/foo ~/bar -c git status")}

  # run "git status" in directories tagged "work" and in ~/foo
  {style.command("run work ~/foo -c git status")}
"""


@dtags_command
def execute(args: Optional[List[str]] = None) -> None:
    parser = get_argparser(prog="run", desc=DESCRIPTION, usage=USAGE)
    parser.add_argument(
        "destinations",
        metavar="DEST",
        nargs="+",
        help="directory path or tag",
    )
    parser.add_argument(
        "-c",
        "--cmd",
        dest="command",
        nargs=argparse.REMAINDER,
        required=True,
        help="command to execute",
    )
    parsed_args = parser.parse_args(sys.argv[1:] if args is None else args)
    run_command(parsed_args.destinations, parsed_args.command)


def run_command(destinations: List[str], command: List[str]) -> None:
    config = load_config_file()
    tag_config = config["tags"]

    tag_to_dirpaths = reverse_map(tag_config)
    dirpaths = set()

    for dest in destinations:
        dirpath = normalize_dir(dest)
        if dirpath is not None:
            dirpaths.add(dirpath)
        else:
            tag = normalize_tag(dest)
            if tag in tag_to_dirpaths:
                dirpaths.update(tag_to_dirpaths[tag])

    return_code = 0
    for dirpath in sorted(dirpaths):
        tags = tag_config.get(dirpath, set())

        fix_color_for_windows()
        print(f"\n{style.mapping(dirpath, tags)}:")
        try:
            process = subprocess.run(
                command,
                cwd=dirpath,
                stderr=subprocess.STDOUT,
            )
        except FileNotFoundError:
            print(f"Invalid command: {command[0]}", file=sys.stderr)
        except NotADirectoryError:  # pragma no cover
            print(f"Not a directory: {dirpath.as_posix()}", file=sys.stderr)
        else:
            if process.returncode != 0:
                return_code = 1

    sys.exit(return_code)

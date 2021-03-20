import sys
from pathlib import Path
from typing import List, Optional, Set, Tuple

from dtags import style
from dtags.commons import (
    dtags_command,
    get_argparser,
    normalize_dirs,
    normalize_tags,
    prompt_user,
)
from dtags.files import load_config_file, save_config_file

USAGE = "untag [-y] [DIR ...] [-t TAG [TAG ...]]"
DESCRIPTION = f"""
Untag directories.

Tag names are automatically slugified (e.g "foo bar" to "foo-bar").
If no tags are specified, all tags are removed.
If no directories are specified, tags are removed from all directories.

examples:

  # remove tags "app" and "work" from directories ~/foo and ~/bar
  {style.command("untag ~/foo ~/bar -t app work")}

  # remove all tags from directory ~/foo
  {style.command("untag ~/foo")}

  # remove tag "work" from all directories
  {style.command("untag -t work")}

  # skip confirmation prompts with -y/--yes
  {style.command("untag -y ~/foo -t work app")}
"""


@dtags_command
def execute(args: Optional[List[str]] = None) -> None:
    parser = get_argparser(prog="untag", desc=DESCRIPTION, usage=USAGE)
    parser.add_argument(
        "dirs",
        metavar="DIR",
        nargs="*",
        help="directories or tags",
    )
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        dest="yes",
        help="assume yes to prompts",
    )
    parser.add_argument(
        "-t",
        dest="tags",
        metavar="TAG",
        nargs="+",
        help="tag names",
    )
    parsed_args = parser.parse_args(sys.argv[1:] if args is None else args)

    if not parsed_args.dirs and not parsed_args.tags:
        parser.error("one of the following arguments are required: DIR, -t")
    else:
        untag_directories(
            dirs=parsed_args.dirs,
            tags=parsed_args.tags,
            skip_prompts=parsed_args.yes,
        )


def untag_directories(
    dirs: Optional[List[str]] = None,
    tags: Optional[List[str]] = None,
    skip_prompts: bool = True,
) -> None:
    config = load_config_file()
    tag_config = config["tags"]

    norm_dirs = normalize_dirs(dirs) if dirs else tag_config.keys()
    norm_tags = normalize_tags(tags)

    diffs: List[Tuple[Path, Set[str]]] = []

    for dirpath in sorted(norm_dirs):
        cur_tags = tag_config.get(dirpath, set())
        del_tags = cur_tags.intersection(norm_tags) if norm_tags else cur_tags

        if del_tags:
            diffs.append((dirpath, del_tags))
            tag_config[dirpath] = cur_tags - del_tags

    if not diffs:
        print("Nothing to do")
    else:
        for dirpath, del_tags in diffs:
            print(style.diff(dirpath, del_tags=del_tags))

        if skip_prompts or prompt_user():
            save_config_file(config)
            print("Tags removed successfully")

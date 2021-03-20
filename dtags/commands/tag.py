import sys
from pathlib import Path
from typing import List, Optional, Set, Tuple

from dtags import style
from dtags.commons import (
    dtags_command,
    get_argparser,
    normalize_dirs,
    normalize_tag,
    normalize_tags,
    prompt_user,
)
from dtags.files import load_config_file, save_config_file

USAGE = "tag [-y] [-r] DIR [DIR ...] -t TAG [TAG ...]"
DESCRIPTION = f"""
Tag directories.

Tag names are automatically slugified (e.g "foo bar" to "foo-bar").
If no tags are specified, directory basenames are used instead.

examples:

  # tag ~/Foo_Bar with "foo-bar" (slugified)
  {style.command("tag ~/Foo_Bar")}

  # tag ~/foo and ~/bar with "work" and "app" (many-to-many)
  {style.command("tag ~/foo ~/bar -t work app")}

  # replace existing tags with -r/--replace
  {style.command("tag -r ~/foo -t work")}

  # skip confirmation prompts with -y/--yes
  {style.command("tag -y ~/foo -t work app")}
"""


@dtags_command
def execute(args: Optional[List[str]] = None) -> None:
    parser = get_argparser(prog="tag", desc=DESCRIPTION, usage=USAGE)
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        dest="yes",
        help="assume yes to prompts",
    )
    parser.add_argument(
        "-r",
        "--replace",
        action="store_true",
        dest="replace",
        help="replace existing tags",
    )
    parser.add_argument(
        "dirs",
        metavar="DIR",
        nargs="+",
        help="directories or tags",
    )
    parser.add_argument(
        "-t",
        dest="tags",
        metavar="TAG",
        nargs="+",
        help="tag names",
    )
    parsed_args = parser.parse_args(sys.argv[1:] if args is None else args)

    tag_directories(
        dirs=parsed_args.dirs,
        tags=parsed_args.tags,
        replace=parsed_args.replace,
        skip_prompts=parsed_args.yes,
    )


def tag_directories(
    dirs: Optional[List[str]] = None,
    tags: Optional[List[str]] = None,
    replace: bool = False,
    skip_prompts: bool = True,
) -> None:
    config = load_config_file()
    tag_config = config["tags"]

    norm_dirs = normalize_dirs(dirs)
    norm_tags = normalize_tags(tags)

    diffs: List[Tuple[Path, Set[str], Set[str]]] = []

    for dirpath in sorted(norm_dirs):
        cur_tags = tag_config.get(dirpath, set())
        new_tags = norm_tags or {normalize_tag(dirpath.name)}
        add_tags = new_tags - cur_tags
        del_tags = (cur_tags - new_tags) if replace else set()

        if add_tags or del_tags:
            diffs.append((dirpath, add_tags, del_tags))
            tag_config[dirpath] = cur_tags.union(add_tags) - del_tags

    if not diffs:
        print("Nothing to do")
    else:
        for dirpath, add_tags, del_tags in diffs:
            print(style.diff(dirpath, add_tags, del_tags))

        if skip_prompts or prompt_user():
            save_config_file(config)
            print("Tags saved successfully")

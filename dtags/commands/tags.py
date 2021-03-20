import json
import sys
from pathlib import Path
from typing import List, Optional, Set, Tuple

from dtags import style
from dtags.commons import (
    dtags_command,
    get_argparser,
    normalize_tags,
    prompt_user,
    reverse_map,
)
from dtags.files import get_new_config, load_config_file, save_config_file

USAGE = "tags [-j] [-r] [-y] [-c] [-p] [-t TAG [TAG ...]]"
DESCRIPTION = f"""
Manage directory tags.

examples:

  # show all tags
  {style.command("tags")}

  # show tags in JSON format with -j/--json
  {style.command("tags --json")}

  # show reverse mapping with -r/--reverse
  {style.command("tags --reverse")}

  # filter specific tags with -t
  {style.command("tags -t foo bar baz")}

  # clean invalid directories with -c/--clean
  {style.command("tags --clean")}

  # purge all tags with -p/--purge
  {style.command("tags --purge")}

  # skip confirmation prompts with -y/--yes
  {style.command("tags --clean --yes")}
"""


@dtags_command
def execute(args: Optional[List[str]] = None) -> None:
    parser = get_argparser(prog="tags", desc=DESCRIPTION, usage=USAGE)
    arg_group = parser.add_mutually_exclusive_group()

    parser.add_argument(
        "-j",
        "--json",
        action="store_true",
        dest="json",
        help="show tags in JSON format",
    )
    parser.add_argument(
        "-r",
        "--reverse",
        action="store_true",
        dest="reverse",
        help="show tag to directories relationship",
    )
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        dest="yes",
        help="assume yes to prompts",
    )
    arg_group.add_argument(
        "-c",
        "--clean",
        action="store_true",
        dest="clean",
        help="clean invalid directories",
    )
    arg_group.add_argument(
        "-p",
        "--purge",
        action="store_true",
        dest="purge",
        help="purge all tags",
    )
    arg_group.add_argument(
        "-t",
        metavar="TAG",
        nargs="+",
        dest="tags",
        help="tag names to filter",
    )
    parsed_args = parser.parse_args(sys.argv[1:] if args is None else args)

    if parsed_args.reverse and parsed_args.clean:
        parser.error("argument -r/--reverse: not allowed with argument -c/--clean")
    elif parsed_args.reverse and parsed_args.purge:
        parser.error("argument -r/--reverse: not allowed with argument -p/--purge")
    elif parsed_args.json and parsed_args.clean:
        parser.error("argument -j/--json: not allowed with argument -c/--clean")
    elif parsed_args.json and parsed_args.purge:
        parser.error("argument -j/--json: not allowed with argument -p/--purge")
    elif parsed_args.clean:
        clean_tags(skip_prompts=parsed_args.yes)
    elif parsed_args.purge:
        purge_tags(skip_prompts=parsed_args.yes)
    else:
        show_tags(
            filters=parsed_args.tags,
            in_json=parsed_args.json,
            in_reverse=parsed_args.reverse,
        )


def show_tags(
    filters: Optional[List[str]] = None,
    in_json: bool = False,
    in_reverse: bool = False,
) -> None:
    config = load_config_file()
    tag_config = config["tags"]

    tag_filters = None if filters is None else normalize_tags(filters)

    if in_json and in_reverse:
        raw_data = {
            tag: sorted(dirpath.as_posix() for dirpath in dirpaths)
            for tag, dirpaths in reverse_map(tag_config).items()
            if not tag_filters or tag in tag_filters
        }
        print(json.dumps(raw_data, indent=2, sort_keys=True))

    elif in_json and not in_reverse:
        raw_data = {
            dirpath.as_posix(): sorted(tags)
            for dirpath, tags in tag_config.items()
            if not tag_filters or tags.intersection(tag_filters)
        }
        print(json.dumps(raw_data, indent=2, sort_keys=True))

    elif not in_json and in_reverse:
        tag_to_dirpaths = reverse_map(tag_config)
        for tag in sorted(tag_to_dirpaths):
            if not tag_filters or tag in tag_filters:
                print(style.tag(tag))
                for dirpath in sorted(tag_to_dirpaths[tag]):
                    print("  " + style.path(dirpath))
    else:
        for dirpath, tags in tag_config.items():
            if not tag_filters or tags.intersection(tag_filters):
                print(style.mapping(dirpath, tags))


def clean_tags(skip_prompts: bool = True) -> None:
    config = load_config_file()
    tag_config = config["tags"]

    diffs: List[Tuple[Path, Set[str]]] = [
        (dirpath, tags) for dirpath, tags in tag_config.items() if not dirpath.is_dir()
    ]
    if not diffs:
        print("Nothing to clean")
    else:
        for dirpath, tags in diffs:
            print(style.diff(dirpath, del_tags=tags))
            del tag_config[dirpath]

        if skip_prompts or prompt_user():
            save_config_file(config)
            print("Tags cleaned successfully")


def purge_tags(skip_prompts: bool = True) -> None:
    config = load_config_file()
    tag_config = config["tags"]

    if not tag_config:
        print("Nothing to purge")
    else:
        for dirpath, tags in tag_config.items():
            print(style.diff(dirpath, del_tags=tags))

        if skip_prompts or prompt_user():
            save_config_file(get_new_config())
            print("Tags purged successfully")

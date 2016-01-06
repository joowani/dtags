#!/usr/bin/env python

import os
from argparse import ArgumentParser

from dtags.help import HelpFormatter
from dtags.colors import MAGENTA, CYAN, YELLOW, CLEAR
from dtags.config import load_config, save_config
from dtags.utils import expand_path

command_description = """
Untag specified directories.

All tag names must be preceded by the {m}@{x} character.
For example, after running {y}untag foo bar @a @b bar baz @c{x}:

    directory {c}foo{x} will no longer have tags {m}@a @b{x}
    directory {c}bar{x} will no longer have tags {m}@a @b @c{x}
    directory {c}baz{x} will no longer have tags {m}@c{x}
""".format(m=MAGENTA, c=CYAN, y=YELLOW, x=CLEAR)

remove_msg = "Removed tag {m}{{}}{e} from directory {c}{{}}{e}".format(
    m=MAGENTA, c=CYAN, e=CLEAR
)


def main():
    tag_to_paths = load_config()
    parser = ArgumentParser(
        prog="untag",
        usage="untag [paths] [tags] ...",
        description=command_description,
        formatter_class=HelpFormatter,
    )
    parser.add_argument(
        "arguments",
        type=str,
        nargs='+',
        metavar='[paths] [tags]',
        help="directory paths followed by tag names"
    )
    parsed = parser.parse_args()

    # Tracking variables
    index = 0
    updates = []
    tags = set()
    paths = set()
    last_path = None
    parsing_paths = True

    # Go through the parsed arguments and pair up tags with paths
    # Also perform some simple validations along the way
    while index < len(parsed.arguments):
        arg = parsed.arguments[index]
        if parsing_paths:
            if arg.startswith('@'):
                if not paths:
                    parser.error("no paths given before {}".format(arg))
                parsing_paths = False
            elif not os.path.isdir(arg):
                parser.error("invalid directory path {}".format(arg))
            else:
                last_path = arg
                paths.add(arg)
                index += 1
        else:
            if arg.startswith('@'):
                if arg not in tag_to_paths:
                    parser.error("unknown tag {}".format(arg))
                tags.add(arg)
                index += 1
            else:
                updates.append((tags, paths))
                tags, paths = set(), set()
                parsing_paths = True
    if parsing_paths:
        parser.error("expecting tags after {}".format(last_path))
    updates.append((tags, paths))

    # Save the new changes and print messages
    messages = set()
    for tags, paths in updates:
        for tag in tags:
            if tag in tag_to_paths:
                for path in paths:
                    path = expand_path(path)
                    tag_to_paths[tag].pop(path, None)
                    messages.add(remove_msg.format(tag, path))
                if not tag_to_paths[tag]:
                    tag_to_paths.pop(tag)
    save_config(tag_to_paths)
    print("\n".join(messages))

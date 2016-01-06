#!/usr/bin/env python

import os
from argparse import ArgumentParser

from dtags.help import HelpFormatter
from dtags.colors import MAGENTA, CYAN, YELLOW, CLEAR
from dtags.chars import TAG_NAME_CHARS
from dtags.config import load_config, save_config
from dtags.utils import expand_path, shrink_path

command_description = """
Tag specified directories.

All tag names must be preceded by the {m}@{x} character.
For example, after running {y}tag foo bar @a @b bar baz @c{x}:

    directory {c}foo{x} will have tags {m}@a @b{x}
    directory {c}bar{x} will have tags {m}@a @b @c{x}
    directory {c}baz{x} will have tags {m}@c{x}

""".format(m=MAGENTA, c=CYAN, y=YELLOW, x=CLEAR)

update_msg = "Added tag {m}{{}}{x} to directory {c}{{}}{x}".format(
    m=MAGENTA, c=CYAN, x=CLEAR
)


def main():
    tag_to_paths = load_config()
    parser = ArgumentParser(
        prog="tag",
        usage="tag [paths] [tags] ...",
        description=command_description,
        formatter_class=HelpFormatter,
    )
    parser.add_argument(
        "-e", "--expand",
        action="store_true",
        help="Expand the directory paths"
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
                    parser.error("no paths given before '{}'".format(arg))
                parsing_paths = False
            elif not os.path.isdir(arg):
                parser.error("invalid directory path '{}'".format(arg))
            else:
                last_path = arg
                paths.add(arg)
                index += 1
        else:
            if arg.startswith('@'):
                tag = arg[1:]
                if len(tag) == 0:
                    parser.error("empty tag name '@'")
                has_alpha = False
                for char in tag:
                    if char not in TAG_NAME_CHARS:
                        parser.error(
                            "invalid character '{}' in tag name '@{}'"
                            .format(char, tag)
                        )
                    has_alpha |= char.isalpha()
                if not has_alpha:
                    parser.error(
                        "no alphabets in tag name '@{}'".format(tag)
                    )
                tags.add(arg)
                index += 1
            else:
                updates.append((tags, paths))
                tags, paths = set(), set()
                parsing_paths = True
    if parsing_paths:
        parser.error("expecting tags after '{}'".format(last_path))
    updates.append((tags, paths))

    # Save the new changes and print messages
    messages = set()
    for tags, paths in updates:
        for tag in tags:
            if tag not in tag_to_paths:
                tag_to_paths[tag] = {}
            for path in paths:
                expanded_path = expand_path(path)
                if not parsed.expand:
                    path = shrink_path(path)
                tag_to_paths[tag][expanded_path] = path
                messages.add(update_msg.format(tag, path))
    save_config(tag_to_paths)
    print("\n".join(messages))

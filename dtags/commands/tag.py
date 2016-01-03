#!/usr/bin/env python

import os
from argparse import ArgumentParser

from dtags.colors import MAGENTA, CYAN, YELLOW, END
from dtags.characters import ALLOWED_CHARS
from dtags.formatters import HelpFormatter
from dtags.config import load_config, save_config

description = """
Tag specified directories.

All tag names must be preceded by the {m}@{e} character.
For example, after running {y}tag foo bar @a @b bar baz @c{e}:

    directory {c}foo{e} will have tags {m}@a @b{e}
    directory {c}bar{e} will have tags {m}@a @b @c{e}
    directory {c}baz{e} will have tags {m}@c{e}
""".format(m=MAGENTA, c=CYAN, y=YELLOW, e=END)

message = "Added tag {m}{{}}{e} to directory {c}{{}}{e}".format(
    m=MAGENTA, c=CYAN, e=END
)


def main():
    config = load_config()
    tags = config["tags"]
    all_paths = set()
    for paths in tags.values():
        all_paths.update(paths)

    parser = ArgumentParser(
        prog="tag",
        usage="tag [options] [paths] [tags] ...",
        description=description,
        formatter_class=HelpFormatter
    )
    parser.add_argument(
        "arguments",
        type=str,
        nargs='+',
        metavar='[paths] [tags]',
        help="directory paths followed by tag names"
    )
    arguments = parser.parse_args().arguments

    collected_tags = set()
    collected_paths = set()
    collecting_paths = True

    def consume_collected():
        for tag_name in collected_tags:
            if tag_name not in tags:
                tags[tag_name] = list(collected_paths)
                for path in collected_paths:
                    print(message.format(tag_name, path))
            else:
                existing_paths = set(tags[tag_name])
                for path in collected_paths:
                    if path not in existing_paths:
                        tags[tag_name].append(path)
                        print(message.format(tag_name, path))
        collected_paths.clear()
        collected_tags.clear()

    index = 0
    while index < len(arguments):
        arg = arguments[index]
        if collecting_paths:
            if arg.startswith('@'):
                if not collected_paths:
                    parser.error(
                        "directory paths missing before '{}'".format(arg)
                    )
                collecting_paths = False
            elif not os.path.isdir(arg):
                parser.error("invalid directory path '{}'".format(arg))
            else:
                collected_paths.add(os.path.realpath(os.path.expanduser(arg)))
                index += 1
        else:
            if arg.startswith('@'):
                tag = arg[1:]
                if len(tag) == 0:
                    parser.error("empty tag name")
                has_alpha = False
                for char in tag:
                    if char not in ALLOWED_CHARS:
                        parser.error("invalid character '{}' in tag name '@{}'"
                                     .format(char, tag))
                    if char.isalpha():
                        has_alpha = True
                if not has_alpha:
                    parser.error("no alphabets in tag name '@{}'".format(tag))
                collected_tags.add(arg)
                index += 1
            else:
                consume_collected()
                collecting_paths = True

    if collecting_paths:
        parser.error("expecting tags for the last argument")

    consume_collected()
    save_config(config)

if __name__ == "__main__":
    main()

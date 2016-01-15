#!/usr/bin/env python

import os
from argparse import ArgumentParser

from dtags.help import HelpFormatter
from dtags.colors import PINK, CYAN, YELLOW, CLEAR
from dtags.chars import TAG_NAME_CHARS
from dtags.config import load_tags, save_tags
from dtags.utils import expand_path, shrink_path

cmd_description = """
dtags - tag directories

e.g. the command {y}tag ~/foo ~/bar @a @b ~/baz @a @c{x}:

    adds to directory {c}~/foo{x} tags {p}@a @b{x}
    adds to directory {c}~/bar{x} tags {p}@a @b{x}
    adds to directory {c}~/baz{x} tags {p}@a @c{x}

""".format(p=PINK, c=CYAN, y=YELLOW, x=CLEAR)

msg = 'Added tag {p}{{}}{x} to {c}{{}}{x}'.format(p=PINK, c=CYAN, x=CLEAR)


def main():
    tag_to_paths = load_tags()
    parser = ArgumentParser(
        prog='tag',
        usage='tag [[paths] [tags]...]',
        description=cmd_description,
        formatter_class=HelpFormatter
    )
    parser.add_argument(
        'arguments',
        type=str,
        nargs='+',
        metavar='[paths] [tags]',
        help='directory paths and tag names'
    )
    parsed = parser.parse_args()

    # Tracking variables and collectors
    updates = []
    arg_index = 0
    parsing_paths = True
    tags_collected = set()
    paths_collected = set()

    # Iterate through the arguments and pair up tags with paths
    while arg_index < len(parsed.arguments):
        arg = parsed.arguments[arg_index]
        if parsing_paths and arg.startswith('@'):
            if len(paths_collected) == 0:
                parser.error('expecting paths before {}'.format(arg))
            parsing_paths = False
        elif parsing_paths and not arg.startswith('@'):
            paths_collected.add(arg)
            arg_index += 1
        elif not parsing_paths and arg.startswith('@'):
            tag_name_has_alphabet = False
            for ch in arg[1:]:
                if ch not in TAG_NAME_CHARS:
                    parser.error('bad char {} in tag name {}'.format(ch, arg))
                tag_name_has_alphabet |= ch.isalpha()
            if not tag_name_has_alphabet:
                parser.error('no alphabets in tag name {}'.format(arg))
            tags_collected.add(arg)
            arg_index += 1
        else:
            updates.append((tags_collected, paths_collected))
            tags_collected, paths_collected = set(), set()
            parsing_paths = True
    if parsing_paths:
        parser.error('expecting a tag name')
    updates.append((tags_collected, paths_collected))

    # Apply updates and message
    messages = set()
    for tags, paths in updates:
        valid_paths = [p for p in paths if os.path.isdir(p)]
        if len(valid_paths) == 0:
            continue
        for tag in tags:
            if tag not in tag_to_paths:
                tag_to_paths[tag] = {}
            for path in valid_paths:
                full_path = expand_path(path)
                short_path = shrink_path(path)
                tag_to_paths[tag][full_path] = short_path
                messages.add(msg.format(tag, full_path))
    save_tags(tag_to_paths)
    if messages:
        print('\n'.join(messages))

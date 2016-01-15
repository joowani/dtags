#!/usr/bin/env python

import os
import argparse

from dtags.help import HelpFormatter
from dtags.colors import PINK, CYAN, YELLOW, CLEAR
from dtags.config import load_tags, save_tags
from dtags.utils import expand_path

cmd_description = """
dtags - untag directories

e.g. the command {y}untag ~/foo ~/bar @a @b ~/baz @c @d{x}:

    removes from directory {c}~/foo{x} tags {p}@a @b{x}
    removes from directory {c}~/bar{x} tags {p}@a @b{x}
    removes from directory {c}~/baz{x} tags {p}@c @d{x}

""".format(p=PINK, c=CYAN, y=YELLOW, x=CLEAR)

msg = 'Removed tag {p}{{}}{x} from {c}{{}}{x}'.format(p=PINK, c=CYAN, x=CLEAR)


def main():
    tag_to_paths = load_tags()
    parser = argparse.ArgumentParser(
        prog="untag",
        usage="untag [options] [[paths] [tags]...]",
        description=cmd_description,
        formatter_class=HelpFormatter
    )
    parser.add_argument(
        '-a', '--all',
        help='untag all tags or paths',
        action='store_true'
    )
    parser.add_argument(
        'arguments',
        type=str,
        nargs=argparse.REMAINDER,
        metavar='[paths] [tags]',
        help='directory paths and tag names'
    )
    parsed = parser.parse_args()

    if parsed.all:
        # Collect all the paths and tags to remove
        messages = set()
        tags_to_remove = set()
        paths_to_remove = set()
        for arg in parsed.arguments:
            if arg in tag_to_paths:
                tags_to_remove.add(arg)
            elif os.path.isdir(arg):
                paths_to_remove.add(expand_path(arg))

        # Untag all the paths specified
        for tag, paths in tag_to_paths.items():
            for path in [p for p in paths if p in paths_to_remove]:
                paths.pop(path)
                messages.add(msg.format(tag, path))
            if len(paths) == 0:
                tags_to_remove.add(tag)

        # Remove all the tags specified
        for tag in tags_to_remove:
            paths = tag_to_paths.pop(tag)
            for path in paths:
                messages.add(msg.format(tag, expand_path(path)))

        # Save the updated tags and print messages
        save_tags(tag_to_paths)
        if messages:
            print('\n'.join(messages))
    else:
        # Initialize tracking variables and collectors
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
                    parser.error('excepting paths before {}'.format(arg))
                parsing_paths = False
            elif parsing_paths and not arg.startswith('@'):
                paths_collected.add(arg)
                arg_index += 1
            elif not parsing_paths and arg.startswith('@'):
                tags_collected.add(arg)
                arg_index += 1
            else:
                updates.append((tags_collected, paths_collected))
                tags_collected, paths_collected = set(), set()
                parsing_paths = True
        if parsing_paths:
            parser.error('expecting a tag name')
        updates.append((tags_collected, paths_collected))

        # Apply updates and collect messages to print
        messages = set()
        for tags, paths in updates:
            for tag in tags:
                if tag not in tag_to_paths:
                    continue
                for path in paths:
                    if not os.path.isdir(path):
                        continue
                    full_path = expand_path(path)
                    if full_path in tag_to_paths[tag]:
                        tag_to_paths[tag].pop(full_path)
                        messages.add(msg.format(tag, full_path))
                if len(tag_to_paths[tag]) == 0:
                    # Remove the tag completely if it has no paths
                    tag_to_paths.pop(tag)

        # Save the updated tags and print messages
        save_tags(tag_to_paths)
        if messages:
            print('\n'.join(messages))

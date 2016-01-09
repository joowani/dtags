#!/usr/bin/env python

import os
import sys
import json

from collections import defaultdict
from argparse import ArgumentParser

from dtags.colors import PINK, CYAN, YELLOW, CLEAR
from dtags.completion import ChoicesCompleter, autocomplete
from dtags.config import load_tags
from dtags.help import HelpFormatter
from dtags.utils import expand_path

cmd_description = """
dtags - display tags and tagged directories

e.g. the command {y}tags @a @b ~/foo ~/bar @c{x}:

    displays tags {p}@a @b @c{x}
    displays all tags with directory {c}~/foo{x}
    displays all tags with directory {c}~/bar{x}

""".format(p=PINK, c=CYAN, y=YELLOW, x=CLEAR)


def main():
    tag_to_paths = load_tags()
    path_to_tags = defaultdict(set)
    for tag, paths in tag_to_paths.items():
        for path in paths.keys():
            path_to_tags[path].add(tag)

    parser = ArgumentParser(
        prog="tags",
        description=cmd_description,
        usage="tags [options] [paths] [tags]",
        formatter_class=HelpFormatter
    )
    parser.add_argument(
        "-e", "--expand",
        action="store_true",
        help="Expand the directory paths"
    )
    parser.add_argument(
        "-r", "--reverse",
        help="display the reverse mapping",
        action="store_true"
    )
    parser.add_argument(
        "-j", "--json",
        help="display the raw JSON",
        action="store_true"
    )
    parser.add_argument(
        "search_terms",
        type=str,
        nargs='*',
        metavar="[paths] [tags]",
        help="tag and directory paths to filter by"
    ).completer = ChoicesCompleter(tag_to_paths.keys())
    autocomplete(parser)
    parsed = parser.parse_args()

    if len(tag_to_paths) == 0:
        print("No tags found! You can add them by running the 'tag' command.")
        sys.exit(0)

    # Filter by any given tags and paths
    # TODO optimize here if possible
    if not parsed.search_terms:
        if parsed.expand:
            filtered = {t: ps.keys() for t, ps in tag_to_paths.items()}
        else:
            filtered = {t: ps.values() for t, ps in tag_to_paths.items()}
    else:
        filtered = {}
        for term in parsed.search_terms:
            if term in tag_to_paths:
                if parsed.expand:
                    filtered[term] = tag_to_paths[term].keys()
                else:
                    filtered[term] = tag_to_paths[term].values()
            elif os.path.isdir(term):
                term = expand_path(term)
                if term in path_to_tags:
                    for tag in path_to_tags[term]:
                        if parsed.expand:
                            filtered[tag] = tag_to_paths[tag].keys()
                        else:
                            filtered[tag] = tag_to_paths[tag].values()

    if parsed.json:
        formatted = {tag: sorted(paths) for tag, paths in filtered.items()}
        print(json.dumps(formatted, sort_keys=True, indent=4))
    elif parsed.reverse:
        reverse = defaultdict(set)
        for tag, paths in filtered.items():
            for path in paths:
                reverse[path].add(tag)
        for path, tags in reverse.items():
            print("{}{}{}".format(CYAN, path, CLEAR))
            print("{}{}{}\n".format(PINK, " ".join(sorted(tags)), CLEAR))
    else:
        for tag, paths in sorted(filtered.items()):
            print("{}{}{}".format(PINK, tag, CLEAR))
            print("{}{}{}\n".format(CYAN, "\n".join(sorted(paths)), CLEAR))

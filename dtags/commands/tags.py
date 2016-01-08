#!/usr/bin/env python

import os
import json

from collections import defaultdict
from argparse import ArgumentParser

from dtags.colors import PINK, CYAN, CLEAR
from dtags.completion import ChoicesCompleter, autocomplete
from dtags.config import load_tags
from dtags.utils import expand_path


def main():
    tag_to_paths = load_tags()
    path_to_tags = defaultdict(set)
    for tag, paths in tag_to_paths.items():
        for path in paths.keys():
            path_to_tags[path].add(tag)

    parser = ArgumentParser(
        prog="tags",
        description="dtags: display tags and tagged directories",
        usage="tags [options] [paths] [tags]",
    )
    parser.add_argument(
        "-e", "--expand",
        action="store_true",
        help="Expand the directory paths"
    )
    parser.add_argument(
        "-r", "--reverse",
        help="display tags to directories",
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
        help="tag and/or directory paths to search",
    ).completer = ChoicesCompleter(tag_to_paths.keys())
    autocomplete(parser)
    parsed = parser.parse_args()

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

#!/usr/bin/env python
import os
import json
from collections import defaultdict
from argparse import ArgumentParser
from argcomplete import autocomplete

from dtags.colors import MAGENTA, CYAN, END
from dtags.completers import ChoicesCompleter
from dtags.formatters import HelpFormatter
from dtags.config import load_config


# TODO optimize the filtering if possible
def main():
    tags = load_config()['tags']
    paths_to_tags = defaultdict(set)
    for tag_name, paths in tags.items():
        for path in paths:
            paths_to_tags[path].add(tag_name)

    parser = ArgumentParser(
        prog="tags",
        description="Display tagged directories.",
        usage="tags [options] [paths] [tags]",
        formatter_class=HelpFormatter
    )
    parser.add_argument(
        "-s", "--swap",
        help="display tags to directories",
        action="store_true"
    )
    parser.add_argument(
        "-r", "--raw",
        help="display the raw JSON",
        action="store_true"
    )
    parser.add_argument(
        "search_terms",
        type=str,
        nargs='*',
        metavar="[paths] [tags]",
        help="tag and/or directory paths to search",
    ).completer = ChoicesCompleter(tags.keys() + paths_to_tags.keys())
    autocomplete(parser)
    args = parser.parse_args()

    if not args.search_terms:
        filtered_tags = tags
    else:
        filtered_tags = {}
        for term in args.search_terms:
            if term in tags:
                filtered_tags[term] = tags[term]
            elif os.path.isdir(term):
                term = os.path.realpath(os.path.expanduser(term))
                if term in paths_to_tags:
                    for tag_name in paths_to_tags[term]:
                        filtered_tags[tag_name] = tags[tag_name]
    if args.raw:
        print(json.dumps(filtered_tags, sort_keys=True, indent=4))
    elif args.swap:
        swapped = defaultdict(set)
        for tag_name, paths in filtered_tags.items():
            for path in paths:
                swapped[path].add(tag_name)
        for path, tags in swapped.items():
            print("{}{}{}".format(CYAN, path, END))
            print("{}{}{}\n".format(MAGENTA, " ".join(sorted(tags)), END))
    else:
        for tag_name, paths in sorted(filtered_tags.items()):
            print("{}{}{}".format(MAGENTA, tag_name, END))
            for path in paths:
                print("{}{}{}".format(CYAN, path, END))
            print("")

if __name__ == "__main__":
    main()

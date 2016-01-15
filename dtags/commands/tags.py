#!/usr/bin/env python

import os
import sys
import json
import shutil
import subprocess

from collections import defaultdict
from argparse import ArgumentParser

from dtags.config import TAGS_FILE_PATH
from dtags.colors import PINK, CYAN, YELLOW, CLEAR
from dtags.completion import ChoicesCompleter, autocomplete
from dtags.config import load_tags, check_tags, save_tags
from dtags.help import HelpFormatter
from dtags.utils import halt, expand_path, shrink_path, msgify, safe_remove

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
        prog='tags',
        description=cmd_description,
        usage='tags [options] [paths] [tags]',
        formatter_class=HelpFormatter
    )
    parser.add_argument(
        '-e', '--edit',
        action='store_true',
        help='Edit the tags directly using an editor'
    )
    parser.add_argument(
        '-x', '--expand',
        action='store_true',
        help='Expand the directory paths'
    )
    parser.add_argument(
        '-r', '--reverse',
        help='display the reverse mapping',
        action='store_true'
    )
    parser.add_argument(
        '-j', '--json',
        help='display the raw JSON',
        action='store_true'
    )
    parser.add_argument(
        'search_terms',
        type=str,
        nargs='*',
        metavar='[paths] [tags]',
        help='tag and directory paths to filter by'
    ).completer = ChoicesCompleter(tag_to_paths.keys())
    autocomplete(parser)
    parsed = parser.parse_args()

    if parsed.edit:
        if parsed.search_terms:
            raise parser.error('no arguments allowed with option -e/--edit')
        edit_file_path = TAGS_FILE_PATH + '.edit'
        shutil.copy2(TAGS_FILE_PATH, edit_file_path)
        subprocess.call([os.environ.get('EDITOR', 'vi'), edit_file_path])
        new_tag_to_paths = save_error = None
        with open(edit_file_path, 'r') as edit_file:
            try:
                new_tag_to_paths = json.load(edit_file)
            except ValueError as err:
                save_error = 'Failed to save tags: {}'.format(msgify(err))
            else:
                try:
                    check_tags(new_tag_to_paths)
                except ValueError as err:
                    save_error = 'Failed to save tags: {}'.format(err)
        safe_remove(edit_file_path)
        if save_error is not None:
            halt(save_error)
        save_tags({
            tag: {expand_path(p): shrink_path(p) for p in paths}
            for tag, paths in new_tag_to_paths.items()
        })
        print('New tags saved successfully')
        sys.exit(0)

    if len(tag_to_paths) == 0:
        print('No tags defined')
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
            print('{}{}{}'.format(CYAN, path, CLEAR))
            print('{}{}{}\n'.format(PINK, ' '.join(sorted(tags)), CLEAR))
    else:
        for tag, paths in sorted(filtered.items()):
            print('{}{}{}'.format(PINK, tag, CLEAR))
            print('{}{}{}\n'.format(CYAN, '\n'.join(sorted(paths)), CLEAR))

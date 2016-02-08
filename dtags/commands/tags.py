import os
import sys
import shutil
import argparse
import subprocess
from collections import defaultdict

from dtags import MAPPING_FILE
from dtags.colors import RED, PINK, CYAN, YELLOW, END
from dtags.config import load_mapping, save_mapping, parse_mapping
from dtags.exceptions import ParseError
from dtags.help import HelpFormatter
from dtags.utils import halt, info, is_dir, expand_path, collapse_path, rm_file


cmd_description = """
dtags - display tags and tagged directories

e.g. {y}tags @a @b ~/foo ~/bar @c{x} displays:

    tags {p}@a @b{x} and {p}@c{x}
    all tags mapped to directory {c}~/foo{x}
    all tags mapped to directory {c}~/bar{x}

""".format(p=PINK, c=CYAN, y=YELLOW, x=END)

msg = 'removed path {r}{{}}{x} for {p}{{}}{x}'.format(r=RED, p=PINK, x=END)


def main():
    parser = argparse.ArgumentParser(
        prog='dtags: tags',
        description=cmd_description,
        usage='tags [option] [target]',
        formatter_class=HelpFormatter
    )
    parser.add_argument(
        '-c', '--clean',
        action='store_true',
        help='remove invalid directories'
    )
    parser.add_argument(
        '-e', '--edit',
        action='store_true',
        help='edit the tags directly using an editor'
    )
    parser.add_argument(
        '-u', '--user',
        action='store_true',
        help='expand the user in the directory paths'
    )
    parser.add_argument(
        '-r', '--reverse',
        help='display the reverse mapping',
        action='store_true'
    )
    parser.add_argument(
        'targets',
        type=str,
        nargs='*',
        metavar='target',
        help='directory path or tag name'
    )
    args = parser.parse_args()

    if args.edit:
        if args.clean or args.user or args.reverse or args.targets:
            parser.error('no other arguments allowed with -e/--edit')
        if 'EDITOR' not in os.environ:
            parser.error('environment variable EDITOR not defined')
        temp_mapping_file = MAPPING_FILE + '.tmp'
        shutil.copy2(MAPPING_FILE, temp_mapping_file)
        subprocess.call([os.environ['EDITOR'], temp_mapping_file])
        try:
            new_mapping = parse_mapping(temp_mapping_file)
        except ParseError as err:
            rm_file(temp_mapping_file)
            halt(message=str(err))
        else:
            save_mapping(new_mapping)
            rm_file(temp_mapping_file)
            info('new tags saved successfully')
            sys.exit(0)

    mapping = load_mapping()
    if len(mapping) == 0:
        info('no tags defined')
        sys.exit(0)

    if args.clean:
        if args.edit or args.user or args.reverse or args.targets:
            parser.error('no other arguments allowed with -c/--clean')
        messages = set()
        for tag in list(mapping):
            for path in list(mapping[tag]):
                if not is_dir(path):
                    mapping[tag].remove(path)
                    messages.add(msg.format(path, tag))
            if len(mapping[tag]) == 0:
                mapping.pop(tag)
        save_mapping(mapping)
        if len(messages) > 0:
            for message in sorted(messages):
                info(message)
        else:
            info('nothing to clean')
        sys.exit(0)

    # Filter by given tags and/or paths
    if not args.targets:
        filtered = {
            tag: map(expand_path, paths) if args.user else paths
            for tag, paths in mapping.items()
        }
    else:
        reverse_mapping = defaultdict(set)
        for tag, paths in mapping.items():
            for path in paths:
                reverse_mapping[path].add(tag)
        filtered = {}
        for target in args.targets:
            if target in mapping:
                filtered[target] = (
                    map(expand_path, mapping[target])
                    if args.user else mapping[target]
                )
            else:
                target = collapse_path(target)
                if target in reverse_mapping:
                    for tag in reverse_mapping[target]:
                        filtered[tag] = (
                            map(expand_path, mapping[tag])
                            if args.user else mapping[tag]
                        )
    if args.reverse:
        reverse = defaultdict(set)
        for tag, paths in filtered.items():
            for path in paths:
                reverse[path].add(tag)
        for path, tags in reverse.items():
            print('{}{}\n{}{}{}\n'.format(
                CYAN if is_dir(path) else RED, path,
                PINK, ' '.join(sorted(tags)), END
            ))
    else:
        for tag, paths in sorted(filtered.items()):
            print('{}{}\n{}\n'.format(
                PINK, tag,
                '\n'.join('{}{}{}'.format(
                    CYAN if is_dir(path) else RED, path, END
                ) for path in sorted(paths))
            ))

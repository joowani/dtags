import argparse

from dtags.chars import ALLOWED_CHARS
from dtags.colors import PINK, CYAN, YELLOW, END
from dtags.config import load_mapping, save_mapping
from dtags.help import HelpFormatter
from dtags.utils import collapse_path, info

cmd_description = """
dtags - tag directories

e.g. {y}tag ~/foo ~/bar @a @b ~/baz @a @c{x} maps:

    directory {c}~/foo{x} to tags {p}@a @b{x}
    directory {c}~/bar{x} to tags {p}@a @b{x}
    directory {c}~/baz{x} to tags {p}@a @c{x}

""".format(p=PINK, c=CYAN, y=YELLOW, x=END)

msg = 'added tag {p}{{}}{x} to {c}{{}}{x}'.format(p=PINK, c=CYAN, x=END)


def main():
    parser = argparse.ArgumentParser(
        prog='dtags: tag',
        usage='tag [[path] [tag]]',
        description=cmd_description,
        formatter_class=HelpFormatter
    )
    parser.add_argument(
        'arguments',
        type=str,
        nargs='+',
        metavar='[path] [tag]',
        help='directory paths and tag names'
    )
    args = parser.parse_args()
    mapping = load_mapping()

    # Tracking variables and collectors
    updates = []
    arg_index = 0
    parsing_paths = True
    tags_collected = set()
    paths_collected = set()
    # Iterate through the arguments and pair up tags with paths
    while arg_index < len(args.arguments):
        arg = args.arguments[arg_index]
        if parsing_paths and arg.startswith('@'):
            if len(paths_collected) == 0:
                parser.error('expecting paths before {}'.format(arg))
            parsing_paths = False
        elif parsing_paths and not arg.startswith('@'):
            paths_collected.add(arg)
            arg_index += 1
        elif not parsing_paths and arg.startswith('@'):
            tag_has_alpha = False
            for char in arg[1:]:
                if char not in ALLOWED_CHARS:
                    parser.error('bad char {} in tag {}'.format(char, arg))
                tag_has_alpha |= char.isalpha()
            if not tag_has_alpha:
                parser.error('no alphabets in tag {}'.format(arg))
            tags_collected.add(arg)
            arg_index += 1
        else:
            updates.append((tags_collected, paths_collected))
            tags_collected, paths_collected = set(), set()
            parsing_paths = True
    if parsing_paths:
        parser.error('expecting a tag name')
    updates.append((tags_collected, paths_collected))
    # Apply changes
    messages = set()
    for tags, paths in updates:
        for tag in tags:
            if tag not in mapping:
                mapping[tag] = set()
            for path in paths:
                path = collapse_path(path)
                mapping[tag].add(path)
                messages.add(msg.format(tag, path))
    save_mapping(mapping)
    for message in messages:
        info(message)

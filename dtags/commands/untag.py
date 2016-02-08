import argparse

from dtags.help import HelpFormatter
from dtags.colors import PINK, CYAN, YELLOW, END
from dtags.config import load_mapping, save_mapping
from dtags.utils import info, collapse_path

cmd_description = """
dtags - untag directories

e.g. {y}untag ~/foo ~/bar @a @b ~/baz @c @d{x} removes:

    tags {p}@a @b{x} from directory {c}~/foo{x}
    tags {p}@a @b{x} from directory {c}~/bar{x}
    tags {p}@c @d{x} from directory {c}~/baz{x}

""".format(p=PINK, c=CYAN, y=YELLOW, x=END)

msg = 'removed tag {p}{{}}{x} from {c}{{}}{x}'.format(p=PINK, c=CYAN, x=END)


def main():
    parser = argparse.ArgumentParser(
        prog="dtags-untag",
        usage="untag [option] [[path] [tag]]",
        description=cmd_description,
        formatter_class=HelpFormatter
    )
    parser.add_argument(
        '-a', '--all',
        help='untag all directory tags or paths',
        action='store_true'
    )
    parser.add_argument(
        'arguments',
        type=str,
        nargs=argparse.REMAINDER,
        metavar='[[path] [tag]]',
        help='directory paths and tag names'
    )
    args = parser.parse_args()
    mapping = load_mapping()

    if args.all:
        # Collect all the paths and tags to remove
        messages = set()
        tags_to_remove = set()
        paths_to_remove = set()
        for arg in args.arguments:
            if arg.startswith('@'):
                tags_to_remove.add(arg)
            else:
                paths_to_remove.add(collapse_path(arg))
        # Remove all the specified paths
        for tag, paths in mapping.items():
            for path in [p for p in paths if p in paths_to_remove]:
                paths.remove(path)
                messages.add(msg.format(tag, path))
            if len(paths) == 0:
                tags_to_remove.add(tag)
        # Remove all the specified tags
        for tag in tags_to_remove:
            paths = mapping.pop(tag)
            for path in paths:
                messages.add(msg.format(tag, collapse_path(path)))
        # Save the changes and print messages
        save_mapping(mapping)
        for message in messages:
            info(message)
    else:
        # Initialize trackers and collectors
        updates = []
        arg_index = 0
        parsing_paths = True
        tags_collected = set()
        paths_collected = set()
        # Iterate through the arguments and pair up tags with paths
        while arg_index < len(args.arguments):
            arg = args.arguments[arg_index]
            if parsing_paths and arg.startswith('@'):
                if not paths_collected:
                    parser.error('expecting paths before {}'.format(arg))
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
        # Apply the changes and collect messages to print
        messages = set()
        for tags, paths in updates:
            for tag in tags:
                if tag not in mapping:
                    continue
                for path in paths:
                    path = collapse_path(path)
                    if path in mapping[tag]:
                        mapping[tag].remove(path)
                        messages.add(msg.format(tag, path))
                if len(mapping[tag]) == 0:
                    # Remove the tag completely if it has no paths
                    mapping.pop(tag)
        # Save the updated tags and print messages
        save_mapping(mapping)
        for message in messages:
            info(message)

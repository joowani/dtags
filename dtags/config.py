import os
import json

from dtags.utils import halt, expand_path

TAGS = os.path.expanduser('~/.dtags')


def load_tags():
    """Load the tags from disk."""
    if not os.path.exists(TAGS):
        try:
            with open(TAGS, "w") as config_file:
                json.dump({}, config_file)
        except (IOError, OSError) as e:
            halt("Failed to init {}: {}".format(TAGS, e.strerror), e.errno)
    else:
        try:
            with open(TAGS, "r") as config_file:
                json_str = config_file.read().strip()
                tag_data = {} if not json_str else json.loads(json_str)
                return {
                    tag: {expand_path(path): path for path in paths}
                    for tag, paths in tag_data.items()
                }
        except ValueError as e:
            halt("Failed to load {}: {}".format(TAGS, e))
        except (IOError, OSError) as e:
            halt("Failed to load {}: {}".format(TAGS, e.strerror), e.errno)


def save_tags(tags):
    """Save the tags to disk.

    :param tags: tags to save
    """
    try:
        with open(TAGS, "w") as config_file:
            json.dump(
                {tag: sorted(paths.values()) for tag, paths in tags.items()},
                config_file,
                indent=4,
                sort_keys=True
            )
    except IOError as e:
        halt("Failed to save {}: {}".format(TAGS, e.strerror))

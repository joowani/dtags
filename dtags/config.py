import os
import json

from dtags.utils import halt, expand_path

TAGS_FILE = expand_path('~/.dtags')


def load_tags():
    """Load the tags from disk.

    Return a dictionary which maps tag names to sub-dictionaries, which in
    turn maps fully expanded paths to unexpanded paths like this:

    {
        "@app" : {
            "~/app/backend": "/home/user/app/backend",
            "~/app/frontend": "/home/user/app/frontend",
        },
        "@frontend": {
            "~/app/frontend": "/home/user/app/frontend",
        },
        "@backend": {
            "~/app/backend": "/home/user/app/backend",
        }
        ...
    }

    :return: the tags loaded from the disk
    """
    if not os.path.exists(TAGS_FILE):
        try:
            with open(TAGS_FILE, "w") as config_file:
                json.dump({}, config_file)
            return {}
        except (IOError, OSError):
            halt("Failed to initialize {}".format(TAGS_FILE))
    else:
        try:
            with open(TAGS_FILE, "r") as config_file:
                json_str = config_file.read().strip()
                if not json_str:
                    return {}
                tag_data = json.loads(json_str)
                if not tag_data:
                    return {}
                else:
                    return {
                        tag: {expand_path(path): path for path in paths}
                        for tag, paths in tag_data.items()
                    }
        except (ValueError, IOError, OSError):
            # TODO better error handling and messaging here
            halt("Failed to load {}".format(TAGS_FILE))


def save_tags(tags):
    """Save the tags to disk.

    Convert the incoming tags dictionary to JSON and dump the content to the
    file. For portability, only the unexpanded paths are saved.

    :param tags: tags to save to disk
    """
    try:
        with open(TAGS_FILE, "w") as config_file:
            json.dump(
                {tag: sorted(paths.values()) for tag, paths in tags.items()},
                config_file,
                indent=4,
                sort_keys=True
            )
    except IOError:
        # TODO better error handling and messaging here
        halt("Failed to write to {}: {}".format(TAGS_FILE))

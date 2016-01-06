import os
import json

from dtags.utils import halt, expand_path

CONFIG = os.path.expanduser('~/.dtags')


def load_config():
    """Load the configuration from disk."""
    if not os.path.exists(CONFIG):
        try:
            with open(CONFIG, "w") as config_file:
                json.dump({}, config_file)
        except (IOError, OSError) as e:
            halt("Failed to init {}: {}".format(CONFIG, e.strerror), e.errno)
    else:
        try:
            with open(CONFIG, "r") as config_file:
                json_str = config_file.read().strip()
                tag_data = {} if not json_str else json.loads(json_str)
                return {
                    tag: {expand_path(path): path for path in paths}
                    for tag, paths in tag_data.items()
                }
        except ValueError as e:
            halt("Failed to load {}: {}".format(CONFIG, e.message))
        except (IOError, OSError) as e:
            halt("Failed to load {}: {}".format(CONFIG, e.strerror), e.errno)


def save_config(config):
    """Save the configuration to disk.

    :param config: configuration
    """
    try:
        with open(CONFIG, "w") as config_file:
            json.dump(
                {tag: paths.values() for tag, paths in config.items()},
                config_file,
                indent=4,
                sort_keys=True
            )
    except IOError as e:
        halt("Failed to save {}: {}".format(CONFIG, e.strerror))

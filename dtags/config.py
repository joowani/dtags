import os
import json

from dtags.utils import halt

ROOT_PATH = os.path.expanduser('~/.dtags')
CONFIG_PATH = os.path.join(ROOT_PATH, 'config')

NEW_CONFIG = {
    "tags": {}
}


def load_config():
    """Load the configuration from disk.

    :return: configuration
    """
    if not os.path.exists(ROOT_PATH):
        os.makedirs(ROOT_PATH)
    if not os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "w") as fp:
                json.dump(NEW_CONFIG, fp)
                return NEW_CONFIG
        except (IOError, OSError) as e:
            halt("Failed to initialize config {}: {}"
                 .format(CONFIG_PATH, e.strerror), e.errno)
    try:
        with open(CONFIG_PATH, "r") as fp:
            data = fp.read().strip()
            return {} if not data else json.loads(data)
    except ValueError as e:
        halt("Failed to load {}: {}".format(CONFIG_PATH, e.message))
    except (IOError, OSError) as e:
        halt("Failed to load {}: {}".format(CONFIG_PATH, e.strerror), e.errno)


def save_config(config):
    """Save the configuration to disk.

    :param config: configuration
    """
    try:  # Write the configuration to the disk
        with open(CONFIG_PATH, "w") as fp:
            json.dump(config, fp, indent=4, sort_keys=True)
    except IOError as e:
        halt("Failed to write to {}: {}".format(CONFIG_PATH, e.strerror))

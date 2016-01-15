import os
import json

from dtags.chars import TAG_NAME_CHARS
from dtags.utils import halt, expand_path, is_dict, is_list, is_str

TAGS_FILE_PATH = expand_path('~/.dtags')
TEMP_FILE_PATH = TAGS_FILE_PATH + '.tmp'


def load_tags():
    """Load the tags from disk.

    Return a dictionary which maps tag names to sub-dictionaries, which in
    turn maps fully expanded paths to unexpanded paths like this:

    {
        "@app" : {
            "/home/user/app/backend": "~/app/backend",
            "/home/user/app/frontend": "~/app/frontend",
        },
        "@frontend": {
            "/home/user/app/frontend": "~/app/frontend",
        },
        "@backend": {
            "/home/user/app/backend": "~/app/backend",
        }
        ...
    }

    :return: the tags loaded from the disk
    """
    if not os.path.exists(TAGS_FILE_PATH):
        try:
            with open(TAGS_FILE_PATH, 'w') as open_file:
                json.dump({}, open_file)
            return {}
        except (IOError, OSError):
            halt('Failed to initialize {}'.format(TAGS_FILE_PATH))
    else:
        try:
            with open(TAGS_FILE_PATH, 'r') as open_file:
                json_str = open_file.read().strip()
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
            halt('Failed to load {}'.format(TAGS_FILE_PATH))


def save_tags(tags):
    """Save the tags to disk.

    Convert the incoming tags dictionary to JSON and dump the content to the
    file. For portability, only the unexpanded paths are saved.

    :param tags: tags to save to disk
    """
    try:
        with open(TEMP_FILE_PATH, 'w') as open_file:
            json.dump(
                {tag: sorted(paths.values()) for tag, paths in tags.items()},
                open_file,
                indent=4,
                sort_keys=True
            )
    except IOError:
        # TODO better error handling and messaging here
        halt('Failed to write to {}'.format(TAGS_FILE_PATH))
    else:
        # Overwrite the old file with the new
        os.rename(TEMP_FILE_PATH, TAGS_FILE_PATH)


def check_tags(tags):
    """Check the tags for correctness.

    :param tags: tags to check for correctness
    :raise: ValueError
    """
    if not is_dict(tags):
        raise ValueError('expecting a JSON object')
    for tag, paths in tags.items():
        if not (is_str(tag) and tag.startswith('@')):
            raise ValueError('invalid tag name {}'.format(tag))
        tag_name_has_alphabet = False
        for ch in tag[1:]:
            if ch not in TAG_NAME_CHARS:
                raise ValueError('bad char {} in tag name {}'.format(ch, tag))
            tag_name_has_alphabet |= ch.isalpha()
        if not tag_name_has_alphabet:
            raise ValueError('no alphabets in tag name {}'.format(tag))
        if not (is_list(paths) and len(paths) > 0):
            raise ValueError('expecting a non-empty list for {}'.format(tag))
        for path in paths:
            if not (is_str(path) and os.path.isdir(expand_path(path))):
                raise ValueError(
                    'invalid directory path {} for {}'.format(path, tag)
                )

"""DTags configuration."""

import os
import errno
import shutil
from collections import defaultdict

from dtags import DTAGS_DIR, TAGS_FILE, MAPPING_FILE
from dtags.chars import ALLOWED_CHARS
from dtags.exceptions import ParseError
from dtags.utils import halt, expand_path, collapse_path, msgify, rm_file


def load_mapping():
    """Load the tag-to-paths mapping from the disk.

    :return: the tags loaded from the disk
    :rtype: dict
    """
    try:
        return parse_mapping(MAPPING_FILE)
    except ParseError as parse_error:
        halt(message=str(parse_error))
    except (IOError, OSError) as parse_error:
        if parse_error.errno != errno.ENOENT:
            halt(
                message='failed to read {}: {}'.format(
                    MAPPING_FILE, msgify(parse_error.strerror)
                ),
                exit_code=parse_error.errno
            )
        else:
            try:
                os.makedirs(DTAGS_DIR)
            except (IOError, OSError) as create_error:
                if create_error.errno != errno.EEXIST:
                    halt(
                        message='failed to create directory {}: {}'.format(
                            DTAGS_DIR, msgify(create_error.strerror)
                        ),
                        exit_code=create_error.errno
                    )
            try:
                open(MAPPING_FILE, 'w').close()
            except (IOError, OSError) as create_error:
                if create_error.errno != errno.EEXIST:
                    halt(
                        message='failed to create mapping {}: {}'.format(
                            MAPPING_FILE, msgify(create_error.strerror)
                        ),
                        exit_code=create_error.errno
                    )
            try:
                open(TAGS_FILE, 'w').close()
            except (IOError, OSError) as create_error:
                if create_error.errno != errno.EEXIST:
                    halt(
                        message='failed to create tags {}: {}'.format(
                            TAGS_FILE, msgify(create_error.strerror)
                        ),
                        exit_code=create_error.errno
                    )
            return {}  # Return empty mapping


def save_mapping(mapping):
    """Save the mapping and the tags back to the disk.

    This function assumes that the mapping is already validated.

    :param mapping: the mapping to save to disk
    :type mapping: collections.Mapping
    """
    temp_mapping_file = MAPPING_FILE + '.tmp'
    reverse_mapping = defaultdict(set)
    for tag, paths in mapping.items():
        for path in paths:
            reverse_mapping[path].add(tag)
    try:
        with open(temp_mapping_file, 'w') as open_file:
            open_file.write('\n'.join(
                ' '.join([path] + sorted(reverse_mapping[path]))
                for path in sorted(reverse_mapping)
            ))
    except (IOError, OSError) as mapping_save_error:
        rm_file(temp_mapping_file)
        halt(
            message='failed to write to {}: {}\n'.format(
                temp_mapping_file, msgify(mapping_save_error.strerror)
            ),
            exit_code=mapping_save_error.errno
        )
    else:
        temp_tags_file = TAGS_FILE + '.tmp'
        try:
            with open(temp_tags_file, 'w') as open_file:
                open_file.write(' '.join(sorted(mapping)))
        except (IOError, OSError) as tags_save_error:
            rm_file(temp_tags_file, ignore_errors=True)
            rm_file(temp_mapping_file, ignore_errors=True)
            halt(
                message='failed to write to {}: {}\n'.format(
                    temp_tags_file, msgify(tags_save_error.strerror)
                ),
                exit_code=tags_save_error.errno
            )
        else:
            os.rename(temp_tags_file, TAGS_FILE)
            os.rename(temp_mapping_file, MAPPING_FILE)


def parse_mapping(filename):
    """Validate the mapping and return it.

    Return a mapping of tag names to directory paths like this:
    {
        "@app" : {"~/app/backend", "~/app/frontend"},
        "@frontend": {"~/app/frontend", "~/app/web"}
    }

    :param filename: the path of the mapping file to validate
    :type filename: str
    :return: the tags loaded from the disk
    :rtype: dict
    :raises: dtags.exceptions.ParseError
    """
    with open(filename, 'r') as open_file:
        mapping = defaultdict(set)
        line_num = 1
        for line in open_file.readlines():
            words = line.split()
            if len(words) <= 1:
                raise ParseError(filename, line_num, 'line malformed')
            path, tags = expand_path(words[0]), words[1:]
            for tag in tags:
                if not tag.startswith('@'):
                    raise ParseError(
                        filename,
                        line_num,
                        'bad tag name {}'.format(tag)
                    )
                tag_has_alphabet = False
                for char in tag[1:]:
                    if char not in ALLOWED_CHARS:
                        raise ParseError(
                            filename,
                            line_num,
                            "bad char '{}' in tag name {}".format(char, tag)
                        )
                    tag_has_alphabet |= char.isalpha()
                if not tag_has_alphabet:
                    raise ParseError(
                        filename,
                        line_num,
                        'no alphabets in tag name {}'.format(tag)
                    )
                mapping[tag].add(collapse_path(path))
            line_num += 1
        return mapping

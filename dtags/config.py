from __future__ import unicode_literals

import os
import io
import errno
import shutil
from collections import defaultdict
from tempfile import NamedTemporaryFile

from dtags import style, CFG_DIR, TAGS_FILE, MAPPING_FILE
from dtags.chars import get_invalid_path_chars, get_invalid_tag_chars
from dtags.utils import abort, expand, rm_files


BULLET = '  > '


def parse_mapping(filename):
    """Parse the mapping file and return a mapping object.

    The mapping object looks like this (tag to directories):
    {
        'app' : {'/home/user/app/backend', '/home/app/frontend'},
        'frontend': {'/home/user/app/frontend'},
        'backend': {'/home/user/app/backend'},
    }
    Any invalid directories and tags are ignored.

    :param filename: the name of the mapping file to parse
    :return: the mapping object and set of ignored paths and tags
    """
    # Collect errors while parsing
    excluded = set()
    orphaned_paths = set()

    # The mapping object to populate
    mapping = defaultdict(set)

    # Parse the file line by line
    with io.open(filename, mode='rt') as mapping_file:
        for line in mapping_file.readlines():
            words = []
            for word in line.split(','):
                word = word.strip()
                if word:
                    words.append(word)
            # Skip empty lines or comments
            if not words or words[0].startswith('#'):
                continue
            # Collect orphan directories
            if len(words) == 1:
                orphaned_paths.add(words[0])
                continue
            path, tags = expand(words[0]), words[1:]
            valid_directory = True
            invalid_path_chars = get_invalid_path_chars(path)
            if invalid_path_chars:
                excluded.add(
                    BULLET + style.bad(path) +
                    ' contains bad characters: ' +
                    style.bad_chars(invalid_path_chars)
                )
                valid_directory = False
            elif not os.path.isdir(path):
                excluded.add(
                    BULLET + style.bad(path) +
                    ' is not a directory path'
                )
                valid_directory = False
            for tag in tags:
                if not tag[0].isalpha():
                    excluded.add(
                        BULLET + style.bad(tag) +
                        ' does not start with an alphabet '
                    )
                    continue
                if ' ' in tag:
                    excluded.add(
                        BULLET + style.bad(tag) +
                        ' contains whitespaces '
                    )
                    continue
                invalid_tag_chars = get_invalid_tag_chars(tag)
                if invalid_tag_chars:
                    excluded.add(
                        BULLET + style.bad(tag) +
                        ' contains bad characters: ' +
                        style.bad_chars(invalid_tag_chars)
                    )
                elif valid_directory:
                    mapping[tag].add(path)
                    orphaned_paths.discard(path)
        excluded.update(
            BULLET + style.bad(orphaned_path) +
            ' is not mapped to any valid tags'
            for orphaned_path in orphaned_paths
        )
    # Return the mapping and the ignored entries if any
    return mapping, '\n'.join(excluded) if excluded else None


def load_mapping():
    """Load the mapping from the disk.

    If the configuration directory files do not exist (probably because it is
    the user's first time executing a dtags command), create them.

    :return: the mapping object loaded from the disk
    """
    try:
        # Parse and load the mapping from the disk
        return parse_mapping(MAPPING_FILE)
    except (IOError, OSError) as mapping_load_error:
        if mapping_load_error.errno != errno.ENOENT:
            abort(
                message='Failed to read {file}: {msg}'.format(
                    file=MAPPING_FILE,
                    msg=mapping_load_error.strerror
                ),
                exit_code=mapping_load_error.errno
            )
        else:
            try:  # Create the directory if it does not exist
                os.makedirs(CFG_DIR)
            except (IOError, OSError) as dir_create_error:
                if dir_create_error.errno != errno.EEXIST:
                    abort(
                        message='Failed to create {file}: {msg}'.format(
                            file=CFG_DIR,
                            msg=dir_create_error.strerror
                        ),
                        exit_code=dir_create_error.errno
                    )
            for config_file_to_create in (MAPPING_FILE, TAGS_FILE):
                try:
                    open(config_file_to_create, 'w').close()
                except (IOError, OSError) as file_create_error:
                    if file_create_error.errno != errno.EEXIST:
                        abort(
                            message='Failed to create {file}: {msg}'.format(
                                file=config_file_to_create,
                                msg=file_create_error.strerror
                            ),
                            exit_code=file_create_error.errno
                        )
            return defaultdict(set), None  # Return an empty mapping


def save_mapping(mapping):
    """Save the mapping (and tags for autocomplete) back to the disk.

    This function assumes that the mapping is already validated.

    :param mapping: the mapping object to save
    """
    # Create a reverse mapping (this is what gets saved to the disk)
    reverse_mapping = defaultdict(set)
    for tag, paths in mapping.items():
        for path in paths:
            reverse_mapping[path].add(tag)
    # Save the reverse mapping to a temporary file
    temp_mapping_file = NamedTemporaryFile(
        mode='w', dir=CFG_DIR, prefix='mapping.', delete=False
    )
    temp_mapping_file.close()
    try:
        with io.open(temp_mapping_file.name, 'wt') as temp_mapping_file:
            temp_mapping_file.write('\n'.join(
                path + ',' + ','.join(sorted(reverse_mapping[path])) + ','
                for path in sorted(reverse_mapping)
            ))
            temp_mapping_file.flush()
            os.fsync(temp_mapping_file.fileno())
    except (IOError, OSError) as temp_mapping_write_error:
        rm_files(temp_mapping_file.name)
        abort(
            message='Failed to write to {name}: {msg}\n'.format(
                name=temp_mapping_file.name,
                msg=temp_mapping_write_error.strerror
            ),
            exit_code=temp_mapping_write_error.errno
        )
    # Save the tags (for tab-completion) to a temporary file
    temp_tags_file = NamedTemporaryFile(
        mode='w', prefix='tags.', dir=CFG_DIR, delete=False
    )
    temp_tags_file.close()
    try:
        with io.open(temp_tags_file.name, 'wt') as temp_tags_file:
            temp_tags_file.write('\n'.join(sorted(mapping)))
            temp_tags_file.flush()
            os.fsync(temp_tags_file.fileno())
    except (IOError, OSError) as temp_tags_write_error:
        rm_files(temp_mapping_file.name, temp_tags_file.name)
        abort(
            message='Failed to write to {name}: {msg}\n'.format(
                name=temp_tags_file.name,
                msg=temp_tags_write_error.strerror
            ),
            exit_code=temp_tags_write_error.errno
        )
    try:  # Overwrite the mapping file with the temporary one
        shutil.move(temp_mapping_file.name, MAPPING_FILE)
    except (IOError, OSError) as mapping_rename_error:
        rm_files(temp_mapping_file.name, temp_tags_file.name)
        abort(
            message='Failed to move {src} to {dest}: {msg}\n'.format(
                src=temp_mapping_file.name,
                dest=MAPPING_FILE,
                msg=mapping_rename_error.strerror
            ),
            exit_code=mapping_rename_error.errno
        )
    try:  # Overwrite the tags file with the temporary one
        shutil.move(temp_tags_file.name, TAGS_FILE)
    except (IOError, OSError) as tags_rename_error:
        rm_files(temp_tags_file.name)
        abort(
            message='Failed to move {src} to {dest}: {msg}\n'.format(
                src=temp_tags_file.name,
                dest=TAGS_FILE,
                msg=tags_rename_error.strerror
            ),
            exit_code=tags_rename_error.errno
        )

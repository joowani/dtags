#!/usr/bin/env python

import os
import sys
import json
from collections import defaultdict

HOME = os.path.expanduser('~')
DTAGS = os.path.join(HOME, '.dtags')
TAGS = os.path.join(DTAGS, 'tags')
MAPPING = os.path.join(DTAGS, 'mapping')

if __name__ == '__main__':
    if not os.path.isfile(DTAGS):
        print('Nothing to migrate. You can upgrade dtags!')
        sys.exit(0)
    try:
        with open(DTAGS, 'r') as open_file:
            content = open_file.read().strip()
            mapping = json.loads(content) if content else {}
            rmapping = defaultdict(set)
            for tag, paths in mapping.items():
                for path in paths:
                    rmapping[path].add(tag)
    except (ValueError, IOError, OSError) as e:
        sys.stderr.write('Failed to read {}: {}\n'.format(DTAGS, e))
        sys.exit(getattr(e, 'errno', 1))
    else:
        temp_mapping_file = DTAGS + '.mapping'
        try:
            with open(temp_mapping_file, 'w') as open_file:
                open_file.write('\n'.join(
                    ','.join([os.path.abspath(os.path.expanduser(path))] +
                    [t[1:] for t in sorted(rmapping[path])])
                    for path in sorted(rmapping)
                ))
        except (IOError, OSError) as e:
            if os.path.isfile(temp_mapping_file):
                os.remove(temp_mapping_file)
            sys.stderr.write('Failed to save {}: {}\n'.format(MAPPING, e))
            sys.exit(e.errno)
        else:
            temp_tags_file = DTAGS + '.tags'
            try:
                with open(temp_tags_file, 'w') as open_file:
                    open_file.write(
                        ' '.join(tag[1:] for tag in sorted(mapping))
                    )
            except (IOError, OSError) as e:
                for temp_file in [temp_mapping_file, temp_tags_file]:
                    if os.path.isfile(temp_file):
                        os.remove(temp_file)
                sys.stderr.write('Failed to save {}: {}\n'.format(TAGS, e))
                sys.exit(e.errno)
            else:
                os.remove(DTAGS)
                os.mkdir(DTAGS)
                os.rename(temp_tags_file, TAGS)
                os.rename(temp_mapping_file, MAPPING)
                print('Migration complete. You can now upgrade dtags!')
                sys.exit(0)

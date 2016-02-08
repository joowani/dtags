"""Directory Tags for Lazy Programmers."""

import os

SHELL = os.getenv('SHELL')
HOME = os.path.expanduser('~')
DTAGS_DIR = os.path.join(HOME, '.dtags')
TAGS_FILE = os.path.join(DTAGS_DIR, 'tags')
MAPPING_FILE = os.path.join(DTAGS_DIR, 'mapping')

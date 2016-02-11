"""
     ____  ______
    / __ \/_  __/___ _____ ______
   / / / / / / / __ `/ __ `/ ___/
  / /_/ / / / / /_/ / /_/ (__  )
 /_____/ /_/  \__,_/\__, /____/
                   /____/

Directory tags for lazy programmers.
By Joohwan Oh (github.com/joowani/dtags)
"""

import os

LOGO = __doc__

# Determine the home directory on runtime
HOME = os.path.expanduser('~')

# Configuration directory (i.e. ~/.dtags)
CFG_DIR = os.path.join(HOME, '.dtags')

# File containing just the tag names for tab completion
TAGS_FILE = os.path.join(CFG_DIR, 'tags')

# File containing the path-to-tag mapping
MAPPING_FILE = os.path.join(CFG_DIR, 'mapping')

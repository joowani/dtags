Features
========

**dtags** is a lightweight command line tool which lets you:

-  Tag and un-tag directories
-  Run commands in multiple directories in parallel
-  Change directories quickly via tag names
-  Use shell variables to reference directories
-  Easily manage git repositories, vagrant machines etc.


Installation
============

Check requirements:

-  Python 2.7+ or 3.4+
-  Recent version of `pip <https://pip.pypa.io>`__
-  Recent version of Bash, Zsh or Fish with tab-completion enabled

Install the package:

.. code:: bash

    # You may need to sudo depending on your setup
    ~$ pip install --upgrade dtags

Add the following line at the end of your shell runtime configuration and reload the shell:

.. code:: bash

    # For zsh, place in ~/.zshrc:
    command -v dtags-activate > /dev/null 2>&1 && eval "`dtags-activate zsh`"

    # For bash, place in ~/.bashrc (or ~/.bash_profile for OS X):
    command -v dtags-activate > /dev/null 2>&1 && eval "`dtags-activate bash`"

    # For fish, place in ~/.config/fish/config.fish:
    command -v dtags-activate > /dev/null 2>&1; and dtags-activate fish | source

Once installed, you will have the following at your disposal:

-  Utility commands ``t``, ``u``, ``d``, ``e``, ``p``
-  Main command ``dtags``

All commands come with tab-completion.


Usage
=====

Tag directories with ``t``:

.. code:: bash

    ~$ t ~/app dev work     # tag ~/app with 'dev' and 'work'
    ~$ t ~/app              # tag ~/app with its basename, 'app'

Un-tag directories with ``u``:

.. code:: bash

    ~$ u ~/app dev          # remove tag 'dev' from ~/app
    ~$ u ~/app              # remove all tags from ~/app

Change directories with ``d`` (designed to fully replace ``cd``!):

.. code:: bash

    ~$ d                    # go to the user's home directory
    ~$ d -                  # go to the last directory
    ~$ d app                # go to the directory tagged 'app'
    ~$ d ~/app              # go to directory ~/app

Execute commands in one or more directories with ``e``:

.. code:: bash

    ~$ e app git status     # execute 'git status' in all directories tagged 'app'
    ~$ e ~/vm vagrant halt  # regular directory paths are accepted as well
    ~$ e app,~/vm,~/foo ls  # multiple tags and/or paths can be specified using commas
    ~$ e -i app myalias     # use -i (interactive shell) to use functions, aliases etc.

Execute commands in parallel with ``p`` (same interface as ``e``):

.. code:: bash

    ~$ p app git pull       # execute 'git pull' in all directories tagged 'app' in parallel
    ~$ p -i app myalias     # again, use -i for interactive shell (read below for caveats)

Display, search and manage tags with ``dtags``:

.. code:: bash

    ~$ dtags                # display the directories-to-tags mapping
    ~$ dtags list ~ ~/vm    # list the tags and directories associated with ~ and ~/vm
    ~$ dtags list foo bar   # list the tags and directories associated with 'foo' or 'bar'
    ~$ dtags reverse        # list the tags-to-directories (reverse) mapping
    ~$ dtags edit           # edit tags and directories via editor
    ~$ dtags clean          # remove invalid or stale tags and directories
    ~$ dtags commands       # display all available dtags commands (e.g. t, u, d, e, p)


If a tag points to a single directory, shell variables are automatically created:

.. code:: bash

    ~$ t ~/some/dir foo     # shell variable '$foo' is automatically created
    ~$ ls $foo/sub/dir      # $foo can now be used to denote the tagged directory ~/some/dir
    ~$ rm $foo/file.sh      # $foo can now be used to denote the tagged directory ~/some/dir

You can always use the ``--help`` option to find out more about each command!

More Examples
=============

Streamline your Git workflows:

.. code:: bash

    # Tag your git directories
    ~$ t ~/project/mobile app
    ~$ t ~/project/backend app
    ~$ t ~/project/frontend app
    ~$ t ~/project/config app

    # Save yourself some time!
    ~$ e app git status
    ~$ p app git pull
    ~$ e app git checkout v1.7.2

Control multiple vagrant machines at the same time:

.. code:: bash

    # Tag all the things
    ~$ t ~/machines/web vm
    ~$ t ~/machines/redis vm
    ~$ t ~/machines/mysql vm
    ~$ t ~/machines/compute vm

    # Profit!
    ~$ p vm vagrant status
    ~$ p vm vagrant up


Technical Notes
===============

-  The directory-to-tags mapping is stored in ``~/.dtags/mapping``
-  Tags are also stored on their own in ``~/.dtags/tags`` for tab-completion
-  ``p`` is currently not fully supported on Windows
-  ``p`` cannot execute interactive commands that wait on input
-  ``p`` spawns child processes and redirects all output to temp files and then to stdout
-  ``p`` does not retain font colors due to shell limitations
-  ``p`` sends *sigterm* to its child processes when killed
-  ``e`` (or ``p``) uses environment variable **$SHELL** to guess which shell is in use
-  ``e`` (or ``p``) redirects stderr to stdout and always returns an exit status of 0
-  Using ``-i`` (interactive shell) has caveats:

   -  The shell runtime configuration must be "sourced" for every command execution
   -  The performance is affected by the shell startup time (beware oh-my-zsh users)
   -  Any errors thrown during the "sourcing" will be displayed in the output

-  ``dtags edit`` uses environment variable **$EDITOR**
-  ``d`` prefers tags over subdirectories when there are name conflicts

   -  To go to the subdirectory, put ``/`` after the directory name

-  ``d`` expects ``~/.dtags/mapping`` to be correctly formatted:

   -  Refrain from editing ``~/.dtags/mapping`` directly.
   -  Instead, use ``dtags edit`` which does the validation and formatting for you

-  Tab-completion expects ``~/.dtags/tags`` to be correctly formatted:

   -  Refrain from touching this file
   -  This file is auto-generated whenever a dtags command is run.
-  A shell variable is created only if its name does not conflict with environment variables
-  When shell variables are created, any hyphens in the name are replaced with underscores

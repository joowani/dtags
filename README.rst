Features
========

**dtags** is a lightweight command line tool which lets you:

-  Tag and un-tag directories
-  Automatically create shell variables for easy access
-  Change directories via tag names
-  Execute commands in multiple directories at the same time
-  Easily manage git repositories, vagrant machines etc.

All commands come with tab-completion.


Installation
============

**Step 1**: Check requirements:

-  Python 2.7+ or 3.4+
-  Recent version of `pip <https://pip.pypa.io>`__
-  Recent version of Bash, Zsh or Fish with tab-completion enabled

**Step 2**: Install the package:

.. code:: bash

    # You may need to sudo depending on your setup
    ~$ pip install --upgrade dtags

**Step 3**: Add the following line to your shell runtime configuration:

.. code:: bash

    # For zsh, place in ~/.zshrc:
    command -v dtags-activate > /dev/null 2>&1 && eval "`dtags-activate zsh`"

    # For bash, place in ~/.bashrc (or ~/.bash_profile for OS X):
    command -v dtags-activate > /dev/null 2>&1 && eval "`dtags-activate bash`"

    # For fish, place in ~/.config/fish/config.fish:
    command -v dtags-activate > /dev/null 2>&1; and dtags-activate fish | source

**Step 4**. Restart your shell.

Once installed, you will have **5** commands at your disposal: ``t``, ``u``,
``d``, ``e`` and ``dtags``. Make sure you don't have name conflicts with any
existing linux aliases, functions or symlinks etc.


Usage Examples
==============

Tag directories with ``t``:

.. code:: bash

    ~$ t ~/web dev work     # add tags 'dev' and 'work' to ~/web
    ~$ t ~/app              # tag ~/app with its basename, 'app'

Un-tag directories with ``u``:

.. code:: bash

    ~$ u ~/web dev          # remove tag 'dev' from ~/web
    ~$ u ~/app              # remove all tags from ~/app

Change directories with ``d`` (designed to fully replace ``cd``!):

.. code:: bash

    ~$ d                    # go to the user's home directory 
    ~$ d frontend           # go to the directory tagged 'frontend'
    ~$ d tag_with_many_dirs # prompt the user to select a specific directory         
    ~$ d ~/app              # go to directory ~/app

Execute commands in one or more directories with ``e``:

.. code:: bash

    ~$ e repo git status    # execute 'git status' in directories tagged 'repo'
    ~$ e ~/vm vagrant halt  # execute 'vagrant halt' in directory ~/vm
    ~$ e -p vm git pull     # execute 'git pull' in directories tagged 'vm' in parallel
    ~$ e vm,~/foo ls        # execute 'ls' in directories tagged 'vm' and ~/foo

Display, search and manage directory tags with ``dtags``:

.. code:: bash

    ~$ dtags                # display the directories-to-tags mapping
    ~$ dtags list ~ ~/vm    # display the tags and directories associated with ~ and ~/app
    ~$ dtags list foo bar   # display the tags and directories associated with 'foo' or 'bar'
    ~$ dtags reverse        # display the tags-to-directories mapping
    ~$ dtags edit           # edit tags and directories via editor like vim
    ~$ dtags clean          # remove invalid or stale tags and directories
    ~$ dtags commands       # display all available dtags commands

You can always use the ``--help`` option to find out more!

If a tag points to a single directory, shell variables are automatically created:

.. code:: bash

    ~$ t ~/some/dir test    # shell variable $test is automatically created
    ~$ ls $test/foo/bar     # $test can be used to denote the tagged directory
    ~$ rm $test/file.sh     # $test can be used to denote the tagged directory


Technical Notes
===============

-  The directory-to-tags mapping is stored in ``~/.dtags/mapping``
-  Tags are also stored on their own in ``~/.dtags/tags`` for tab-completion
-  ``e -p`` is currently not supported on Windows
-  ``e -p`` hangs on interactive commands that wait on input
-  ``e -p`` spawns child processes and redirects their output to
   temporary files and then to stdout
-  ``e -p`` sends *sigterm* to its child processes when killed
-  ``e`` uses environment variable **$SHELL** to guess which shell is in use
-  ``e`` redirects stderr to stdout and always return an exit status of 0
-  ``e`` uses *interactive shell*, which has pros and cons:

   -  The user has access to all linux functions and aliases
   -  The shell runtime configuration must be "sourced" each execution
   -  The performance of ``e`` is affected by the shell startup time
      (beware oh-my-zsh users)
   -  Any errors thrown during the "sourcing" will show up in the output

-  ``dtags edit`` uses environment variable **$EDITOR**
-  ``d`` prefers tags over subdirectories when there are name conflicts
   -  To go to the subdirectory, put a ``/`` after the directory name
-  ``d`` expects ``~/.dtags/mapping`` to be correctly formatted:

   -  Please refrain from editing ``~/.dtags/mapping`` directly
   -  Instead, use ``dtags edit`` which does the validation and
      formatting for you

-  Tab-completion expects ``~/.dtags/tags`` to be correctly formatted:

   -  Don't touch this file at all if possible
   -  If this is deleted, it is auto-generated the next time a dtags
      command is run.

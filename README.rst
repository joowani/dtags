Features
========

**dtags** is a lightweight command line tool which lets you:

-  Tag and un-tag directories
-  Change directories quickly via tag names
-  Run commands in multiple directories at once
-  Use shell variables to reference the tagged directories
-  Easily manage git repositories, vagrant machines etc.


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

**Step 3**: Add the following line at the end of your shell runtime configuration:

.. code:: bash

    # For zsh, place in ~/.zshrc:
    command -v dtags-activate > /dev/null 2>&1 && eval "`dtags-activate zsh`"

    # For bash, place in ~/.bashrc (or ~/.bash_profile for OS X):
    command -v dtags-activate > /dev/null 2>&1 && eval "`dtags-activate bash`"

    # For fish, place in ~/.config/fish/config.fish:
    command -v dtags-activate > /dev/null 2>&1; and dtags-activate fish | source

**Step 4**. Restart your shell.

Once installed, you will have **5** commands at your disposal: 
``t``, ``u``, ``d``, ``e`` and ``dtags``. All commands come with tab-completion.


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

Display, search and manage tags with ``dtags``:

.. code:: bash

    ~$ dtags                # display the directories-to-tags mapping
    ~$ dtags list ~ ~/vm    # display the tags and directories associated with ~ and ~/vm
    ~$ dtags list foo bar   # display the tags and directories associated with 'foo' or 'bar'
    ~$ dtags reverse        # display the tags-to-directories (reverse) mapping
    ~$ dtags edit           # edit tags and directories via editor like vim
    ~$ dtags clean          # remove invalid or stale tags and directories
    ~$ dtags commands       # display all available dtags commands (e.g. t, u, d, e)


If a tag points to a single directory, shell variables are automatically created:

.. code:: bash

    ~$ t ~/some/dir foo     # shell variable '$foo' is automatically created
    ~$ ls $foo/sub/dir      # $foo can now be used to denote the tagged directory ~/some/dir
    ~$ rm $foo/file.sh      # $foo can now be used to denote the tagged directory ~/some/dir

You can always use the ``--help`` option to find out more about each command!


Technical Notes
===============

-  The directory-to-tags mapping is stored in ``~/.dtags/mapping``
-  Tags are also stored on their own in ``~/.dtags/tags`` for tab-completion
-  ``e -p`` is currently not supported on Windows
-  ``e -p`` cannot execute interactive commands that wait on input
-  ``e -p`` spawns child processes and redirects their output to
   temporary files and then to stdout
-  ``e -p`` sends *sigterm* to its child processes when killed
-  ``e`` uses environment variable **$SHELL** to guess which shell is in use
-  ``e`` redirects stderr to stdout and always returns an exit status of 0
-  ``e`` uses *interactive shell* and this has pros and cons:

   -  The user has access to all linux functions and aliases
   -  The shell runtime configuration must be "sourced" each execution
   -  The performance of ``e`` is affected by the shell startup time
      (beware oh-my-zsh users)
   -  Any errors thrown during the "sourcing" will show up in the output

-  ``dtags edit`` uses environment variable **$EDITOR**
-  ``d`` prefers tags over subdirectories when there are name conflicts

   -  To go to the subdirectory, put a ``/`` after the directory name
   
-  ``d`` expects ``~/.dtags/mapping`` to be correctly formatted:

   -  Please refrain from editing ``~/.dtags/mapping`` directly.
   -  Instead, use ``dtags edit`` which does the validation and
      formatting for you

-  Tab-completion expects ``~/.dtags/tags`` to be correctly formatted:

   -  Don't touch this file at all if possible
   -  If this is deleted, it is auto-generated the next time a dtags
      command is run.
-  For a shell variable to be created automatically, the tag name must
   not conflict with environment variable names 
-  When shell variables are created hyphens are replaced with underscores

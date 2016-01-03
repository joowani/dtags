"""Formatter classes used with the argparse library."""

from argparse import RawDescriptionHelpFormatter, PARSER


class HelpFormatter(RawDescriptionHelpFormatter):
    """A small workaround to make command help menus look nicer.

    http://stackoverflow.com/questions/13423540/
        argparse-subparser-hide-metavar-in-command-listing
    """

    def _format_action(self, action):
        parts = super(RawDescriptionHelpFormatter, self)._format_action(action)
        if action.nargs == PARSER:
            parts = "\n".join(parts.split("\n")[1:])
        return parts

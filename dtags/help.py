"""DTags help formatter used with the argparse library."""

from argparse import PARSER, RawDescriptionHelpFormatter


class HelpFormatter(RawDescriptionHelpFormatter):
    """This makes help menus look a little bit nicer."""

    def _format_action(self, action):
        parts = super(RawDescriptionHelpFormatter, self)._format_action(action)
        if action.nargs == PARSER:
            return '\n'.join(parts.split('\n')[1:])
        return parts

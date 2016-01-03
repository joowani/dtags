"""Completer classes used with the argcomplete library."""


class ChoicesCompleter(object):
    """Completer initialized with a set of all possible choices."""

    def __init__(self, choices=None):
        self.choices = map(str, choices) if choices else []

    def __call__(self, prefix, **kwargs):
        return (c for c in self.choices if c.startswith(prefix))

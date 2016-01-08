"""All the things related to auto-completion."""

from argcomplete import CompletionFinder


class DTagsCompletionFinder(CompletionFinder):
    """Completion finder for DTags."""

    def _get_option_completions(self, parser, cword_prefix):
        """Skip auto-completion for optional arguments."""
        return []


class ChoicesCompleter(object):
    """Completer initialized with a set of all possible choices."""

    def __init__(self, choices=None):
        self.choices = map(str, choices) if choices else []

    def __call__(self, prefix, **kwargs):
        return (c for c in self.choices if c.startswith(prefix))

autocomplete = DTagsCompletionFinder()

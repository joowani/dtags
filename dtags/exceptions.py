"""DTags exceptions."""


class ParseError(ValueError):

    def __init__(self, filename, line_number, message):
        super(ParseError, self).__init__(
            'dtags: error: line {} in {}: {}'.format(
                line_number, filename, message
            )
        )

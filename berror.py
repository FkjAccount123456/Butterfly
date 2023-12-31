class BException(Exception):
    def __init__(self, msg: str = "", pos: tuple[int, int] | None = None):
        self.msg = msg
        self.pos = pos

    def __str__(self):
        if not self.msg:
            if self.pos:
                return "{} at line {}, column {}.".format(
                    type(self).__name__[1:], *self.pos
                )
            return "{}.".format(type(self).__name__[1:])
        if self.pos:
            return "{} at line {}, column {}: {}.".format(
                type(self).__name__[1:], *self.pos, self.msg
            )
        return "{}: {}.".format(type(self).__name__[1:], self.msg)


class BLexerError(BException):
    ...


class BParserError(BException):
    ...


class BNameError(BException):
    ...


class BTypeError(BException):
    ...

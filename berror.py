class BException(Exception):
    def __init__(self, ln: int, col: int, msg: str = ""):
        self.ln, self.col = ln, col
        self.msg = msg

    def __str__(self):
        if not self.msg:
            return "{} at line {}, column {}.".format(
                type(self).__name__[1:], self.ln, self.col)
        return "{} at line {}, column {}: {}.".format(
            type(self).__name__[1:], self.ln, self.col, self.msg)


class BLexerError(BException):
    ...


class BParserError(BException):
    ...


class BNameError(BException):
    ...


class BTypeError(BException):
    ...

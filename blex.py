from typing import Any, NamedTuple

from bdata import TokenType, op_map, keyword_map, escape_map
from berror import BLexerError


class Token(NamedTuple):
    ln: int
    col: int
    tp: TokenType
    val: Any = None


class Lexer:
    def __init__(self, code: str):
        self.code = code
        self.pos = 0
        self.ln, self.col = 1, 1

    def eof(self, n: int = 0):
        return self.pos + n >= len(self.code)

    def cur(self):
        return self.code[self.pos]

    def get(self, n: int = 1):
        return self.code[self.pos: self.pos + n]

    def next(self, n: int = 1):
        for _ in range(n):
            if self.eof():
                break
            if self.cur() == '\n':
                self.ln += 1
                self.col = 1
            else:
                self.col += 1

    def skip(self):
        while not self.eof() and (self.cur() in ' \n\t' or
                                  self.get(2) in ('//', '/*')):
            if self.get(2) == '//':
                while not self.eof() and self.cur() != '\n':
                    self.next()
            elif self.get(2) == '/*':
                self.next(2)
                while not self.eof() and self.get(2) != '*/':
                    self.next()
                if self.eof():
                    raise BLexerError(self.ln, self.col,
                                      "unexpected EOF in a long comment")
                self.next(2)
            else:
                self.next()

    def get_token(self):
        self.skip()

        if self.eof():
            return Token(self.ln, self.col, TokenType.EOF)
        elif self.cur().isdigit():
            num = self.cur()
            self.next()
            while not self.eof() and (self.cur().isdigit() or
                                      self.cur() == '.'):
                num += self.cur()
                self.next()
            if num.count('.') == 1:
                return Token(self.ln, self.col, TokenType.CONST, float(num))
            elif num.count('.') > 1:
                raise BLexerError(self.ln, self.col,
                                  "too many dots in a number")
            else:
                return Token(self.ln, self.col, TokenType.CONST, int(num))
        elif self.cur().isalpha() or self.cur() == '_':
            ident = self.cur()
            self.next()
            while not self.eof() and (
                    self.cur().isalnum() or self.cur() == '_'):
                ident += self.cur()
                self.next()
            if ident in keyword_map:
                return Token(self.ln, self.col, keyword_map[ident])
            elif ident == 'True':
                return Token(self.ln, self.col, TokenType.CONST, True)
            elif ident == 'False':
                return Token(self.ln, self.col, TokenType.CONST, False)
            elif ident == 'None':
                return Token(self.ln, self.col, TokenType.CONST, None)
            else:
                return Token(self.ln, self.col, TokenType.IDENT, ident)
        elif self.cur() in '\'"':
            x = self.cur()
            self.next()
            string = ""
            while not self.eof() and self.cur() != x:
                if self.cur() == '\\':
                    self.next()
                    if self.eof():
                        raise BLexerError(self.ln, self.col,
                                          "unexpected EOF in a string")
                    elif self.cur() in escape_map:
                        string += escape_map[self.cur()]
                        self.next()
                    elif self.cur() == 'x':
                        self.next()
                        if self.eof(2):
                            raise BLexerError(
                                self.ln, self.col,
                                "unexpected EOF in a string")
                        string += chr(int(self.get(2), 16))
                        self.next(2)
                    elif self.cur() == 'u':
                        self.next()
                        if self.eof(4):
                            raise BLexerError(
                                self.ln, self.col,
                                "unexpected EOF in a string")
                        string += chr(int(self.get(4), 16))
                        self.next(4)
                    else:
                        raise BLexerError(self.ln, self.col,
                                          "wrong escape sequence")
                else:
                    string += self.cur()
                    self.next()
            if self.eof():
                raise BLexerError(self.ln, self.col,
                                  "unexpected EOF in a string")
            self.next()
            return Token(self.ln, self.col, TokenType.CONST, string)
        elif not self.eof(2) and self.get(2) in op_map:
            op = op_map[self.get(2)]
            self.next(2)
            return Token(self.ln, self.col, op)
        elif self.cur() in op_map:
            op = op_map[self.cur()]
            self.next()
            return Token(self.ln, self.col, op)
        else:
            raise BLexerError(self.ln, self.col,
                              "unexpected character '{}'".format(self.cur()))

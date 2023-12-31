from typing import Any, NamedTuple

from bdata import TokenType, op_map, keyword_map, escape_map
from berror import BLexerError


class Token(NamedTuple):
    tp: TokenType
    val: Any = None
    pos: tuple[int, int] | None = None


class Lexer:
    def __init__(self, code: str):
        self.code = code
        self.pos = 0
        self.vpos = (1, 1)

    def eof(self, n: int = 0):
        return self.pos + n >= len(self.code)

    def cur(self):
        return self.code[self.pos]

    def get(self, n: int = 1):
        return self.code[self.pos : self.pos + n]

    def next(self, n: int = 1):
        for _ in range(n):
            if self.eof():
                break
            if self.cur() == "\n":
                self.vpos = (self.vpos[0] + 1, 1)
            else:
                self.vpos = (self.vpos[0], self.vpos[1] + 1)

    def skip(self):
        while not self.eof() and (self.cur() in " \n\t" or self.get(2) in ("//", "/*")):
            if self.get(2) == "//":
                while not self.eof() and self.cur() != "\n":
                    self.next()
            elif self.get(2) == "/*":
                self.next(2)
                while not self.eof() and self.get(2) != "*/":
                    self.next()
                if self.eof():
                    raise BLexerError("unexpected EOF in a long comment", self.vpos)
                self.next(2)
            else:
                self.next()

    def get_token(self):
        self.skip()

        if self.eof():
            return Token(TokenType.EOF, self.vpos)
        elif self.cur().isdigit():
            num = self.cur()
            self.next()
            while not self.eof() and (self.cur().isdigit() or self.cur() == "."):
                num += self.cur()
                self.next()
            if num.count(".") == 1:
                return Token(TokenType.CONST, float(num), self.vpos)
            elif num.count(".") > 1:
                raise BLexerError("too many dots in a number", self.vpos)
            else:
                return Token(TokenType.CONST, int(num), self.vpos)
        elif self.cur().isalpha() or self.cur() == "_":
            ident = self.cur()
            self.next()
            while not self.eof() and (self.cur().isalnum() or self.cur() == "_"):
                ident += self.cur()
                self.next()
            if ident in keyword_map:
                return Token(keyword_map[ident], self.vpos)
            elif ident == "True":
                return Token(TokenType.CONST, True, self.vpos)
            elif ident == "False":
                return Token(TokenType.CONST, False, self.vpos)
            elif ident == "None":
                return Token(TokenType.CONST, None, self.vpos)
            else:
                return Token(TokenType.IDENT, ident, self.vpos)
        elif self.cur() in "'\"":
            x = self.cur()
            self.next()
            string = ""
            while not self.eof() and self.cur() != x:
                if self.cur() == "\\":
                    self.next()
                    if self.eof():
                        raise BLexerError("unexpected EOF in a string", self.vpos)
                    elif self.cur() in escape_map:
                        string += escape_map[self.cur()]
                        self.next()
                    elif self.cur() == "x":
                        self.next()
                        if self.eof(2):
                            raise BLexerError("unexpected EOF in a string", self.vpos)
                        string += chr(int(self.get(2), 16))
                        self.next(2)
                    elif self.cur() == "u":
                        self.next()
                        if self.eof(4):
                            raise BLexerError("unexpected EOF in a string", self.vpos)
                        string += chr(int(self.get(4), 16))
                        self.next(4)
                    else:
                        raise BLexerError("wrong escape sequence", self.vpos)
                else:
                    string += self.cur()
                    self.next()
            if self.eof():
                raise BLexerError("unexpected EOF in a string", self.vpos)
            self.next()
            return Token(TokenType.CONST, string, self.vpos)
        elif not self.eof(2) and self.get(2) in op_map:
            op = self.get(2)
            self.next(2)
            return Token(op_map[op], op, self.vpos)
        elif self.cur() in op_map:
            op = self.cur()
            self.next()
            return Token(op_map[op], op, self.vpos)
        else:
            raise BLexerError("unexpected character '{}'".format(self.cur()), self.vpos)

from berror import BNameError
from blex import Token
from btype import *


class Scope:
    def __init__(self, parent: "Scope | None" = None):
        self.parent = parent
        self.variables = {}
        self.types = {}
        self.funcs = {}

    def findVar(self, name: Token):
        if name.val in self.variables:
            return self.variables[name.val]
        elif self.parent:
            return self.parent.findVar(name.val)
        else:
            raise BNameError(name.ln, name.col, "undefined variable '{}'".format(name.val))

    def findFunc(self, name: Token):
        if name.val in self.funcs:
            return self.funcs[name.val]
        elif self.parent:
            return self.parent.findVar(name.val)
        else:
            raise BNameError(name.ln, name.col, "undefined function '{}'".format(name.val))

    def findType(self, name: Token):
        if name.val in self.types:
            return self.types[name.val]
        elif self.parent:
            return self.parent.findType(name.val)
        else:
            raise BNameError(name.ln, name.col, "undefined function '{}'".format(name.val))

    def setVar(self, name: Token, value):
        if name.val in self.types:
            self.types[name.val] = value
        elif self.parent:
            self.parent.setVar(name, value)
        else:
            raise BNameError(name.ln, name.col, "undefined variable '{}'".format(name.val))


class RunSignal:
    RETURN, BREAK, CONTINUE = 0, 1, 2

    def __init__(self, signal, ret_value=None):
        self.signal, self.ret_value = signal, ret_value


class Stmt:
    def check(self, scope: Scope) -> Type | None:
        ...

    def visit(self, scope: Scope) -> RunSignal:
        ...


class Expr:
    def check(self, scope: Scope) -> Type:
        ...

    def visit(self) -> Any:
        ...

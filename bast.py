from berror import BNameError, BTypeError
from btype import *


class Scope:
    def __init__(self, parent: "Scope | None" = None):
        self.parent = parent
        self.variables = {}
        self.types = {}
        self.funcs = {}

    def findVar(self, ln: int, col: int, name: str):
        if name in self.variables:
            return self.variables[name]
        elif self.parent:
            return self.parent.findVar(ln, col, name)
        else:
            raise BNameError(ln, col, "undefined variable '{}'".format(name))

    def findFunc(self, ln: int, col: int, name: str):
        if name in self.funcs:
            return self.funcs[name]
        elif self.parent:
            return self.parent.findFunc(ln, col, name)
        else:
            raise BNameError(ln, col, "undefined function '{}'".format(name))

    def findType(self, ln: int, col: int, name: str):
        if name in self.types:
            return self.types[name]
        elif self.parent:
            return self.parent.findType(ln, col, name)
        else:
            raise BNameError(ln, col, "undefined function '{}'".format(name))

    def setVar(self, ln: int, col: int, name: str, value):
        if name in self.types:
            self.types[name] = value
        elif self.parent:
            self.parent.setVar(ln, col, name, value)
        else:
            raise BNameError(ln, col, "undefined variable '{}'".format(name))


class RunSignal:
    RETURN, BREAK, CONTINUE = 0, 1, 2

    def __init__(self, signal, ret_value=None):
        self.signal, self.ret_value = signal, ret_value


class Stmt:
    def __init__(self, ln: int, col: int):
        self.ln, self.col = ln, col

    def check(self, scope: Scope) -> Type | None:
        ...

    def visit(self, scope: Scope) -> RunSignal | None:
        ...


class Expr:
    def __init__(self, ln: int, col: int):
        self.ln, self.col = ln, col

    def check(self, scope: Scope) -> Type:
        ...

    def visit(self, scope: Scope) -> Any:
        ...


class Block(Stmt):
    def __init__(self, ln: int, col: int, stmts: list[Stmt]):
        super().__init__(ln, col)
        self.stmts = stmts

    def check(self, scope: Scope) -> Type | None:
        ret_type = None
        for stmt in self.stmts:
            ret = stmt.check(scope)
            if ret:
                if not ret_type:
                    ret_type = ret
                elif ret_type != ret:
                    raise BTypeError(self.ln, self.col, "conflicted type")
        return ret_type

    def visit(self, scope: Scope) -> RunSignal | None:
        for stmt in self.stmts:
            ret = stmt.visit(scope)
            if ret:
                return ret


class NoOp(Stmt):
    def __init__(self, ln: int, col: int):
        super().__init__(ln, col)


class ExprStmt(Stmt):
    def __init__(self, ln: int, col: int, expr: Expr):
        super().__init__(ln, col)
        self.expr = expr

    def check(self, scope: Scope) -> Type | None:
        self.expr.check(scope)
        return

    def visit(self, scope: Scope) -> RunSignal | None:
        self.expr.visit(scope)
        return


class VarDecl(Stmt):
    def __init__(self, ln: int, col: int, vardecls: list[tuple[str, Type, Expr]]):
        super().__init__(ln, col)
        self.vardecls = col, vardecls

    def check(self, scope: Scope) -> Type | None:
        for name, tp, _ in self.vardecls:
            if isinstance(tp, BasicType):
                scope.findType(self.ln, self.col, tp.name)
            scope.variables[name] = tp
        return

    def visit(self, scope: Scope) -> RunSignal | None:
        for name, tp, val in self.vardecls:
            if isinstance(tp, BasicType):
                tpdetail: TypeDetail = scope.findType(self.ln, self.col, tp.name)
                if val is None:
                    v = tpdetail.new()
                else:
                    v = val.visit(scope)
                scope.variables[name] = Value(tpdetail, v)
        return


class If(Stmt):
    def __init__(self, ln: int, col: int, cases: list[tuple[Expr, Block]], default: Block):
        super().__init__(ln, col)
        self.cases, self.default = cases, default

    def check(self, scope: Scope) -> Type | None:
        ret_type = None
        for cond, body in self.cases:
            cond.check(scope)
            ret = body.check(Scope(scope))
            if ret:
                if not ret_type:
                    ret_type = ret
                else:
                    raise BTypeError(self.ln, self.col, "conflicted type")
        ret = self.default.check(scope)
        if ret:
            if not ret_type:
                ret_type = ret
            else:
                raise BTypeError(self.ln, self.col, "conflicted type")
        return ret_type

    def visit(self, scope: Scope) -> RunSignal | None:
        for cond, body in self.cases:
            if cond.visit(scope):
                return body.visit(Scope(scope))
        return self.default.visit(Scope(scope))


class While(Stmt):
    def __init__(self, ln: int, col: int, cond: Expr, body: Block):
        super().__init__(ln, col)
        self.cond, self.body = cond, body

    def check(self, scope: Scope) -> Type | None:
        self.cond.check(scope)
        return self.body.check(Scope(scope))

    def visit(self, scope: Scope) -> RunSignal | None:
        while self.cond.visit(scope):
            ret = self.body.visit(Scope(scope))
            if isinstance(ret, RunSignal):
                if ret.signal == RunSignal.RETURN:
                    return ret
                if ret.signal == RunSignal.BREAK:
                    break
        return


class FuncDef(Stmt):
    def __init__(self, ln: int, col: int, name: str, params: list[str], param_types: list[Type], ret_type: Type, body: Block):
        super().__init__(ln, col)
        self.name, self.params, self.param_types, self.ret_type, self.body = name, params, param_types, ret_type, body

    def check(self, scope: Scope) -> Type | None:
        for param_type in self.param_types:
            if isinstance(param_type, BasicType):
                scope.findType(self.ln, self.col, param_type.name)
        register_name = self.name + " " + ' '.join(map(str, self.param_types))
        scope.funcs[register_name] = (self.ret_type, Func(self.params, self.body, scope))
        check_scope = Scope(scope)
        check_scope.variables = dict(zip(self.params, self.param_types))
        ret_type = self.body.check(check_scope)
        if ret_type != self.ret_type:
            raise BTypeError(self.ln, self.col, "conflicted type")
        return

    def visit(self, scope: Scope) -> RunSignal | None:
        register_name = self.name + " " + ' '.join(map(str, self.param_types))
        scope.funcs[register_name] = (self.ret_type, Func(self.params, self.body, scope))
        return


class Const(Expr):
    def __init__(self, ln: int, col: int, val: Any):
        super().__init__(ln, col)
        self.val = val

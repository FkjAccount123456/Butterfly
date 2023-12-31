from berror import BNameError, BTypeError
from btype import *
from btype import Scope, Type, Value


class Scope:
    def __init__(self, parent: "Scope | None" = None):
        self.parent = parent
        self.variables: dict[str, Any] = {}
        self.types: dict[str, TypeDetail] = {}
        self.funcs: dict[str, FuncDetail] = {}

    def findVar(self, name: str):
        if name in self.variables:
            return self.variables[name]
        elif self.parent:
            return self.parent.findVar(name)
        else:
            raise BNameError("undefined variable '{}'".format(name))

    def findFunc(self, name: str):
        if name in self.funcs:
            return self.funcs[name]
        elif self.parent:
            return self.parent.findFunc(name)
        else:
            raise BNameError("undefined function '{}'".format(name))

    def findType(self, name: str):
        if name in self.types:
            return self.types[name]
        elif self.parent:
            return self.parent.findType(name)
        else:
            raise BNameError("undefined function '{}'".format(name))

    def setVar(self, name: str, value):
        if name in self.types:
            self.types[name] = value
        elif self.parent:
            self.parent.setVar(name, value)
        else:
            raise BNameError("undefined variable '{}'".format(name))


class RunSignal:
    RETURN, BREAK, CONTINUE = 0, 1, 2

    def __init__(self, signal, ret_value=None):
        self.signal, self.ret_value = signal, ret_value


class Stmt:
    def __init__(self, pos: tuple[int, int] | None):
        self.pos = pos

    def check(self, scope: Scope) -> Type | None:
        ...

    def visit(self, scope: Scope) -> RunSignal | None:
        ...


class Expr:
    def __init__(self, pos: tuple[int, int] | None):
        self.pos = pos

    def check(self, scope: Scope) -> Type:
        ...

    def visit(self, scope: Scope) -> Value:
        ...


class Block(Stmt):
    def __init__(self, pos: tuple[int, int] | None, stmts: list[Stmt]):
        super().__init__(pos)
        self.stmts = stmts

    def check(self, scope: Scope) -> Type | None:
        ret_type = None
        for stmt in self.stmts:
            ret = stmt.check(scope)
            if ret:
                if not ret_type:
                    ret_type = ret
                elif ret_type != ret:
                    raise BTypeError("conflicted type", self.pos)
        return ret_type

    def visit(self, scope: Scope) -> RunSignal | None:
        for stmt in self.stmts:
            ret = stmt.visit(scope)
            if ret:
                return ret


class NoOp(Stmt):
    def __init__(self, pos: tuple[int, int] | None):
        super().__init__(pos)


class ExprStmt(Stmt):
    def __init__(self, pos: tuple[int, int] | None, expr: Expr):
        super().__init__(pos)
        self.expr = expr

    def check(self, scope: Scope) -> Type | None:
        self.expr.check(scope)
        return

    def visit(self, scope: Scope) -> RunSignal | None:
        self.expr.visit(scope)
        return


class VarDecl(Stmt):
    def __init__(self, pos: tuple[int, int] | None, vardecls: list[tuple[str, Type, Expr]]):
        super().__init__(pos)
        self.vardecls = vardecls

    def check(self, scope: Scope) -> Type | None:
        for name, tp, _ in self.vardecls:
            if isinstance(tp, BasicType):
                scope.findType(tp.name)
            scope.variables[name] = tp
        return

    def visit(self, scope: Scope) -> RunSignal | None:
        for name, tp, val in self.vardecls:
            if isinstance(tp, BasicType):
                tpdetail: TypeDetail = scope.findType(tp.name)
                if val is None:
                    v = tpdetail.new()
                else:
                    v = val.visit(scope)
                scope.variables[name] = Value(tpdetail, v)
        return


class If(Stmt):
    def __init__(self, pos: tuple[int, int] | None, cases: list[tuple[Expr, Block]], default: Block):
        super().__init__(pos)
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
                    raise BTypeError("conflicted type", self.pos)
        ret = self.default.check(scope)
        if ret:
            if not ret_type:
                ret_type = ret
            else:
                raise BTypeError("conflicted type", self.pos)
        return ret_type

    def visit(self, scope: Scope) -> RunSignal | None:
        for cond, body in self.cases:
            if cond.visit(scope):
                return body.visit(Scope(scope))
        return self.default.visit(Scope(scope))


class While(Stmt):
    def __init__(self, pos: tuple[int, int] | None, cond: Expr, body: Block):
        super().__init__(pos)
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
    def __init__(self, pos: tuple[int, int] | None, name: str, params: list[str], param_types: list[Type], ret_type: Type, body: Block):
        super().__init__(pos)
        self.name, self.params, self.param_types, self.ret_type, self.body = name, params, param_types, ret_type, body

    def check(self, scope: Scope) -> Type | None:
        for param_type in self.param_types:
            if isinstance(param_type, BasicType):
                scope.findType(param_type.name)
        register_name = self.name + " " + ' '.join(map(str, self.param_types))
        scope.funcs[register_name] = (self.ret_type, Func(self.params, self.body, scope))
        check_scope = Scope(scope)
        check_scope.variables = dict(zip(self.params, self.param_types))
        ret_type = self.body.check(check_scope)
        if ret_type != self.ret_type:
            raise BTypeError("conflicted type", self.pos)
        return

    def visit(self, scope: Scope) -> RunSignal | None:
        register_name = self.name + " " + ' '.join(map(str, self.param_types))
        scope.funcs[register_name] = (self.ret_type, Func(self.params, self.body, scope))
        return


class Const(Expr):
    def __init__(self, pos: tuple[int, int] | None, val: Any):
        super().__init__(pos)
        self.val = val

    def check(self, scope: Scope) -> Type:
        tp = type(self.val).__name__
        return {
            'int': BasicType('Int'),
            'float': BasicType('Float'),
            'bool': BasicType('Bool'),
            'str': BasicType('String'),
        }[tp]
    
    def visit(self, scope: Scope) -> Value:
        tp = type(self.val).__name__
        tp = {
            'int': 'Int',
            'float': 'Float',
            'bool': 'Bool',
            'str': 'String',
        }[tp]
        return Value(scope.findType(tp), self.val)
    

class Variable(Expr):
    def __init__(self, pos: tuple[int, int] | None, name: str):
        super().__init__(pos)
        self.name = name

    def check(self, scope: Scope) -> Type:
        return scope.findVar(self.name)
    
    def visit(self, scope: Scope) -> Value:
        return scope.findVar(self.name)
    

class BinaryOp(Expr):
    def __init__(self, pos: tuple[int, int] | None, op: str, left: Expr, right: Expr):
        super().__init__(pos)
        self.op, self.left, self.right = op, left, right

    def check(self, scope: Scope) -> Type:
        op = self.op
        left = self.left.check(scope)
        right = self.right.check(scope)
        left_detail = left.getDetail(scope)
        # right_detail = right.getDetail(scope)
        opname = "operator" + op + " this " + str(right)
        if left_detail.hasMethod(opname):
            return left_detail.getMethod(opname)[0]
        opname = "operator" + op + " " + str(left) + " " + str(right)
        return scope.findFunc(opname)[0]

    def visit(self, scope: Scope) -> Value:
        op = self.op
        left = self.left.visit(scope)
        right = self.right.visit(scope)
        opname = "operator" + op + " this " + str(right.tp.toType())
        if left.tp.hasMethod(opname):
            return left.tp.getMethod(opname)[1](left, right)
        opname = "operator" + op + " " + str(left.tp.toType()) + " " + str(right.tp.toType)
        return scope.findFunc(opname)[1](left, right)
    

class UnaryOp(Expr):
    def __init__(self, pos: tuple[int, int], op: str, val: Expr):
        super().__init__(pos)
        self.op, self.val = op, val

    def check(self, scope: Scope) -> Type:
        op = self.op
        val = self.val.check(scope)
        val_detail = val.getDetail(scope)
        opname = "operator" + op + " this"
        if val_detail.hasMethod(opname):
            return val_detail.getMethod(opname)[0]
        opname = "operator" + op + " " + str(val)
        return scope.findFunc(opname)[0]
    
    def visit(self, scope: Scope) -> Value:
        op = self.op
        val = self.val.visit(scope)
        opname = "operator" + op + " this"
        if val.tp.hasMethod(opname):
            return val.tp.getMethod(opname)[1](val)
        opname = "operator" + op + " " + str(val.tp.toType())
        return scope.findFunc(opname)[1](val)


class FuncCall(Expr):
    def __init__(self, pos: tuple[int, int], func: str, args: list[Expr]):
        super().__init__(pos)
        self.func, self.args = func, args

    def check(self, scope: Scope) -> Type:
        args = [i.check(scope) for i in self.args]
        funcname = self.func + " " + " ".join(map(str, args))
        func = scope.findFunc(funcname)
        return func[0]
    
    def visit(self, scope: Scope) -> Value:
        args = [i.visit(scope) for i in self.args]
        arg_types = [i.tp.toType() for i in args]
        funcname = self.func + " " + " ".join(arg_types)
        return scope.findFunc(funcname)[1](args)

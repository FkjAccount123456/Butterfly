import copy
from typing import Any, Callable
from bast import Block, Scope
from berror import BTypeError


class Type:
    def __eq__(self, _) -> bool:
        ...

    def __str__(self) -> str:
        ...

    def __repr__(self) -> str:
        return str(self)

    def getDetail(self, scope: Scope) -> "TypeDetail":
        ...


class BasicType(Type):
    def __init__(self, name: str):
        self.name = name

    def __eq__(self, other) -> bool:
        return isinstance(other, BasicType) and self.name == other.name

    def getDetail(self, scope: Scope) -> "TypeDetail":
        return scope.findType(self.name)


# 没错，一阶段不支持列表
# 等支持了泛型再说
'''class ListType(Type):
    def __init__(self, base: Type):
        self.base = base

    def __eq__(self, other) -> bool:
        return isinstance(other, ListType) and self.base == other.base'''


class TypeDetail:
    def __init__(self, name: str, methods: dict[str, "FuncDetail"], attrs: dict, parents: list["TypeDetail"]):
        # method的格式： 名称 参数类型列表 : (返回值, 主体)
        # 可恶，为什么时隔一年半还要用这种方式实现重载！
        # parents：继承一切+隐式转换
        self.name, self.method, self.attrs, self.parents = name, methods, attrs, parents

    def new(self) -> "Value":
        newobj = Value(self, self.getAttrs())
        # 什么？self.attrs某一项没有初值？去找解释器！
        if "operator init " in self.method:
            return self.method["operator init "][1](newobj)
        return newobj
    
    def getAttrs(self) -> dict:
        res = {}
        for i in self.parents:
            r = i.getAttrs()
            for k, v in r.items():
                res[k] = copy.deepcopy(v)
        for k, v in self.attrs.items():
            res[k] = copy.deepcopy(v)
        return res

    def hasMethod(self, name: str):
        if name in self.method:
            return True
        for i in self.parents:
            if i.hasMethod(name):
                return True
        return False
    
    def getMethod(self, name: str):
        if name in self.method:
            return self.method[name]
        for i in self.parents:
            if i.hasMethod(name):
                return i.getMethod(name)
        raise BTypeError(f"undefined method '{name}'")
    
    def toType(self):
        return self.name


class Value:
    def __init__(self, tp: TypeDetail, val: Any):
        self.tp, self.val = tp, val


class Func:
    def __init__(self, params: list[str], body: Block, closure: Scope):
        self.params, self.body, self.closure = params, body, closure

    def __call__(self, *args):
        new_scope = Scope(self.closure)
        new_scope.variables = dict(zip(self.params, args))
        ret = self.body.visit(new_scope)
        if ret:
            return ret


FuncDetail = tuple[Type, Callable]

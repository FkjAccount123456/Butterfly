from btype import *


def printFn(val: Value):
    print(val.val)


def operator_init_value_based(tp: TypeDetail):
    return lambda val: Value(tp, val)


def operator_init(tp: TypeDetail, val: Any):
    return lambda: Value(tp, val)


def binary_operator(tp: TypeDetail, op: str):
    return lambda a, b: Value(tp, getattr(a, op)(b))


def unary_operator(tp: TypeDetail, op: str):
    return lambda a: Value(tp, getattr(a, op)())


Bool = TypeDetail("Bool", {}, {}, [])
Int = TypeDetail("Int", {}, {}, [])
Int.method["operator init "] = (BasicType("Int"), operator_init(Int, 0))
Int.method["operator init Int"] = (BasicType("Int"), operator_init_value_based(Int))
Int.method["operator init String"] = (BasicType("Int"), lambda a: Value(Int, int(a)))
Int.method["operator+ this Int"] = (BasicType("Int"), binary_operator(Int, "__add__"))
Int.method["operator- this Int"] = (BasicType("Int"), binary_operator(Int, "__sub__"))
Int.method["operator* this Int"] = (BasicType("Int"), binary_operator(Int, "__mul__"))
Int.method["operator/ this Int"] = (
    BasicType("Int"),
    binary_operator(Int, "__truediv__"),
)
Int.method["operator% this Int"] = (BasicType("Int"), binary_operator(Int, "__mod__"))
Int.method["operator== this Bool"] = (
    BasicType("Bool"),
    binary_operator(Bool, "__eq__"),
)
Int.method["operator!= this Bool"] = (
    BasicType("Bool"),
    binary_operator(Bool, "__ne__"),
)
Int.method["operator> this Bool"] = (BasicType("Bool"), binary_operator(Bool, "__gt__"))
Int.method["operator< this Bool"] = (BasicType("Bool"), binary_operator(Bool, "__lt__"))
Int.method["operator>= this Bool"] = (
    BasicType("Bool"),
    binary_operator(Bool, "__ge__"),
)
Int.method["operator<= this Bool"] = (
    BasicType("Bool"),
    binary_operator(Bool, "__le__"),
)
Int.method["operator<< this Int"] = (
    BasicType("Int"),
    binary_operator(Int, "__lshift__"),
)
Int.method["operator>> this Int"] = (
    BasicType("Int"),
    binary_operator(Int, "__rshift__"),
)
Int.method["operator& this Int"] = (BasicType("Int"), binary_operator(Int, "__and__"))
Int.method["operator| this Int"] = (BasicType("Int"), binary_operator(Int, "__or__"))
Int.method["operator^ this Int"] = (BasicType("Int"), binary_operator(Int, "__xor__"))
Int.method["operator+ this"] = (BasicType("Int"), unary_operator(Int, "__pos__"))
Int.method["operator- this"] = (BasicType("Int"), unary_operator(Int, "__neg__"))
Int.method["operator~ this"] = (BasicType("Int"), unary_operator(Int, "__invert__"))

std_scope = Scope(None)

std_scope.funcs = {
    "print Int": (BasicType("None"), printFn),
    "print Float": (BasicType("None"), printFn),
    "print String": (BasicType("None"), printFn),
    "print Bool": (BasicType("None"), printFn),
}

std_scope.types = {
    "Int": Int,
}

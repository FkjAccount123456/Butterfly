"""
对类型系统的第一次测试
"""
from bast import *
from bbuiltins import std_scope

expr = BinaryOp(None, '+', Const(None, 1), Const(None, 1))
print(expr.check(std_scope))
print(expr.visit(std_scope))

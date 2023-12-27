from typing import Any


class Type:
    def __eq__(self, other) -> bool:
        ...

    def __str__(self) -> str:
        ...

    def __repr__(self) -> str:
        return str(self)


class BasicType(Type):
    def __init__(self, name: str):
        self.name = name

    def __eq__(self, other) -> bool:
        return isinstance(other, BasicType) and self.name == other.name


class ListType(Type):
    def __init__(self, base: Type):
        self.base = base

    def __eq__(self, other) -> bool:
        return isinstance(other, ListType) and self.base == other.base


class TypeDetail:
    def __init__(self, name: str, methods: dict, attrs: dict):
        self.name, self.method, self.attrs = name, methods, attrs


class Value:
    def __init__(self, tp: TypeDetail, val: Any):
        self.tp, self.val = tp, val

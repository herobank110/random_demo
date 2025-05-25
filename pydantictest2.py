# from abc import ABCMeta
from dataclasses import InitVar

# from inspect import Parameter, Signature, _ParameterKind
from typing import Any, dataclass_transform

# sig = Signature(
#     parameters=[
#         Parameter("hi", _ParameterKind.KEYWORD_ONLY, default=23, annotation=int),
#     ],
#     return_annotation=None,
# )


def my_field[T](*, default: T, init: bool = True) -> T:
    return default


@dataclass_transform(field_specifiers=(my_field,), kw_only_default=True)
class MyMetaclass(type):
    def __new__(mcs, name, bases, namespace, **kwargs):  # pyright: ignore
        # This is a placeholder for the metaclass logic.
        # You can modify the class creation process here if needed.
        cls = super().__new__(mcs, name, bases, namespace)  # pyright: ignore
        return cls
    # def __new__(mcs, name, bases, namespace, **kwargs):
    #     #     # namespace["__init__"] = my__init__
    #     cls = super().__new__(mcs, name, bases, namespace)
    #     cls.__init__ = my__init__
    #     cls.__init__.__signature__ = sig
    #     cls.__signature__ = sig
    #     return cls


# @dataclass_transform(field_specifiers=(my_field,), kw_only_default=True)
class MyClass(metaclass=MyMetaclass):
    # foo: InitVar[str | None] = None  # pyright: ignore[reportAssignmentType, reportRedeclaration]

    def __init__(self, **kwargs: Any) -> None:
        self._foo = kwargs.get("foo", "hi")

    def foo(self) -> str:
        return self._foo


class MyClass2(MyClass):
    hello: int = my_field(default=22)
    foo: InitVar[str | None] = None
    # f: Annotated[float, "Hello"]
    # _x: str = my_field(default="hi", init=False)
    # y = my_field(default=None)
    # __signature__ = sig


# print(MyClass2.__signature__)
# print(MyClass2().foo())
# print(MyClass2(foo="hello").foo())
MyClass2(hello=42).foo()
from inspect import signature

reveal_type(MyClass2)

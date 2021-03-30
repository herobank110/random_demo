from itertools import filterfalse
import re

ignore_pattern = re.compile("^__.*__$")

def _init_list(cls):
    fields = tuple(filterfalse(ignore_pattern.search, cls.__dict__))
    cls.__init__ = lambda self, *args, fields=fields: any(
            setattr(self, f, a) for f, a in zip(fields, args)) or None
    return cls

def _aggregate(cls):
    fields = set(filterfalse(ignore_pattern.search, cls.__dict__))
    init = lambda fields: lambda self, **kw: any(
            setattr(self, *fa)
            for fa in filter(lambda fa: fa[0] in fields, kw.items())) or None
    cls.__init__ = init(fields)
    return cls

class ctor:
    init_list = _init_list
    aggregate = _aggregate

@ctor.init_list
class S:
    a = 0
    b = 1
    c = "hi"

s = S(1, 2, "hello")
print("s.a =", s.a)
print("s.b =", s.b)
print("s.c =", s.c)

@ctor.aggregate
class S1:
    a = 0
    b = 1
    c = "hi"

s1 = S1(a=1, b=2, c="hello")
print("s1.a =", s1.a)
print("s1.b =", s1.b)
print("s1.c =", s1.c)

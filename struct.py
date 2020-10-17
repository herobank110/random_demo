from itertools import filterfalse
import re

ignore_pattern = re.compile("^__.*__$")

def generate_ctor(cls):
    fields = tuple(filterfalse(ignore_pattern.search, cls.__dict__))
    cls.__init__ = lambda self, *args, fields=fields: any(
            setattr(self, f, a) for f, a in zip(fields, args)) or None
    return cls

@generate_ctor
class S:
    a = 0
    b = 1
    c = "hi"

s = S(1, 2, "hello")
print("s.a =", s.a)
print("s.b =", s.b)
print("s.c =", s.c)

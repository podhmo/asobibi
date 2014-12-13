# -*- coding:utf-8 -*-
from functools import partial
from .construct import (
    gennil,
    _OptionHandler,
    VALIDATION_ERRORS,
    schema
)


class IncrementCounter(object):
    def __init__(self):
        self.i = 0

    def __call__(self):
        self.i += 1
        return self.i


_column_counter = IncrementCounter()


def column(fn, **options):
    g = partial(fn, **options)
    g._column_count = _column_counter()
    return g


def as_schema(missing=gennil,
              opt_handler=_OptionHandler,
              except_errors=VALIDATION_ERRORS):
    def wrapper(cls):
        xs = []
        for name, f in cls.__dict__.items():
            if hasattr(f, "_column_count"):
                xs.append((f._column_count, f(name)))
        fields = [v for _, v in sorted(xs, key=lambda x: x[0])]
        return schema(name, fields, cls.__mro__[0],
                      missing=missing,
                      opt_handler=opt_handler,
                      except_errors=except_errors)
    return wrapper

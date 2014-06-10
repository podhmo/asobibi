# -*- coding:utf-8 -*-
def _makeOne(*args, **kwargs):
    from asobibi.construct import schema
    return schema("Point", *args, **kwargs)

dummy = object()


def test_it():
    target = _makeOne([("x", dummy), ("y", dummy)])
    assert target.field_keys == ["x", "y"]


def test_it2():
    target = _makeOne([("a", dummy), ("b", dummy), ("c", dummy), ("z", dummy), ("y", dummy)])
    assert target.field_keys == ["a", "b", "c", "z", "y"]


def test_declrative():
    from asobibi.converters import Int
    from asobibi.construct import field
    from asobibi.declarative import as_schema, column

    IntegerField = field(converters=[Int])

    @as_schema
    class Point(object):
        x = column(IntegerField)
        y = column(IntegerField)

    assert Point.field_keys == ["x", "y"]

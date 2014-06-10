# -*- coding:utf-8 -*-
def _makeOne(*args, **kwargs):
    from asobibi.construct import schema
    return schema("Point", *args, **kwargs)


dummy = object()


def test_it():
    target = _makeOne([("x", dummy), ("y", dummy)])
    target.field_keys == ["x", "y"]


def test_it2():
    target = _makeOne([("a", dummy), ("b", dummy), ("c", dummy), ("z", dummy), ("y", dummy)])
    target.field_keys == ["a", "b", "c", "z", "y"]

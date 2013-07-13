from functools import wraps
from .exceptions import ValidationError

def Int(k, val):
    return int(val)
def Float(k, val):
    return float(val)
def String(k, val):
    return str(val)
def Unicode(k, val):
    return unicode(val)

def as_converter(schema):
    @wraps(schema)
    def converter(k, *args, **kwargs):
        return schema(*args, **kwargs)
    return converter

def as_validation(fn):
    @wraps(fn)
    def validate(k, x):
        fn(k, x)
        return x
    return validate

def validation_from_condition(cond, fmt="condition: {condition}({value!r}) is {result}"):
    @wraps(cond)
    def validate(k, value):
        result = cond(value)
        if not result:
            raise ValidationError(dict(fmt=fmt, field=k, result=result, value=value, condition=cond.__name__))
        return value
    return validate

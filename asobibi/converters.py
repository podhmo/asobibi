from functools import wraps

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

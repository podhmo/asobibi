class SymbolPool(object):
    def __init__(self,*ks):
        for k in ks:
            setattr(self,k,k)
        self._reserved = set(ks)
    
    def __contains__(self, k):
        return k in self._reserved

def merged(d1, d2):
    for k, v in d2.iteritems():
        if not k in d1:
            val = v
        else:
            val = d1[k][:]
            if hasattr(val, "append"):
                if isinstance(v, (tuple, list)):
                    val.extend(v)
                else:
                    val.append(v)
        d1[k] = val
    return d1
    

class mergeable(object):
    """ a realtive of functools.partial"""
    def __init__(self, fn, *args, **kwargs):
        self.fn = fn
        self.args = list(args)
        self.kwargs = kwargs

    def merged(self, **kwargs):
        original = merged(self.kwargs.copy(), kwargs)
        return self.__class__(self.fn, *self.args, **original)

    def __call__(self, *args, **kwargs):
        args_ = self.args[:]
        args_.extend(args)
        original = merged(self.kwargs.copy(), kwargs)
        return self.fn(*args_, **original)

def compose_rl(*fns):
    def wrapped(*args, **kwargs):
        rfns = reversed(fns)
        v = rfns.next()(*args, **kwargs)
        for f in rfns:
            v = f(v)
        return v
    return wrapped
compose = compose_rl


def flatten_dict(D, delimiter=".", factory=dict, result=None):
    result = factory()
    for k in D:
        _flatten_dict(D[k], delimiter, result, [k])
    return result

def _flatten_dict(val, delimiter, result, ks):
    if isinstance(val, (tuple, list)) and val and hasattr(val[0], "keys"):
        for v in val:
            for k in v:
                ks.append(k)
                _flatten_dict(v[k], delimiter, result, ks)
                ks.pop()
    elif hasattr(val, "keys"):
        for k in val:
            ks.append(k)
            _flatten_dict(val[k], delimiter, result, ks)
            ks.pop()
    else:
        result[delimiter.join(ks)] = val
    

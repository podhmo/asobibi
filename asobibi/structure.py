from collections import OrderedDict

class GentleDictMixin(object):
    def __repr__(self):
        return "<%r: %r>" % (self.__class__.__name__, self.items())
    def __getattr__(self, k):
        if k == "_OrderedDict__root":
            return OrderedDict.__getattr__(k)
        return self[k]

class Missing(object):
    def __nonzero__(self):
        return False
    def __init__(self,v):
        self.v = v
    def __repr__(self):
        return '<%r %r>' % (self.__class__.__name__, self.v)

class Failure(GentleDictMixin, OrderedDict):
    def __nonzero__(self):
        return False
    def __missing__(self, k):
        v = self[k] = Missing(k)
        return v
    def on_failure(self):
        return self

class Success(GentleDictMixin, OrderedDict):
    def on_failure(self):
        result = Failure()
        for k in self:
            result[k] = self[k]
        return result

class _Nil(object):
    def __nonzero__(self):
        return False
    def __str__(self):
        return "<Nil>"
def gennil(*args, **kwargs):
    return Nil

Nil = _Nil()

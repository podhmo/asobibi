from collections import OrderedDict
  
class GentleDictMixin(object):
    def __repr__(self):
        return "<%r: %r>" % (self.__class__.__name__, self.items())
    def __getattr__(self, k):
        if k == "_OrderedDict__root":
            return OrderedDict.__getattr__(k)
        return self[k]


class Failure(GentleDictMixin, OrderedDict):
    def __nonzero__(self):
        return False
    def __missing__(self, k):
        v = self[k] = Nil
        return v

class Success(GentleDictMixin, OrderedDict):
    def on_failure(self):
        result = Failure()
        for k in self:
            result[k] = self[k]
        return result

class _Nil(object):
    def __nonzero__(self):
        return False
def gennil(*args, **kwargs):
    return Nil

Nil = _Nil()


def getitem_not_nil(D, k):
    val = D[k]
    if val is Nil:
        raise KeyError("{0} ({1} is found)".format(k, Nil))
    return val


from collections import OrderedDict
from collections import Mapping

_dummy = object()
class ChainMapView(Mapping):
    def __init__(self, *candidates):
        self.candidates = candidates
        self.size = None
        self.ks = None

    def __getitem__(self, k):
        for c in self.candidates:
            v = c.get(k, _dummy)
            if not v is _dummy:
                return v
        raise KeyError(k)

    def configure(self):
        self.ks = ks = set()
        for c in self.candidates:
            for k in c:
                if k in ks:
                    continue
                ks.add(k)
        self.size = len(self.ks)

    def __iter__(self):
        if self.size is None:
            self.configure()
        for k in self.ks:
            yield k

    def __len__(self):
        if self.size is None:
            self.configure()
        return self.size

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

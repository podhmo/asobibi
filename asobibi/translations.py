# -*- coding:utf-8 -*-

from collections import namedtuple
from collections import defaultdict
from .langhelpers import warning
from .structure import ChainMapView
from functools import partial

_default = "default"
_system_lang = "system"
_display_lang = "display"

def dicttree():
    return defaultdict(dicttree)
_pool = dicttree()

class NotFound(Exception):
    pass
class MessageStringNotFound(NotFound):
    pass


class MessageString(namedtuple("MessageString", "fmt, mapping")):
    def __call__(self, mapping):
        return self.fmt.format(**ChainMapView(mapping, self.mapping))

def get_registry(category=None):
    global _pool
    category = category or _default
    return _pool[category]

def has_registry(category=_default):
    global _pool
    return category in _pool


def translate(name, mapping, category=None):
    global _system_lang
    registry = get_registry(category)
    try:
        return registry[_system_lang][name](mapping)
    except TypeError: #not callable
        raise MessageStringNotFound(name)            

def unicode_translate(name, mapping, category=None):
    global _display_lang
    registry = get_registry(category)
    try:
        return registry[_display_lang][name](mapping)
    except TypeError: #not callable
        raise MessageStringNotFound(name)            

def register(category, lang, name, fmt, mapping, force=False):
    registry = get_registry(category)[lang]
    if not force and name in registry:
        warning("{name} is already registered(category={category})".format(name=name, category=category))
    s = registry[name] = MessageString(fmt, mapping)
    return s

def get_system_message_factory(category=None, lang=None):
    global _default
    global _system_lang
    return partial(register, (category or _default), (lang or _system_lang))

def get_display_message_factory(category=None, lang=None):
    global _default
    global _display_lang
    return partial(register, (category or _default), (lang or _display_lang))
    
SystemMessage = get_system_message_factory()
DisplayMessage = get_display_message_factory()

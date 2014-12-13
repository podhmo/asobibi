from .translations import translate
from .translations import unicode_translate


class ConstructionError(Exception):
    pass


class InitializeError(Exception):
    pass


class ValidationError(Exception):

    def __str__(self):
        val = self.args[0]
        if "fmt" in val:
            return val["fmt"].format(**val)
        return translate(val["name"], val)

    def __unicode__(self):
        val = self.args[0]
        return unicode_translate(val["name"], val)

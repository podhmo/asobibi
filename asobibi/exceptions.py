class ConstructionError(Exception):
    pass

class InitializeError(Exception):
    pass

class ValidationError(Exception):
    def __str__(self):
        val = self.args[0]
        return val["fmt"].format(**val)

import inspect
from collections import defaultdict
from langhelpers import (
    SymbolPool, 
    mergeable, 
    ComfortableProperty, 
    Dispatch
)
from .structure import gennil, getitem_not_nil
from .structure import Success
from .exceptions import (
    ConstructionError,
    ValidationError,
    InitializeError
)


Op = SymbolPool(
    "initial",
    "required",
    "converters", 
    "label"
)

def _field(name, **options):
    for k in options:
        if not k in Op:
            raise ConstructionError("{0} is not reserved in Op ({0})".format(Op))
    return (name, options)

field = mergeable(_field).merged

class _OptionHandler(object):
    def __init__(self, options):
        self.options = options

    @classmethod
    def get_required(cls, options):
        return options.get(Op.required,True) 

    @classmethod       
    def get_converters(cls, options):
        return options.get(Op.converters, ())

    @classmethod
    def get_default_value(cls, options, on_missing, e):
        if Op.initial in options:
            return options[Op.initial]
        else:
            return on_missing(e)

VALIDATION_ERRORS = (AssertionError, TypeError, ValueError, ValidationError)
# hmm
def extract_message_from_exception(e):
    if isinstance(e, (str, unicode)):
        return e
    elif isinstance(e, Exception):
        return str(e)
    else:
        return e

def extract_message_raw(e):
    return e

def schema(name, fields, 
           base=object, 
           missing=gennil, 
           opt_handler=_OptionHandler,
           except_errors=VALIDATION_ERRORS, 
           extract_message=extract_message_from_exception):
    field_keys = [f for f, _ in fields]
    def __init__(self, _data=None, **data):
        rawdata = _data.copy() if _data else {}
        rawdata.update(data)
        for k, options in fields:
            try:
                rawdata[k]
            except KeyError as e:
                rawdata[k] = opt_handler.get_default_value(options, missing, e)
        self.rawdata = rawdata
        self.result = None
        self.errors = None
        self._configured = False #I hate this. want to remove.

    def on_failure(self, result, k, e):
        if self.errors is None:
            result = result.on_failure()
        if not self.errors:
            self.errors = defaultdict(list)
        self.errors[k].append(extract_message(e))
        return result

    def on_validate(self, result, k, val, options):
        result[k] = val
        for validator in opt_handler.get_converters(options):
            val = validator(k, val)
            ## field is schema
            if hasattr(val, "validate"):
                if not val.validate():
                    result = self.on_failure(result, k, val.errors)
                val = val.result
            result[k] = val
        return result

    def validate(self):
        if not self._configured:
            self.result = self._validate()
            self._configured = True
        return not self.errors
    
    def _validate(self):
        result = Success()
        for k, options in fields:
            try:
                val = getitem_not_nil(self.rawdata, k)
                result = self.on_validate(result, k, val, options)
            except KeyError as e:
                required = opt_handler.get_required(options)
                if required:
                    result = self.on_failure(result, k, e)
                else:
                    result[k] = self.rawdata[k]
            except except_errors as e:
                result = self.on_failure(result, k, e)
        return result

    def get_data(self):
        if self.result is None:
            return self.rawdata
        else:
            return self.result


    def rawdata_iter(self):
        rawdata = self.rawdata
        for f in field_keys:
            yield rawdata[f]

    def result_iter(self):
        result = self.result
        for f in field_keys:
            yield result[f]
        
    def __iter__(self):
        data = self.get_data()
        for f in self.field_keys:
            yield data[f]

    attrs = {"__iter__": __iter__,
             "rawdata_iter": rawdata_iter,
             "result_iter": result_iter,
             "__init__": __init__,
             "get_data": get_data, 
             "_fields": fields,
             "field_keys": field_keys, 
             "on_validate": on_validate, 
             "on_failure": on_failure,
             "_validate": _validate, 
             "validate": validate}

    def access_property(self, k):
        return self.get_data()[k]
    for f,_ in fields:
        attrs[f] = ComfortableProperty(f, access_property)
    return type(name, (base,), attrs)

WithExtra = Dispatch("extra")
Empty = object()

def default_apply_dispatch(fn, ks, result, extra_ks, extra):
    if WithExtra.is_tagged(fn):
        args = [result[k] for k in ks]
        kwargs = {}
        if hasattr(extra, "get"):
            kwargs = extra
        elif isinstance(extra, (list, tuple)):
            args.extend(extra)
        elif extra is not Empty:
            args.append(extra)
        return fn(ks[0], *args, **kwargs)
    else:
        return fn(ks[0], *(result[k] for k in ks))

def normalize(fields, validate_fn):
    """some. validation. and [ks, validator] -> [ks, extra_ks, validator]"""
    if not isinstance(fields,(tuple,list)):
        fields = (fields,)

    if len(fields) != len(set(fields)):
        raise ConstructionError("candidate fields name is conflicted.(len(fields) != len(set(fields))) fields={0}".format(fields))

    if WithExtra.is_tagged(validate_fn):
        spec = WithExtra.argspec(validate_fn)
    else:
        spec = inspect.getargspec(validate_fn)

    extra_fields = ()
    arity_from_schema_fields = len(fields)+1
    arity_from_validate_fn = len(spec.args)-len(spec.defaults or [])

    if arity_from_schema_fields > arity_from_validate_fn:
        raise ConstructionError("too many candidate fields. len({0})+1 > {1}".format(fields, arity_from_validate_fn))
    elif arity_from_schema_fields != arity_from_validate_fn:
        if not WithExtra.is_tagged(validate_fn):
            raise ConstructionError("too few candidate fields. len({0})+1 < {1}".format(fields, arity_from_validate_fn))
        extra_fields = spec.args[arity_from_schema_fields:]
    return fields, extra_fields, validate_fn, spec

def validator(name, _converters,
              base=object, 
              apply_dispatch=default_apply_dispatch,
              except_errors=VALIDATION_ERRORS):

    converters = [normalize(fields, validate_fn) for fields, validate_fn in _converters]

    def __init__(self, schema, extra=Empty, setup_check=True):
        self.schema = schema
        self.extra = extra
        if setup_check:
            self.setup_check()

    def setup_check(self):
        for _,  extra_fields, _, spec in converters:
            if extra_fields and self.extra is Empty:
                raise InitializeError("at least, {0} need extra data! ({1})".format(extra_fields, spec))
            for k in extra_fields:
                if not k in self.extra:
                    raise InitializeError("'{0}' is not found in extra. ({1})".format(k, spec))

    def validate(self):
        status = self.schema.validate()
        return status and self._validate()

    def _validate(self):
        result = self.result
        for fields, extra_fields, validator, _ in converters:
            if all(result.get(k,False) for k in fields):
                try:
                    apply_dispatch(validator, fields, result, extra_fields, self.extra)
                except except_errors as e:
                    result = self.on_failure(result, fields[0], e)
        self.result = result
        return self.schema.errors is None

    @property
    def result(self):
        return self.schema.result
    @result.setter
    def result(self, r):
        self.schema.result = r
    @property
    def errors(self):
        return self.schema.errors

    def on_failure(self,result, k, e):
        return self.schema.on_failure(result, k, e)

    return type(name,
                (base,),
                {"__init__": __init__,
                 "setup_check": setup_check, 
                 "_converters": converters,
                 "validate": validate,
                 "_validate": _validate,
                 "result": result,
                 "errors": errors,
                 "on_failure": on_failure})

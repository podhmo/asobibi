## feature

* support iteration, in definition order
* enable to register multiple value target validations
** if target field is optional, iff has truethy value called registered
* wrapping by decorator, multiply times
* validator and converter is same.
* compound schema

sample code

```py
from asobibi import (
    schema, 
    validator, 
    field, 
    Nil
)
import asobibi.converters as c
from asobibi.exceptions import ValidationError
```

validation definition

```py
def tiny_email(k, x):
    if not "@" in x:
        params = dict(field=k, value=x, fmt="{field} is not email address")
        raise ValidationError(params)
    return x

@c.validation_from_condition
def not_empty(x):
    return x != ""

Unicode = field(converters=[c.Unicode, not_empty])
```

schema definition

```py
Submit = schema(
    "Submit", 
    (Unicode("mail", initial="sample@mail", converters=[tiny_email]), 
     Unicode("password"), 
     Unicode("confirm")
 ))


submit = Submit(mail="foo", password="@", confirm="@")
assert submit.validate() == False

submit = Submit(mail="foo@bar.jp", password="@", confirm="@")
assert submit.validate()
assert submit.result["mail"] == "foo@bar.jp"
assert submit.password == "@"
assert submit.confirm == "@"
```


validator

```
def same(k, x, y):
    assert x == y

PasswordValidator = validator("PasswordValidator", 
                        [((Submit.password, Submit.confirm), same)])

submit = PasswordValidator(
    Submit(mail="foo@bar.jp", password="@", confirm="*"))

assert submit.validate() == False
assert submit.errors.keys() == ["password"]

## if validatation candidates fields are optional, then, registered validations are not called.
Submit2 = schema(
    "Submit", 
    (Unicode("mail", initial="sample@mail", converters=[tiny_email]), 
     Unicode("password", required=False), 
     Unicode("confirm", required=False)
 ))
submit = PasswordValidator(
    Submit2(mail="foo@bar.jp"))

assert submit.validate() == True

submit = PasswordValidator(
    Submit2(mail="foo@bar.jp", password=None, confirm=None))

assert submit.validate() == True
```

composed schema

```
from asobibi.langhelpers import compose

ExtendedSubmit = compose(PasswordValidator, Submit) 

submit = ExtendedSubmit(mail="foo@bar.jp", password="@", confirm="*")

assert submit.validate() == False
assert submit.errors.keys() == ["password"]
```

composed schema2

```py
Int = field(converters=[c.Int])
Person = schema("Person", [Unicode("name"), Int("age")])
Address = schema("Address", [
    Unicode("country", required=False), 
    Unicode("prefecture"), 
    Unicode("city")])

from asobibi import Op
Account = schema("Account", [("person", {Op.converters:[c.as_converter(Person)]}), 
                             ("address", {Op.converters:[c.as_converter(Address)]})])

account = Account({"person": {"name": "foo", "age": "20"}, 
                   "address": {"prefecture": "tokyo", "city": "somewhere"}})

assert account.validate()
assert dict(account.result) == {
    "person": {"name": "foo", "age": 20}, 
    "address": {"country": Nil, 
                "prefecture": "tokyo",
                "city": "somewhere"}
}

assert dict(account.person) == {"name": "foo", "age": 20}
assert dict(account.address) == {"country": Nil, 
                                 "prefecture": "tokyo",
                                 "city": "somewhere"}
```

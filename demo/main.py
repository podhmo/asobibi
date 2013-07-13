from asobibi import (
    schema, 
    validator, 
    field, 
    Nil
)
import asobibi.converters as c
from asobibi.exceptions import ValidationError

## validation definition

def tiny_email(k, x):
    if not "@" in x:
        params = dict(field=k, value=x, fmt="{field} is not email address")
        raise ValidationError(params)
    return x

@c.validation_from_condition
def not_empty(x):
    return x != ""

Unicode = field(converters=[c.Unicode, not_empty])


## schema definition

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


## validator definition
def same(k, x, y):
    assert x == y

PasswordValidator = validator("PasswordValidator", 
                        [((Submit.password, Submit.confirm), same)])

submit = PasswordValidator(
    Submit(mail="foo@bar.jp", password="@", confirm="*"))

assert submit.validate() == False
assert submit.errors.keys() == ["password"]


## composed schema

from asobibi.langhelpers import compose

ExtendedSubmit = compose(PasswordValidator, Submit) 

submit = ExtendedSubmit(mail="foo@bar.jp", password="@", confirm="*")

assert submit.validate() == False
assert submit.errors.keys() == ["password"]


## composed schema2

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

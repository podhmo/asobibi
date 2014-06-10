# -*- coding:utf-8 -*-
from asobibi import (
    as_schema,
    column,
    validator,
    field,
)
import asobibi.converters as c
from asobibi.exceptions import ValidationError


# Validation Definition
def tiny_email(k, x):
    if "@" not in x:
        params = dict(field=k, value=x, fmt="{field} is not email address")
        raise ValidationError(params)
    return x


@c.validation_from_condition
def not_empty(x):
    return x != ""


def same(k, x, y):
    assert x == y


# Field Definition
UnicodeField = field(converters=[c.Unicode, not_empty])


# Schema Definition
@as_schema()
class Submit(object):
    mail = column(UnicodeField, initial="sample@mail", converters=[tiny_email])
    password = column(UnicodeField)
    confirm = column(UnicodeField)


@as_schema()
class Submit2(object):
    mail = column(UnicodeField, initial="sample@mail", converters=[tiny_email])
    password = column(UnicodeField, required=False)
    confirm = column(UnicodeField, required=False)


PasswordValidator = validator("PasswordValidator", [((Submit.password, Submit.confirm), same)])


submit = Submit(mail="foo", password="@", confirm="@")
assert submit.validate() is False


submit = Submit(mail="foo@bar.jp", password="@", confirm="@")
assert submit.validate()

assert submit.result["mail"] == "foo@bar.jp"
assert submit.password == "@"
assert submit.confirm == "@"


submit = PasswordValidator(
    Submit(mail="foo@bar.jp", password="@", confirm="*"))

assert submit.validate() is False

assert list(submit.errors.keys()) == ["password"]


# # if validatation candidates fields are optional, then, registered validations are not called.


submit = PasswordValidator(
    Submit2(mail="foo@bar.jp"))


assert submit.validate() is True

submit = PasswordValidator(
    Submit2(mail="foo@bar.jp", password=None, confirm=None))

assert submit.validate() is True

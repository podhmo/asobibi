asobibi
========================================

background
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* iterate field with definition order
* bind validation about multiple value targets.
* wrapping by decorator, multiply times
* validator and converter is same.
* compound schema

sample code

.. code:: python

    from asobibi import (
        schema, 
        validator, 
        field, 
        Nil
    )
    import asobibi.converters as c
    from asobibi.exceptions import ValidationError

validation definition

.. code:: python

    def tiny_email(k, x):
        if not "@" in x:
            params = dict(field=k, value=x, fmt="{field} is not email address")
            raise ValidationError(params)
        return x

    @c.validation_from_condition
    def not_empty(x):
        return x != ""

    Unicode = field(converters=[c.Unicode, not_empty])

schema definition

.. code:: python

    Submit = schema(
        "Submit", 
        (Unicode("mail", initial="sample@mail", converters=[tiny_email]), 
         Unicode("password"), 
         Unicode("confirm")
     ))

    # try to use schema
    submit = Submit(mail="foo", password="@", confirm="@")
    assert submit.validate() == False

    submit = Submit(mail="foo@bar.jp", password="@", confirm="@")
    assert submit.validate()
    assert submit.result["mail"] == "foo@bar.jp"
    assert submit.password == "@"
    assert submit.confirm == "@"

using validator

.. code:: python

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


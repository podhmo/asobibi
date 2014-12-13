import pytest


class TestsSchemaFeature(object):
    def _getTarget(self):
        from asobibi import schema
        return schema

    # initialization
    def _getPointSchema(self):
        from asobibi import Op, Int
        target = self._getTarget()
        return target("Point", [("x", {Op.converters: [Int]}),
                                ("y", {Op.converters: [Int]})])

    def test_initialize_with_kwargs(self):
        point = self._getPointSchema()
        result = point(x=10, y=20)
        assert result.rawdata["x"] == 10
        assert result.rawdata["y"] == 20

    def test_initialize_with_dict(self):
        point = self._getPointSchema()
        result = point({"x": 10, "y": 20})
        assert result.rawdata["x"] == 10
        assert result.rawdata["y"] == 20

    # field property access
    def test_property__access_class(self):
        point = self._getPointSchema()
        assert point.x == "x"

    def test_property__access_object__pre_validate(self):
        point = self._getPointSchema()
        result = point({"x": "10", "y": "20"})
        assert result.x == "10"
        assert result.rawdata["x"] == "10"

    def test_property__access_object__post_validate(self):
        point = self._getPointSchema()
        result = point({"x": "10", "y": "20"})
        result.validate()
        assert result.x == 10
        assert result.result["x"] == 10

    # validation option
    def test_validate_multiple__always_True(self):
        from asobibi import Op
        Schema = self._getTarget()("Schema", [("x", {Op.required: True}),
                                              ("y", {Op.required: False})])
        target = Schema(x="10")
        assert target.validate() is True
        assert target.result
        assert target.errors is None
        assert target.validate() is True
        assert target.result
        assert target.errors is None

    def test_validate_multiple__always_False(self):
        from asobibi import Op
        from asobibi.construct import ErrorList
        Schema = self._getTarget()("Schema", [("x", {Op.required: True}),
                                              ("y", {Op.required: True})])
        target = Schema(x="20")
        assert target.validate() is not True
        assert target.result is not True

        import copy
        _errors = copy.deepcopy(dict(target.errors.copy()))
        assert target.validate() is not True
        assert target.result is not True
        assert str(target.errors) == str(ErrorList(_errors))

    # required option

    def test_validation_field_is_mandatory(self):
        from asobibi import Op
        from asobibi.structure import Missing
        Schema = self._getTarget()("Schema", [("x", {Op.required: True})])
        target = Schema()
        assert target.validate() is not True
        assert target.result is not True
        assert target.result["x"] is not True
        assert str(target.result["x"]) == str(Missing("x"))

    def test_validation_field_is_optional(self):
        from asobibi import Op
        from asobibi import Nil
        Schema = self._getTarget()("Schema", [("x", {Op.required: False})])
        target = Schema()
        assert target.x == Nil
        assert target.validate() is True
        assert target.result
        assert target.result["x"] == Nil

    def test_validation_field_is_optional__with_default(self):
        from asobibi import Op
        Schema = self._getTarget()("Schema", [("x", {Op.required: False, Op.initial: 0})])
        target = Schema()
        assert target.x == 0
        assert target.validate() is True
        assert target.result
        assert target.result["x"] == 0

    def test_validation_field_is_optional__convert_is_disabled(self):
        with pytest.raises(TypeError):
            int(None)

        from asobibi import Op, Int
        Schema = self._getTarget()("Schema", [("x", {Op.required: False, Op.converters: [Int], Op.initial:0})])
        target = Schema()
        assert target.validate() is True
        assert target.result
        assert target.result["x"] == 0

    def test_validation_field_is_optional__with_invalid_value(self):
        with pytest.raises(TypeError):
            int(None)

        from asobibi import Op, Int
        Schema = self._getTarget()("Schema", [("x", {Op.required: False, Op.converters: [Int], Op.initial:0})])
        target = Schema(x="a")
        assert target.validate() is not True
        assert target.result is not True
        assert target.result["x"] == "a"

    # ordered data

    def test_ordered(self):
        Schema = self._getTarget()("Schema", [("a0", {}), ("x1", {}), ("b0", {}), ("y1", {}), ("c0", {})])
        result = Schema(a0=1, b0=2, c0=3, x1=10, y1=20)
        assert list(result.rawdata_iter()) == [1, 10, 2, 20, 3]
        assert list(result) == [1, 10, 2, 20, 3]

    def test_ordered__validated_data(self):
        from asobibi import Op, Int
        Schema = self._getTarget()("Schema", [("a0", {Op.converters: [Int]}), ("x1", {}), ("b0", {Op.converters: [Int]}), ("y1", {}), ("c0", {Op.converters: [Int]})])
        result = Schema(a0="1", b0="2", c0="3", x1=10, y1=20)
        assert list(result) == ["1", 10, "2", 20, "3"]
        assert result.validate() is True
        assert list(result.result_iter()) == [1, 10, 2, 20, 3]
        assert list(result) == [1, 10, 2, 20, 3]


class TestsSchemaPartial(object):
    def _getTarget(self):
        from asobibi import schema
        return schema

    def test_it(self):
        schema = self._getTarget()
        Schema = schema("Schema", [("a", {}), ("b", {}), ("c", {}), ("d", {})])

        complete = Schema(a=1)
        assert complete.validate() is not True

        partial = Schema.partial(a=1)
        assert partial.validate() is True
        assert dict(partial.result) == {"a": 1}


class TestsValidatorExtraData(object):
    def _get_schema(self):
        from asobibi import schema
        return schema("Schema", [("val", {})])

    def _getTarget(self):
        from asobibi import validator
        return validator

    # on setup phase
    def test_using_field_name_is_conflicted(self):
        from asobibi import ConstructionError
        Schema = self._get_schema()
        with pytest.raises(ConstructionError) as e:
            e.expected_regexp = "conflict"
            self._getTarget()("Validator", [((Schema.val, Schema.val), lambda k, val: True)])

    def test_using_too_many_field(self):
        from asobibi import ConstructionError
        from asobibi import schema
        Schema = schema("Schema", [("val0", {}), ("val1", {})])
        with pytest.raises(ConstructionError) as e:
            e.expected_regexp = "too many"
            self._getTarget()("Validator", [((Schema.val0, Schema.val1), lambda k, val0: True)])

    def test_using_too_few_field(self):
        from asobibi import ConstructionError
        Schema = self._get_schema()
        with pytest.raises(ConstructionError) as e:
            e.expected_regexp = "too few"
            self._getTarget()("Validator", [((Schema.val), lambda k, val, extra: True)])

    def test_using_too_few_field__with_extra_data(self):
        from asobibi import WithExtra
        Schema = self._get_schema()
        self._getTarget()("Validator", [((Schema.val), WithExtra(lambda k, val, extra: True))])

    # on initialize phase
    def test_it(self):
        from asobibi import WithExtra
        Schema = self._get_schema()
        Validator = self._getTarget()("Validator", [((Schema.val), WithExtra(lambda k, val, extra: True))])

        target = Schema(val="a")
        result = Validator(target, {"extra": ">_<"})
        assert result.validate() is True

    def test_with_extra__missing(self):
        from asobibi import WithExtra
        from asobibi import InitializeError
        Schema = self._get_schema()
        Validator = self._getTarget()("Validator", [((Schema.val), WithExtra(lambda k, val, extra: True))])

        target = Schema(val="a")
        with pytest.raises(InitializeError) as e:
            e.expected_regexp = "need extra data!"
            Validator(target)

    def test_with_extra__dict_but_other_values(self):
        from asobibi import WithExtra
        from asobibi import InitializeError
        Schema = self._get_schema()
        Validator = self._getTarget()("Validator", [((Schema.val), WithExtra(lambda k, val, extra: True))])

        target = Schema(val="a")
        with pytest.raises(InitializeError) as e:
            e.expected_regexp = "'extra' is not found"
            Validator(target, {"other": "other-argument"})

    def test_with_extra__default_value(self):
        from asobibi import WithExtra
        Schema = self._get_schema()

        @WithExtra
        def v(k, val, extra=None):
            raise Exception("called. and validation error")
        Validator = self._getTarget()("Validator", [((Schema.val), v)])

        target = Schema(val="a")
        target = Validator(target)
        with pytest.raises(Exception) as e:
            e.expected_regexp = "called. and validation error"
            target.validate()

    # validation with extra data
    def _get_schema__point(self):
        from asobibi import schema
        from asobibi import Op, Int

        def positive(k, x):
            assert x >= 0
            return x
        return schema("Point", [("x", {Op.converters: [Int]}),
                                ("y", {Op.converters: [Int, positive]}), ])

    def _get_validator__with_extra_data(self, Point):
        from asobibi import validator
        from asobibi import WithExtra
        from asobibi import ValidationError

        def validation_with_extradata(_, x, y, z=0):
            if x * x + y * y != z * z:
                raise ValidationError({"fmt": "not x^2 + y^2 == z^2 ({0} != {1})".format(x * x + y * y, z * z)})

        return validator("Validator",
                         [((Point.x, Point.y), WithExtra(validation_with_extradata))])

    def test_validate__with_extra_data__success(self):
        Point = self._get_schema__point()
        point = Point(x=3, y=4)
        point = self._get_validator__with_extra_data(Point)(point, 5)
        assert point.validate() is True

    def test_validate__with_extra_data__success2(self):
        Point = self._get_schema__point()
        point = Point(x=3, y=4)
        point = self._get_validator__with_extra_data(Point)(point, extra=[5])
        assert point.validate() is True

    def test_validate__with_extra_data__success3(self):
        Point = self._get_schema__point()
        point = Point(x=3, y=4)
        point = self._get_validator__with_extra_data(Point)(point, extra={"z": 5})
        assert point.validate() is True

    def test_validate__with_extra_data__failure(self):
        from asobibi.construct import ErrorList
        Point = self._get_schema__point()
        point = Point(x=3, y=10)
        point = self._get_validator__with_extra_data(Point)(point, 5)
        assert point.validate() is not True
        assert str(point.errors) == str(ErrorList({"x": ['not x^2 + y^2 == z^2 (109 != 25)']}))

    def test_validate__with_extra_data__missing_arguments(self):  # xxx:
        from asobibi.construct import ErrorList
        Point = self._get_schema__point()
        point = Point(x=3, y=10)
        point = self._get_validator__with_extra_data(Point)(point)
        assert point.validate() is not True
        assert str(point.errors) == str(ErrorList({"x": ['not x^2 + y^2 == z^2 (109 != 0)']}))


class TestsNestedValidator(object):
    def _get_schema(self):
        from asobibi import schema
        from asobibi import Op, Int

        def positive(k, x):
            assert x >= 0
            return x
        return schema("Point", [("x", {Op.converters: [Int]}),
                                ("y", {Op.converters: [Int, positive]}), ])

    def _get_validator__ordered(self):
        from asobibi import validator

        def ordered(k, x, y):
            assert x < y
            return x
        return validator("FstValidator", [(("x", "y"), ordered)])

    def _get_validator__bigger(self):
        from asobibi import validator

        def bigger(k, x, y):
            assert x * x + y * y > 100
        return validator("SndValidator", [(("x", "y"), bigger)])

    def test_schema__success(self):
        point = self._get_schema()(x=10, y="20")

        assert point.validate() is True
        assert point.result
        assert point.result["x"] == 10
        assert point.result["y"] == 20

    def test_schema__failure(self):
        point = self._get_schema()(x=10, y="-20")

        assert point.validate() is not True
        assert point.result is not True
        assert point.result["x"] == 10
        assert point.result["y"] == -20

    def test_validator__success(self):
        point = self._get_schema()(x=10, y="20")
        point = self._get_validator__ordered()(point)

        assert point.validate() is True
        assert point.result
        assert point.result["x"] == 10
        assert point.result["y"] == 20

    def test_validator__failure(self):
        point = self._get_schema()(x=30, y="20")
        point = self._get_validator__ordered()(point)

        assert point.validate() is not True
        assert point.result is not True
        assert point.result["x"] == 30
        assert point.result["y"] == 20

    def test_nested_validator__success(self):
        point = self._get_schema()(x=10, y="20")
        point = self._get_validator__ordered()(point)
        point = self._get_validator__bigger()(point)

        assert point.validate() is True
        assert point.result
        assert point.result["x"] == 10
        assert point.result["y"] == 20

    def test_nested_validator__failure(self):
        point = self._get_schema()(x=1, y="2")
        point = self._get_validator__ordered()(point)
        point = self._get_validator__bigger()(point)

        assert point.validate() is not True
        assert point.result is not True
        assert point.result["x"] == 1
        assert point.result["y"] == 2

    def test_nested_validator__failure2(self):
        point = self._get_schema()(x=1, y="2")
        point = self._get_validator__bigger()(point)
        point = self._get_validator__ordered()(point)

        assert point.validate() is not True
        assert point.result is not True
        assert point.result["x"] == 1
        assert point.result["y"] == 2

    def test_nested_validator__all(self):
        from asobibi import validator, ValidationError
        from asobibi.construct import ErrorList
        Schema = self._get_schema()

        def odd(k, x):
            if x % 2 != 1:
                raise ValidationError(dict(fmt="not odd, {field}", field=k))
        point = self._get_schema()(x="10", y="20")
        point = self._get_validator__bigger()(point)
        point = self._get_validator__ordered()(point)
        point = validator("Vx", [(Schema.x, odd)])(point)
        point = validator("Vy", [(Schema.y, odd)])(point)

        assert point.validate() is not True
        assert point.result is not True
        assert str(point.errors) == str(ErrorList({'y': ['not odd, y'], 'x': ['not odd, x']}))


class TestsComplexSchema(object):
    def _getComplexSchema(self):
        from asobibi import schema
        from asobibi import Op, Unicode, as_converter

        def capitalize(k, string):
            return u"".join(x.capitalize() for x in string.split("-"))

        Address = schema("Address",
                         [("prefecture", {Op.converters: [Unicode, capitalize]}),
                          ("city", {Op.converters: [Unicode, capitalize]}),
                          ("address_1", {}),
                          ("address_2", {Op.required: False, Op.initial: None}),
                          ])

        Person = schema("Person",
                        [("first_name", {Op.converters: [Unicode, capitalize]}),
                         ("last_name", {Op.converters: [Unicode, capitalize]})])

        Account = schema("Account",
                         [("person", {Op.converters: [as_converter(Person)]}),
                          ("address", {Op.converters: [as_converter(Address)]})])
        return Account

    def test_failure(self):
        schema = self._getComplexSchema()
        target = schema()
        assert target.validate() is not True

    def test_failure2(self):
        schema = self._getComplexSchema()
        target = schema({"person":
                         {"first_name": "first-name"},
                         "address":
                         {"prefecture": "tokyo"}})
        assert target.validate() is not True

    def test_it(self):
        schema = self._getComplexSchema()
        target = schema({"person":
                         {"first_name": "first-name",
                          "last_name": "last-name", },
                         "address":
                         {"prefecture": "tokyo",
                          "city": "chiyoda-ku",
                          "address_1": "chiyoda 1-1",
                          }
                         })
        assert target.validate() is True
        assert target.result ==\
            {"person":
             {"first_name": "FirstName",
              "last_name": "LastName", },
             "address":
             {"prefecture": "Tokyo",
              "city": "ChiyodaKu",
              "address_1": "chiyoda 1-1",
              "address_2": None}
            }


class TestsDeepNest(object):

    def _get_A(self):
        from asobibi import schema
        from asobibi import Op, Unicode, as_converter
        Pair = schema("Pair", [("left", {Op.converters: [Unicode, lambda k, x: x.capitalize()]}),
                               ("right", {Op.converters: [Unicode, lambda k, x: x.capitalize()]}),
                               ])
        E = schema("E", [("f", {Op.converters: [as_converter(Pair)]})])
        D = schema("D", [("e", {Op.converters: [as_converter(E)]})])
        C = schema("C", [("d", {Op.converters: [as_converter(D)]})])
        B = schema("B", [("c", {Op.converters: [as_converter(C)]})])
        A = schema("A", [("b", {Op.converters: [as_converter(B)]})])
        return A

    def test_access_property__class(self):
        A = self._get_A()
        assert A.b == "b"

    def test_access_property__object__pre_validate(self):
        A = self._get_A()
        a = A({"b": {"c": {"d": {"e": {"f": {"left": "xxxx", "right": "yyyy"}}}}}})
        assert a.b == {"c": {"d": {"e": {"f": {"left": "xxxx", "right": "yyyy"}}}}}

        with pytest.raises(AttributeError):
            assert a.b.c.d.e.f.left == "xxxx"
            assert a.b.c.d.e.f.right == "yyyy"

    def test_access_property__object__post_validate(self):
        A = self._get_A()
        a = A({"b": {"c": {"d": {"e": {"f": {"left": "xxxx", "right": "yyyy"}}}}}})
        assert a.validate() is True
        assert a.b.c.d.e.f.left == "Xxxx"
        assert a.b.c.d.e.f.right == "Yyyy"

    def test_deep_nested__success(self):
        A = self._get_A()
        a = A({"b": {"c": {"d": {"e": {"f": {"left": "xxxx", "right": "yyyy"}}}}}})
        assert a.validate() is True
        assert a.result == {"b": {"c": {"d": {"e": {"f": {"left": "Xxxx", "right": "Yyyy"}}}}}}
        assert a.errors is None

    def test_deep_nested__failure(self):
        A = self._get_A()
        a = A({"b": {"c": {"d": {"F": {"f": {"left": "xxxx", "right": "yyyy"}}}}}})
        assert a.validate() is not True
        assert a.result is not True

        from asobibi.langhelpers import flatten_dict
        assert list(flatten_dict(a.errors).keys()) == ["b.c.d.e"]

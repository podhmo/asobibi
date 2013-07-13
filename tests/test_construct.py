import unittest

class ComfortablePropertyTests(unittest.TestCase):
    def _getTargetClass(self):
        from asobibi import ComfortableProperty
        class A(object):
            def __init__(self, **kwargs):
                self.data = kwargs
            def square(o, k):
                v = o.data[k]
                return v * v
            a = ComfortableProperty("a", square)
        return A

    def _makeOne(self, *args, **kwargs):
        return self._getTargetClass()(*args, **kwargs)

    def test_access_from_class(self):
        target = self._getTargetClass()
        self.assertEqual(target.a, "a")

    def test_access_from_object(self):
        target = self._makeOne(a=10)
        self.assertEqual(target.a, 100)

class SchemaFeatureTests(unittest.TestCase):
    def _getTarget(self):
        from asobibi import schema
        return schema

    ## initialization
    def _getPointSchema(self):
        from asobibi import Op, Int
        target = self._getTarget()
        return target("Point", [("x", {Op.converters:[Int]}), 
                                ("y", {Op.converters:[Int]})])
        
    def test_initialize_with_kwargs(self):
        point = self._getPointSchema()
        result = point(x=10,y=20)
        self.assertEquals(result.rawdata["x"],10)
        self.assertEquals(result.rawdata["y"],20)

    def test_initialize_with_dict(self):
        point = self._getPointSchema()
        result = point({"x": 10, "y": 20})
        self.assertEquals(result.rawdata["x"],10)
        self.assertEquals(result.rawdata["y"],20)

    ## field property access
    def test_property__access_class(self):
        point = self._getPointSchema()
        self.assertEqual(point.x, "x")

    def test_property__access_object__pre_validate(self):
        point = self._getPointSchema()
        result = point({"x": "10", "y": "20"})
        self.assertEqual(result.x, "10")
        self.assertEqual(result.rawdata["x"], "10")

    def test_property__access_object__post_validate(self):
        point = self._getPointSchema()
        result = point({"x": "10", "y": "20"})
        result.validate()
        self.assertEqual(result.x, 10)
        self.assertEqual(result.result["x"], 10)

    ## required option

    def test_validation_field_is_mandatory(self):
        from asobibi import Op
        from asobibi import Nil
        Schema = self._getTarget()("Schema", [("x", {Op.required:True})])
        target = Schema()
        self.assertFalse(target.validate())
        self.assertFalse(target.result["x"])
        self.assertEqual(target.result["x"], Nil)

    def test_validation_field_is_optional(self):
        from asobibi import Op
        from asobibi import Nil
        Schema = self._getTarget()("Schema", [("x", {Op.required:False})])
        target = Schema()
        self.assertEqual(target.x, Nil)
        self.assertTrue(target.validate())
        self.assertEqual(target.result["x"], Nil)

    def test_validation_field_is_optional__with_default(self):
        from asobibi import Op
        Schema = self._getTarget()("Schema", [("x", {Op.required:False, Op.initial:0})])
        target = Schema()
        self.assertEqual(target.x, 0)
        self.assertTrue(target.validate())
        self.assertEqual(target.result["x"], 0)

    def test_validation_field_is_optional__convert_is_disabled(self):
        with self.assertRaises(TypeError):
            int(None)

        from asobibi import Op, Int
        Schema = self._getTarget()("Schema", [("x", {Op.required:False, Op.converters:[Int], Op.initial:0})])
        target = Schema()
        self.assertTrue(target.validate())
        self.assertEqual(target.result["x"], 0)

    def test_validation_field_is_optional__with_invalid_value(self):
        with self.assertRaises(TypeError):
            int(None)

        from asobibi import Op, Int
        Schema = self._getTarget()("Schema", [("x", {Op.required:False, Op.converters:[Int], Op.initial:0})])
        target = Schema(x="a")
        self.assertFalse(target.validate())
        self.assertEqual(target.result["x"], "a")

    ## ordered data

    def test_ordered(self):
        Schema = self._getTarget()("Schema", [("a0",{}),("x1",{}),("b0", {}),("y1",{}),("c0",{})])
        result = Schema(a0=1,b0=2,c0=3,x1=10,y1=20)
        self.assertEquals(list(result.rawdata_iter()),[1,10,2,20,3])
        self.assertEquals(list(result),[1,10,2,20,3])
        
    def test_ordered__validated_data(self):
        from asobibi import Op, Int
        Schema = self._getTarget()("Schema", [("a0",{Op.converters:[Int]}),("x1",{}),("b0", {Op.converters:[Int]}),("y1",{}),("c0",{Op.converters:[Int]})])
        result = Schema(a0="1",b0="2",c0="3",x1=10,y1=20)
        self.assertEquals(list(result),["1",10,"2",20,"3"])
        self.assertTrue(result.validate())
        self.assertEquals(list(result.result_iter()),[1,10,2,20,3])
        self.assertEquals(list(result),[1,10,2,20,3])
      
class ValidatorExtraDataTests(unittest.TestCase):
    def _get_schema(self):
        from asobibi import schema
        return schema("Schema",[("val",{})])

    def _getTarget(self):
        from asobibi import validator
        return validator

    ## on setup phase
    def test_using_field_name_is_conflicted(self):
        from asobibi import SetupError
        Schema = self._get_schema()
        with self.assertRaises(SetupError) as e:
            e.expected_regexp = "conflict"
            self._getTarget()("Validator", [((Schema.val, Schema.val),  lambda k, val: True)])
        
    def test_using_too_many_field(self):
        from asobibi import SetupError
        from asobibi import schema
        Schema = schema("Schema", [("val0", {}), ("val1", {})])
        with self.assertRaises(SetupError) as e:
            e.expected_regexp = "too many"
            self._getTarget()("Validator", [((Schema.val0, Schema.val1),  lambda k, val0: True)])
        
    def test_using_too_few_field(self):
        from asobibi import SetupError
        Schema = self._get_schema()
        with self.assertRaises(SetupError) as e:
            e.expected_regexp = "too few"
            self._getTarget()("Validator", [((Schema.val),  lambda k, val, extra: True)])

    def test_using_too_few_field__with_extra_data(self):
        from asobibi import WithExtra
        Schema = self._get_schema()
        self._getTarget()("Validator", [((Schema.val),  WithExtra(lambda k, val, extra: True))])

    ## on initialize phase
    def test_it(self):
        from asobibi import WithExtra
        Schema = self._get_schema()
        Validator = self._getTarget()("Validator", [((Schema.val),  WithExtra(lambda k, val, extra: True))])
        
        target = Schema(val="a")
        result = Validator(target, {"extra": ">_<"})
        self.assertTrue(result.validate())
        
    def test_with_extra__missing(self):
        from asobibi import WithExtra
        from asobibi import InitializeError
        Schema = self._get_schema()
        Validator = self._getTarget()("Validator", [((Schema.val),  WithExtra(lambda k, val, extra: True))])
        
        target = Schema(val="a")
        with self.assertRaises(InitializeError) as e:
            e.expected_regexp = "need extra data!"
            Validator(target)

    def test_with_extra__dict_but_other_values(self):
        from asobibi import WithExtra
        from asobibi import InitializeError
        Schema = self._get_schema()
        Validator = self._getTarget()("Validator", [((Schema.val),  WithExtra(lambda k, val, extra: True))])
        
        target = Schema(val="a")
        with self.assertRaises(InitializeError) as e:
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
        with self.assertRaises(Exception) as e:
            e.expected_regexp = "called. and validation error"
            target.validate()

    ## validation with extra data
    def _get_schema__point(self):
        from asobibi import schema
        from asobibi import Op, Int
        def positive(k,x):
            assert x >= 0
            return x
        return schema("Point",[("x",{Op.converters:[Int]}),
                               ("y",{Op.converters:[Int, positive]}),])

    def _get_validator__with_extra_data(self, Point):
        from asobibi import validator
        from asobibi import WithExtra
        from asobibi import ValidationError
        def validation_with_extradata(_, x, y, z=0):
            if x*x+y*y != z*z:
                raise ValidationError("not x^2 + y^2 == z^2 ({0} != {1})".format(x*x+y*y, z*z))

        return validator("Validator", 
                         [((Point.x, Point.y), WithExtra(validation_with_extradata))])
        
    def test_validate__with_extra_data__success(self):
        Point = self._get_schema__point()
        point = Point(x=3, y=4)
        point = self._get_validator__with_extra_data(Point)(point, 5)
        self.assertTrue(point.validate())

    def test_validate__with_extra_data__success2(self):
        Point = self._get_schema__point()
        point = Point(x=3, y=4)
        point = self._get_validator__with_extra_data(Point)(point, extra=[5])
        self.assertTrue(point.validate())

    def test_validate__with_extra_data__success3(self):
        Point = self._get_schema__point()
        point = Point(x=3, y=4)
        point = self._get_validator__with_extra_data(Point)(point, extra={"z": 5})
        self.assertTrue(point.validate())

    def test_validate__with_extra_data__failure(self):
        Point = self._get_schema__point()
        point = Point(x=3, y=10)
        point = self._get_validator__with_extra_data(Point)(point, 5)
        self.assertFalse(point.validate())
        self.assertEquals(point.errors, {"x": ['not x^2 + y^2 == z^2 (109 != 25)']})

    def test_validate__with_extra_data__missing_arguments(self): #xxx:
        Point = self._get_schema__point()
        point = Point(x=3, y=10)
        point = self._get_validator__with_extra_data(Point)(point)
        self.assertFalse(point.validate())
        self.assertEquals(point.errors, {"x": ['not x^2 + y^2 == z^2 (109 != 0)']})


class NestedValidatorTests(unittest.TestCase):
    def _get_schema(self):
        from asobibi import schema
        from asobibi import Op, Int
        def positive(k,x):
            assert x >= 0
            return x
        return schema("Point",[("x",{Op.converters:[Int]}),
                               ("y",{Op.converters:[Int, positive]}),])
        
    def _get_validator__ordered(self):
        from asobibi import validator
        def ordered(k, x,y):
            assert x < y
            return x
        return validator("FstValidator", [(("x", "y"), ordered)])        

    def _get_validator__bigger(self):
        from asobibi import validator
        def bigger(k, x,y):
            assert x*x+y*y > 100
        return validator("SndValidator",[(("x","y"), bigger)])

    def test_schema__success(self):
        point = self._get_schema()(x=10,y="20")

        self.assertTrue(point.validate())
        self.assertTrue(point.result)
        self.assertEquals(point.result["x"],10)
        self.assertEquals(point.result["y"],20)

    def test_schema__failure(self):
        point = self._get_schema()(x=10,y="-20")

        self.assertFalse(point.validate())
        self.assertFalse(point.result)
        self.assertEquals(point.result["x"],10)
        self.assertEquals(point.result["y"], -20)

    def test_validator__success(self):
        point = self._get_schema()(x=10,y="20")
        point = self._get_validator__ordered()(point)

        self.assertTrue(point.validate())
        self.assertTrue(point.result)
        self.assertEquals(point.result["x"],10)
        self.assertEquals(point.result["y"],20)

    def test_validator__failure(self):
        point = self._get_schema()(x=30,y="20")
        point = self._get_validator__ordered()(point)

        self.assertFalse(point.validate())
        self.assertFalse(point.result)
        self.assertEquals(point.result["x"],30)
        self.assertEquals(point.result["y"],20)

    def test_nested_validator__success(self):
        point = self._get_schema()(x=10,y="20")
        point = self._get_validator__ordered()(point)
        point = self._get_validator__bigger()(point)

        self.assertTrue(point.validate())
        self.assertTrue(point.result)
        self.assertEquals(point.result["x"],10)
        self.assertEquals(point.result["y"],20)

    def test_nested_validator__failure(self):
        point = self._get_schema()(x=1,y="2")
        point = self._get_validator__ordered()(point)
        point = self._get_validator__bigger()(point)

        self.assertFalse(point.validate())
        self.assertFalse(point.result)
        self.assertEquals(point.result["x"],1)
        self.assertEquals(point.result["y"],2)

    def test_nested_validator__failure2(self):
        point = self._get_schema()(x=1,y="2")
        point = self._get_validator__bigger()(point)
        point = self._get_validator__ordered()(point)

        self.assertFalse(point.validate())
        self.assertFalse(point.result)
        self.assertEquals(point.result["x"],1)
        self.assertEquals(point.result["y"],2)

class ComplexSchemaTests(unittest.TestCase):
    def _getComplexSchema(self):
        from asobibi import schema
        from asobibi import Op, Unicode, as_converter

        def capitalize(k, string):
            return u"".join(x.capitalize() for x in string.split("-"))

        Address = schema("Address",
                         [("prefecture", {Op.converters:[Unicode,capitalize]}),
                          ("city", {Op.converters:[Unicode,capitalize]}),
                          ("address_1", {}),
                          ("address_2", {Op.required:False, Op.initial:None}),
                ])

        Person = schema("Person",
                        [("first_name", {Op.converters:[Unicode,capitalize]}),
                         ("last_name", {Op.converters:[Unicode,capitalize]})])

        Account = schema("Account",
                         [("person", {Op.converters:[as_converter(Person)]}), 
                          ("address", {Op.converters:[as_converter(Address)]})])
        return Account

    def test_failure(self):
        schema = self._getComplexSchema()
        target = schema()
        self.assertFalse(target.validate())

    def test_failure2(self):
        schema = self._getComplexSchema()
        target = schema({"person":
                         {"first_name": "first-name"}, 
                         "address":
                         {"prefecture": "tokyo"}})
        self.assertFalse(target.validate())

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
        self.assertTrue(target.validate())
        self.assertEqual(target.result, 
                         {"person":
                          {"first_name": "FirstName", 
                           "last_name": "LastName", }, 
                          "address":
                          {"prefecture": "Tokyo", 
                           "city": "ChiyodaKu", 
                           "address_1": "chiyoda 1-1", 
                           "address_2": None}
                      })
    

if __name__ == "__main__":
    unittest.main()

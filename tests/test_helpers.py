import unittest

class FlattenErrorsTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from asobibi.langhelpers import flatten_dict
        return flatten_dict(*args, **kwargs)

    def test_it(self):
        errors = {"a": {"b": {"c":
                              {"left": ["left is not found"],
                               "right": ["right is not found"]}, 
                        },
                        "x": ["xxxx"]}}
        result = self._callFUT(errors)
        self.assertEquals(result, 
                          {'a.b.c.right': ['right is not found'], 
                           'a.b.c.left': ['left is not found'], 
                           'a.x': ['xxxx'],
                       })

class DeepNestTests(unittest.TestCase):
    def _get_A(self):
        from asobibi import schema
        from asobibi import Op, Unicode, as_converter
        Pair = schema("Pair", [("left", {Op.converters:[Unicode, lambda k, x: x.capitalize()]}), 
                                ("right", {Op.converters:[Unicode, lambda k, x: x.capitalize()]}), 
                ])
        E = schema("E", [("f", {Op.converters:[as_converter(Pair)]})])
        D = schema("D", [("e", {Op.converters:[as_converter(E)]})])
        C = schema("C", [("d", {Op.converters:[as_converter(D)]})])
        B = schema("B", [("c", {Op.converters:[as_converter(C)]})])
        A = schema("A", [("b", {Op.converters:[as_converter(B)]})])
        return A

    def test_access_property__class(self):
        A = self._get_A()
        self.assertEqual(A.b, "b")

    def test_access_property__object__pre_validate(self):
        A = self._get_A()
        a = A({"b": {"c": {"d": {"e": {"f": {"left": "xxxx", "right": "yyyy"}}}}}})
        self.assertEquals(a.b, {"c": {"d": {"e": {"f": {"left": "xxxx", "right": "yyyy"}}}}})

        with self.assertRaises(AttributeError):
            self.assertEquals(a.b.c.d.e.f.left, "xxxx")
            self.assertEquals(a.b.c.d.e.f.right, "yyyy")

    def test_access_property__object__post_validate(self):
        A = self._get_A()
        a = A({"b": {"c": {"d": {"e": {"f": {"left": "xxxx", "right": "yyyy"}}}}}})
        self.assertTrue(a.validate())
        self.assertEquals(a.b.c.d.e.f.left, "Xxxx")
        self.assertEquals(a.b.c.d.e.f.right, "Yyyy")

    def test_deep_nested__success(self):
        A = self._get_A()
        a = A({"b": {"c": {"d": {"e": {"f": {"left": "xxxx", "right": "yyyy"}}}}}})
        self.assertTrue(a.validate())
        self.assertEquals(a.result,{"b": {"c": {"d": {"e": {"f": {"left": "Xxxx", "right": "Yyyy"}}}}}})
        self.assertIsNone(a.errors)

    def test_deep_nested__failure(self):
        A = self._get_A()
        a = A({"b": {"c": {"d": {"F": {"f": {"left": "xxxx", "right": "yyyy"}}}}}})
        self.assertFalse(a.validate())
        self.assertFalse(a.result)

        from asobibi.langhelpers import flatten_dict
        self.assertEquals(flatten_dict(a.errors).keys(), ["b.c.d.e"])

if __name__ == "__main__":
    unittest.main()

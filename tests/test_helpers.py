import unittest


class ChainMapViewTests(unittest.TestCase):

    def _getTargetClass(self):
        from asobibi.structure import ChainMapView
        return ChainMapView

    def _makeOne(self, *args, **kwargs):
        return self._getTargetClass()(*args, **kwargs)

    def test_it(self):
        D0 = {"a": 1, "b": 2}
        D1 = {"b": 3, "c": 3}
        target = self._makeOne(D0, D1)
        self.assertEqual(target["a"], 1)
        self.assertEqual(target["b"], 2)
        self.assertEqual(target["c"], 3)

        with self.assertRaises(KeyError):
            target["missing-key"]

        self.assertEqual(len(target), 3)
        self.assertEqual(dict(target), {"a": 1, "b": 2, "c": 3})


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


class DispatchTests(unittest.TestCase):

    def _makeOne(self, *args, **kwargs):
        from asobibi.langhelpers import Dispatch
        return Dispatch(*args, **kwargs)

    def test_it(self):
        marker = (lambda x: x)
        target = self._makeOne("foo")
        result = target(marker)

        self.assertFalse(target.is_tagged(marker))
        self.assertTrue(target.is_tagged(result))
        self.assertFalse(target.is_tagged((lambda x: x)))

    def test_with_another(self):
        marker = (lambda x: x)
        target = self._makeOne("foo")
        another = self._makeOne("bar")
        result = another(marker)

        self.assertFalse(target.is_tagged(result))


class dummy_caller(object):

    def __call__(self, *args, **kwargs):
        return args, kwargs


class MergableTests(unittest.TestCase):

    def _callFUT(self, *args, **kwargs):
        from asobibi.langhelpers import mergeable
        return mergeable(*args, **kwargs)

    def test_it(self):
        target = self._callFUT(dummy_caller(), x="x", ys=[0])
        result = target.merged(x=10, ys=[1], z=1)
        args, kwargs = result(1, 2, 3)
        self.assertEquals(args, (1, 2, 3))
        self.assertEquals(kwargs, {"x": 10, "ys": [0, 1], "z": 1})

    def test_it__with_tuple_list(self):
        target = self._callFUT(dummy_caller(), ys=(0,))
        result = target.merged(ys=[1])
        args, kwargs = result()
        self.assertEquals(kwargs, {"ys": [0, 1]})

    def test_it__with_tuple_tuple(self):
        target = self._callFUT(dummy_caller(), ys=(0,))
        result = target.merged(ys=(1, ))
        args, kwargs = result()
        self.assertEquals(kwargs, {"ys": [0, 1]})

    def test_it__with_tuple_val(self):
        target = self._callFUT(dummy_caller(), ys=(0,))
        result = target.merged(ys=3)
        args, kwargs = result()
        self.assertEquals(kwargs, {"ys": 3})


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

    def test_it2(self):
        errors = {"a": [{"b": {"c":
                               {"left": ["left is not found"],
                                "right": ["right is not found"]},
                               },
                         "x": ["xxxx"]}]}
        result = self._callFUT(errors)
        self.assertEquals(result,
                          {'a.b.c.right': ['right is not found'],
                           'a.b.c.left': ['left is not found'],
                           'a.x': ['xxxx'],
                           })

if __name__ == "__main__":
    unittest.main()

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

if __name__ == "__main__":
    unittest.main()

# -*- coding:utf-8 -*-

import unittest


class Test(unittest.TestCase):

    def test_it(self):
        from asobibi.exceptions import ValidationError
        from asobibi.translations import SystemMessage, DisplayMessage
        from asobibi.construct import ErrorList

        SystemMessage("unicode", fmt="{value} is not strict unicode.", mapping={"value": "----"})
        DisplayMessage("unicode", fmt=u"入力してください {field}", mapping={"field": "----"})

        def strict_unicode(name, x):
            if x is None or x == "":
                raise ValidationError({"name": "unicode", "field": name, "value": x})

        from asobibi import schema, field
        StrictUnicode = field(converters=[strict_unicode])
        Person = schema("Person", [StrictUnicode("first_name"), StrictUnicode("last_name")])

        person = Person()
        self.assertFalse(person.validate())
        self.assertEquals(str(person.errors),
                          str(ErrorList({'first_name': ['first_name is Missing.'],
                                         'last_name': ['last_name is Missing.']})))
        self.assertEquals(unicode(person.errors),
                          unicode(ErrorList({'first_name': [u'first_name がみつかりません'],
                                             'last_name': [u'last_name がみつかりません']})))

        person = Person(first_name="test", last_name="")
        self.assertFalse(person.validate())
        self.assertEquals(str(person.errors),
                          str(ErrorList({'last_name': [' is not strict unicode.']})))

        self.assertEquals(unicode(person.errors),
                          unicode(ErrorList({"last_name": [u"入力してください last_name"]})))


if __name__ == "__main__":
    unittest.main()

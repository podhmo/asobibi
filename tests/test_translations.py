# -*- coding:utf-8 -*-

import unittest


class TranslationsTests(unittest.TestCase):

    def test_render(self):
        from asobibi.translations import SystemMessage
        s = SystemMessage("input", fmt="NoInput {field}", mapping={"field": "----"})

        self.assertEqual(s(), "NoInput ----")
        self.assertEqual(s({"field": "field0"}), "NoInput field0")

    def test_lookup(self):
        from asobibi.translations import SystemMessage
        from asobibi.translations import translate
        SystemMessage("input", fmt="NoInput {field}", mapping={"field": "----"})

        self.assertEqual(translate("input", {"field": "field0"}), "NoInput field0")

    def test_lookup__notfound(self):
        from asobibi.translations import SystemMessage
        from asobibi.translations import translate
        from asobibi.translations import MessageStringNotFound
        SystemMessage("input", fmt="NoInput {field}", mapping={"field": "----"})

        with self.assertRaises(MessageStringNotFound):
            translate("missing-input", {"field": "field0"})

    def test_it(self):
        from asobibi.translations import SystemMessage
        from asobibi.translations import DisplayMessage
        from asobibi.translations import translate
        from asobibi.translations import unicode_translate

        SystemMessage("input", fmt="NoInput {field}", mapping={"field": "----"})
        DisplayMessage("input", fmt=u"ありません {field}", mapping={"field": "----"})

        self.assertEqual(translate("input", {"field": "field0"}), "NoInput field0")
        self.assertEqual(unicode_translate("input", {"field": "field0"}), u"ありません field0")

if __name__ == "__main__":
    unittest.main()

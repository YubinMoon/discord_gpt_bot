import os
import unittest
from GPT import chat
from GPT import setting
from GPT import message
from dotenv import load_dotenv

load_dotenv()


class SettingTests(unittest.TestCase):
    def setUp(self):
        self.setting = setting.Setting()

    def test_default_value(self):
        self.assertEqual(self.setting.model, "gpt-3.5-turbo-0613")
        self.assertEqual(self.setting.system_text, "")
        self.assertEqual(self.setting.max_token, 3000)
        self.assertEqual(self.setting.temperature, 1.0)
        self.assertEqual(self.setting.top_p, 1.0)
        self.assertEqual(self.setting.keep_min, 10)

    def test_set_value(self):
        self.setting.set_setting("model", "gpt-4")
        self.setting.set_setting("system_text", "aaaa")
        self.setting.set_setting("max_token", "2000")
        self.setting.set_setting("temperature", "2.0")
        self.setting.set_setting("top_p", "1.1")
        self.setting.set_setting("keep_min", "20")
        self.assertEqual(self.setting.model, "gpt-4")
        self.assertEqual(self.setting.system_text, "aaaa")
        self.assertEqual(self.setting.max_token, 2000)
        self.assertEqual(self.setting.temperature, 2.0)
        self.assertEqual(self.setting.top_p, 1.1)
        self.assertEqual(self.setting.keep_min, 20)

    def test_set_value_error(self):
        with self.assertRaises(ValueError):
            self.setting.set_setting("temperature", "asdf")
        with self.assertRaises(ValueError):
            self.setting.set_setting("max_token", "asdf")
        with self.assertRaises(KeyError):
            self.setting.set_setting("asdf", "asdf")
        with self.assertRaises(ValueError):
            self.setting.set_setting("model", "asdf")


if __name__ == "__main__":
    unittest.main()

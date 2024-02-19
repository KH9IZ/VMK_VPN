import unittest
import telebot

from ipaddress import AddressValueError, IPv4Address, ip_network

import main
import wg


class InGameTests(unittest.TestCase):
    def setUp(self):
        self.wg_conf = wg.WireGuardConfig('1234567890')


    def test_1_config_get(self):
        self.assertEqual(self.wg_conf.get(
        ), "/etc/wireguard/clients/1234567890.conf", "Wrong keys generated!")

    def test_2_config_exists(self):
        self.assertEqual(self.wg_conf.exists(), False,
                         "Config doesn't exist, but found!")


    def test_3_gen_markup(self):
        data, n = {"config":  "Pay to get your config!",
                             "faq": "FAQ", "settings": "Settings"}, 3
        res = "{'row_width': 3, 'keyboard': [[<telebot.types.InlineKeyboardButton object at 0x7f736d277790>], [<telebot.types.InlineKeyboardButton object at 0x7f736d274940>], [<telebot.types.InlineKeyboardButton object at 0x7f736d276f50>]]}"
                
        self.assertEqual(main.gen_markup(data, n).row_width, 3, "Wrong markup was generated!")


    def test_4_generate_keys(self):
        wg_test = wg.WireGuardConfig("test name")
        data = wg_test._WireGuardConfig__generate_keys()
        assert len(data) == 2

    def test_5_(self):
        wg_test = wg.WireGuardConfig("test_name")
        self.assertRaises(ValueError, wg_test.remove, "test_name")

if __name__ == '__main__':
    unittest.main()

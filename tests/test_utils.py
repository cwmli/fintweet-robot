import unittest

from src.fintweet_robot.utils import proxy_list

class TestUtils(unittest.TestCase):

    def test_invalid_proto_no_results(self):
        self.assertEqual(proxy_list(protocol=""), [])

    def test_invalid_ISOCC_no_results(self):
        self.assertEqual(proxy_list(country="NULL"), [])

    def test_valid_proto_has_results(self):
        self.assertTrue(proxy_list())

    def test_proxy_format(self):
        # test for valid ip:port format
        # https://stackoverflow.com/questions/5284147/validating-ipv4-addresses-with-regexp
        self.assertRegex(proxy_list()[0], 
            r"((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?):[0-9]+")

if __name__ == '__main__':
    unittest.main()
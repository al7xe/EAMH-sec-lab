import unittest

from network_monitor import validate_network, validate_private_ip


class NetworkValidationTests(unittest.TestCase):
    def test_accepts_private_subnet(self):
        network = validate_network("192.168.1.0/24")
        self.assertEqual(str(network), "192.168.1.0/24")

    def test_normalizes_host_bits(self):
        network = validate_network("192.168.1.23/24")
        self.assertEqual(str(network), "192.168.1.0/24")

    def test_rejects_public_network(self):
        with self.assertRaises(ValueError):
            validate_network("8.8.8.0/24")

    def test_rejects_large_network(self):
        with self.assertRaises(ValueError):
            validate_network("10.0.0.0/16")

    def test_rejects_ipv6(self):
        with self.assertRaises(ValueError):
            validate_network("fd00::/64")

    def test_accepts_private_host(self):
        self.assertEqual(validate_private_ip("192.168.1.10"), "192.168.1.10")

    def test_rejects_public_host(self):
        with self.assertRaises(ValueError):
            validate_private_ip("1.1.1.1")


if __name__ == "__main__":
    unittest.main()

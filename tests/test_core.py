import unittest

from py_ip_address_sorter import sort_addresses, parse_item


class TestParseItem(unittest.TestCase):
    def test_parses_ipv4_address(self):
        parsed = parse_item("192.168.1.1")
        self.assertEqual(str(parsed), "192.168.1.1")
        self.assertEqual(parsed.version, 4)

    def test_parses_ipv6_address(self):
        parsed = parse_item("2001:db8::1")
        self.assertEqual(parsed.version, 6)

    def test_parses_ipv4_network(self):
        parsed = parse_item("10.0.0.0/8")
        self.assertEqual(str(parsed), "10.0.0.0/8")

    def test_host_bits_are_normalised(self):
        # A network written with host bits set is normalised to the network
        # address; this is the documented behaviour of strict=False.
        parsed = parse_item("192.168.1.5/24")
        self.assertEqual(str(parsed), "192.168.1.0/24")

    def test_whitespace_is_stripped(self):
        parsed = parse_item("  10.0.0.1  ")
        self.assertEqual(str(parsed), "10.0.0.1")

    def test_empty_string_raises(self):
        with self.assertRaises(ValueError):
            parse_item("")

    def test_non_string_raises_type_error(self):
        with self.assertRaises(TypeError):
            parse_item(1234)

    def test_invalid_address_raises(self):
        with self.assertRaises(ValueError):
            parse_item("999.1.1.1")


class TestSortAddresses(unittest.TestCase):
    def test_sorts_ipv4_numerically_not_lexically(self):
        got = sort_addresses(["10.0.0.10", "10.0.0.2", "10.0.0.1"])
        self.assertEqual(got, ["10.0.0.1", "10.0.0.2", "10.0.0.10"])

    def test_sorts_ipv6_numerically(self):
        got = sort_addresses(["2001:db8::10", "2001:db8::2", "2001:db8::1"])
        self.assertEqual(got, ["2001:db8::1", "2001:db8::2", "2001:db8::10"])

    def test_mixed_families_ipv4_first(self):
        got = sort_addresses(["2001:db8::1", "10.0.0.1", "::1"])
        self.assertEqual(got, ["10.0.0.1", "::1", "2001:db8::1"])

    def test_network_sorts_by_network_address(self):
        got = sort_addresses(["10.0.0.0/24", "10.0.0.0/8", "9.0.0.0/8"])
        # 9.0.0.0/8 first; then 10.0.0.0/8 before 10.0.0.0/24 because the
        # shorter prefix (the covering network) sorts first.
        self.assertEqual(got, ["9.0.0.0/8", "10.0.0.0/8", "10.0.0.0/24"])

    def test_address_and_network_share_a_key_space(self):
        # 10.0.0.0/8 has network address 10.0.0.0 which is less than
        # 10.0.0.1, so the network sorts first.
        got = sort_addresses(["10.0.0.1", "10.0.0.0/8"])
        self.assertEqual(got, ["10.0.0.0/8", "10.0.0.1"])

    def test_input_not_mutated(self):
        original = ["10.0.0.2", "10.0.0.1"]
        snapshot = list(original)
        sort_addresses(original)
        self.assertEqual(original, snapshot)

    def test_accepts_any_iterable(self):
        got = sort_addresses(iter(["10.0.0.2", "10.0.0.1"]))
        self.assertEqual(got, ["10.0.0.1", "10.0.0.2"])

    def test_empty_input(self):
        self.assertEqual(sort_addresses([]), [])

    def test_ipv6_network_ordering(self):
        got = sort_addresses(["2001:db8:1::/48", "2001:db8::/32", "2001:db8::1"])
        # 2001:db8::/32 covers 2001:db8::1, so the network sorts first;
        # 2001:db8:1::/48 has a larger network address.
        self.assertEqual(got, ["2001:db8::/32", "2001:db8::1", "2001:db8:1::/48"])

    def test_duplicate_values_are_kept(self):
        got = sort_addresses(["10.0.0.1", "10.0.0.1"])
        self.assertEqual(got, ["10.0.0.1", "10.0.0.1"])

    def test_invalid_entry_raises(self):
        with self.assertRaises(ValueError):
            sort_addresses(["10.0.0.1", "not-an-address"])

    def test_mixed_ipv4_and_ipv6_networks(self):
        got = sort_addresses(["2001:db8::/32", "192.168.0.0/16", "::/0"])
        self.assertEqual(got, ["192.168.0.0/16", "::/0", "2001:db8::/32"])


if __name__ == "__main__":
    unittest.main()

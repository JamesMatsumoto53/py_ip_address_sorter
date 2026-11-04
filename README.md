# py_ip_address_sorter

Sort a mixed list of IPv4 and IPv6 addresses and ranges into proper numeric
order using only the standard library.

```python
from py_ip_address_sorter import sort_addresses, parse_item

sort_addresses(["10.0.0.10", "10.0.0.2", "2001:db8::1", "10.0.0.0/24"])
# ['10.0.0.0/24', '10.0.0.2', '10.0.0.10', '2001:db8::1']

parse_item("192.168.1.5/24")
# IPv4Network('192.168.1.0/24')
```

## Why this exists

Lexical sorting of address strings is wrong: `"10.0.0.10"` sorts before
`"10.0.0.2"`, and IPv4 and IPv6 strings have no natural relationship at all.
The obvious fix is to convert each string with the `ipaddress` module and sort
by the resulting integer. The trade-off is what to do with a mixed list.
There is no single correct answer, so this library picks one and states it:
IPv4 sorts before IPv6, and every value is reduced to a single
`(family, packed_bytes, prefix_length)` key. That gives a total order across
addresses and networks, at the cost of a fixed family precedence that some
callers may not want. If you need a different rule, sort the parsed objects
yourself with your own key.

## The awkward edge

Networks are ordered by their network address, and ties are broken by prefix
length with the *shorter* prefix first. So `10.0.0.0/8` sorts before
`10.0.0.0/24`, which is the opposite of naive string order. A network written
with host bits set, such as `192.168.1.5/24`, is normalised to
`192.168.1.0/24` because `ipaddress.ip_network` is called with
`strict=False`; this is almost always what the caller meant, but it does mean
the returned strings can differ from the input strings.

## API

- `sort_addresses(items)` — takes any iterable of strings, returns a new list
  of strings in ascending order. The input is not modified.
- `parse_item(item)` — takes a single string and returns an
  `IPv4Address`, `IPv6Address`, `IPv4Network`, or `IPv6Network`. Raises
  `TypeError` for non-strings and `ValueError` for malformed input or empty
  strings.

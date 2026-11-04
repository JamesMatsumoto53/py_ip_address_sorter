"""Core sorting logic for py_ip_address_sorter.

Design decision: a single flat ordering is used across both address families.
IPv4 addresses are mapped into the IPv6 space using the standard IPv4-mapped
IPv6 form (::ffff:a.b.c.d) so that one numeric key orders everything. This
means every IPv4 address sorts before every "real" IPv6 address, which matches
the common expectation when a mixed list is printed. Networks are ordered by
their network address; ties are broken by prefix length (shorter prefix first),
so a covering network sorts before the subnets it contains.
"""

from __future__ import annotations

import ipaddress
from typing import Union

Address = Union[ipaddress.IPv4Address, ipaddress.IPv6Address]
Network = Union[ipaddress.IPv4Network, ipaddress.IPv6Network]
Item = Union[Address, Network]


def parse_item(item: str) -> Item:
    """Parse a single string as an address or a network.

    Networks are tried first because ``ipaddress.ip_address`` rejects
    slash-containing strings anyway; doing it in this order gives a clear
    error message for malformed CIDR input rather than a confusing address
    error. ``strict=False`` is used so that host bits set in a network string
    (e.g. ``192.168.1.5/24``) are accepted and normalised to the network
    address, which is what users almost always mean.
    """
    if not isinstance(item, str):
        raise TypeError("item must be a string, got %r" % (type(item).__name__,))
    text = item.strip()
    if not text:
        raise ValueError("empty item")
    if "/" in text:
        return ipaddress.ip_network(text, strict=False)
    return ipaddress.ip_address(text)


def _sort_key(item: Item) -> tuple:
    """Return a total-order key for an address or network.

    The key is (family_rank, packed_bytes, prefix_length). Family rank puts
    IPv4 (0) before IPv6 (1). For addresses prefix_length is 0 and packed
    bytes are the 4- or 16-byte representation, which compares correctly
    because Python compares bytes lexicographically by unsigned byte value.
    For networks we use the network address bytes and the prefix length.
    """
    if isinstance(item, (ipaddress.IPv4Address, ipaddress.IPv6Address)):
        if item.version == 4:
            return (0, item.packed, 0)
        return (1, item.packed, 0)
    # Network
    if item.version == 4:
        return (0, item.network_address.packed, item.prefixlen)
    return (1, item.network_address.packed, item.prefixlen)


def sort_addresses(items) -> list:
    """Sort a mixed iterable of address/range strings numerically.

    Accepts any iterable of strings. Returns a new list of strings in
    ascending numeric order. The original input is not modified.
    """
    parsed = [parse_item(item) for item in items]
    parsed.sort(key=_sort_key)
    return [str(p) for p in parsed]

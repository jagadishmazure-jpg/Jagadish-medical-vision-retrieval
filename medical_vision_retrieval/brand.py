"""Brand/name check over hashed blocklist entries (never plain names).

The blocklist holds SHA-256 hashes of sentinel terms used to prove the
mechanism works. A production deployment replaces these with hashes of
its own reserved names, maintained outside this repo.
"""
from __future__ import annotations

import hashlib
import re

BLOCKLIST_HASHES: frozenset[str] = frozenset({
    hashlib.sha256(b"sentinel-blocked-term-alpha").hexdigest(),
    hashlib.sha256(b"sentinel-blocked-term-beta").hexdigest(),
})

_TOKEN = re.compile(r"[a-z0-9][a-z0-9-]+")


def contains_blocked(text: str) -> bool:
    for token in _TOKEN.findall(text.lower()):
        if hashlib.sha256(token.encode("utf-8")).hexdigest() in BLOCKLIST_HASHES:
            return True
    return False

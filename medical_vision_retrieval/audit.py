"""Hash-chained audit log: tampering with any entry breaks the chain."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass


@dataclass(frozen=True)
class AuditEntry:
    index: int
    prev_hash: str
    payload: str
    entry_hash: str


class AuditLog:
    def __init__(self) -> None:
        self.entries: list[AuditEntry] = []
        self._prev = "GENESIS"

    def append(self, payload: str) -> AuditEntry:
        raw = f"{self._prev}|{len(self.entries)}|{payload}"
        entry_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        entry = AuditEntry(len(self.entries), self._prev, payload, entry_hash)
        self.entries.append(entry)
        self._prev = entry_hash
        return entry

    def verify_chain(self) -> bool:
        prev = "GENESIS"
        for i, entry in enumerate(self.entries):
            if entry.index != i or entry.prev_hash != prev:
                return False
            raw = f"{prev}|{i}|{entry.payload}"
            if hashlib.sha256(raw.encode("utf-8")).hexdigest() != entry.entry_hash:
                return False
            prev = entry.entry_hash
        return True

    def to_json(self) -> str:
        return json.dumps([e.__dict__ for e in self.entries], indent=2)

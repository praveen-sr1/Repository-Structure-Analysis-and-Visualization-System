"""SHA-256 hashing helpers used for AI-summary cache invalidation."""
from __future__ import annotations

import hashlib


def hash_bytes(data: bytes) -> str:
    """Return the hex SHA-256 digest of ``data``."""
    return hashlib.sha256(data).hexdigest()


def hash_text(text: str, *, encoding: str = "utf-8") -> str:
    """Return the hex SHA-256 digest of ``text``."""
    return hash_bytes(text.encode(encoding, errors="replace"))

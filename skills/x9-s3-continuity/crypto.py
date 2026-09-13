"""Audited-library client-side authenticated encryption."""

from __future__ import annotations

from dataclasses import dataclass, field
import re

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESSIV
except ImportError:  # pragma: no cover - exercised only on unsupported hosts
    AESSIV = None  # type: ignore[assignment,misc]


class EncryptionUnavailable(RuntimeError):
    """Raised instead of silently falling back to hand-built cryptography."""


class DecryptionError(ValueError):
    """Raised when authenticated decryption or key identity validation fails."""


@dataclass(frozen=True, repr=False)
class EncryptedPayload:
    key_id: str
    algorithm: str
    ciphertext: bytes = field(repr=False)

    def __repr__(self) -> str:
        return (
            "EncryptedPayload("
            f"key_id={self.key_id!r}, algorithm={self.algorithm!r}, "
            f"ciphertext_bytes={len(self.ciphertext)})"
        )


class ClientSideEncryptor:
    """AES-SIV encryption with generation/object identity in authenticated data."""

    algorithm = "AES-SIV-256"
    _KEY_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")

    def __init__(self, key_id: str, key: bytes) -> None:
        if AESSIV is None:
            raise EncryptionUnavailable(
                "cryptography AESSIV is required; no local crypto fallback is allowed"
            )
        if not isinstance(key_id, str) or not self._KEY_ID.fullmatch(key_id):
            raise ValueError("key_id must be a path-safe identifier")
        if not isinstance(key, bytes) or len(key) != 64:
            raise ValueError("AES-SIV-256 requires a 64-byte key")
        self.key_id = key_id
        self._key = key

    def __repr__(self) -> str:
        return f"ClientSideEncryptor(key_id={self.key_id!r}, algorithm={self.algorithm!r})"

    def _associated_data(self, generation_id: str, object_key: str) -> list[bytes]:
        identity = "\0".join(
            ("x9-s3-continuity-v1", self.key_id, generation_id, object_key)
        )
        return [identity.encode("utf-8")]

    def encrypt(self, plaintext: bytes, generation_id: str, object_key: str) -> EncryptedPayload:
        if not isinstance(plaintext, bytes):
            raise TypeError("plaintext must be bytes")
        ciphertext = AESSIV(self._key).encrypt(
            plaintext, self._associated_data(generation_id, object_key)
        )
        return EncryptedPayload(self.key_id, self.algorithm, ciphertext)

    def decrypt(
        self,
        payload: EncryptedPayload,
        generation_id: str,
        object_key: str,
    ) -> bytes:
        if payload.key_id != self.key_id or payload.algorithm != self.algorithm:
            raise DecryptionError("encrypted object key identity is not accepted")
        try:
            return AESSIV(self._key).decrypt(
                payload.ciphertext,
                self._associated_data(generation_id, object_key),
            )
        except Exception as exc:  # cryptography exposes backend-specific failures
            raise DecryptionError("authenticated object decryption failed") from exc

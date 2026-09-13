"""Injected S3 SDK boundary and deterministic offline object store."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol, runtime_checkable


class ProviderError(RuntimeError):
    """Provider failures stay inside the addon failure domain."""


class ObjectNotFound(ProviderError):
    """Raised when a requested object or version does not exist."""


class ObjectAlreadyExists(ProviderError):
    """Raised when an immutable conditional put collides."""


class CapabilityError(ProviderError):
    """Raised when the provider cannot safely commit a generation."""


@dataclass(frozen=True)
class CapabilityProfile:
    """Capabilities are supplied by an external probe; they are not assumed."""

    conditional_create: bool = True
    provider_checksums: bool = False
    versioning: bool = False
    retention: bool = False


@dataclass(frozen=True)
class CapabilityReport:
    conditional_create: bool
    provider_checksums: bool
    versioning: bool
    retention: bool
    commit_allowed: bool
    checksum_mode: str
    restore_mode: str
    retention_mode: str

    def as_dict(self) -> dict[str, object]:
        return {
            "conditional_create": self.conditional_create,
            "provider_checksums": self.provider_checksums,
            "versioning": self.versioning,
            "retention": self.retention,
            "commit_allowed": self.commit_allowed,
            "checksum_mode": self.checksum_mode,
            "restore_mode": self.restore_mode,
            "retention_mode": self.retention_mode,
        }


def _sdk_status_code(exc: Exception) -> int | None:
    response = getattr(exc, "response", None)
    if not isinstance(response, Mapping):
        return None
    metadata = response.get("ResponseMetadata")
    if not isinstance(metadata, Mapping):
        return None
    status = metadata.get("HTTPStatusCode")
    return status if isinstance(status, int) else None


@runtime_checkable
class ObjectStore(Protocol):
    @property
    def capabilities(self) -> CapabilityProfile: ...

    def put(self, key: str, data: bytes, *, if_absent: bool = False) -> None: ...

    def get(self, key: str, *, version_id: str | None = None) -> bytes: ...

    def delete(self, key: str, *, version_id: str | None = None) -> None: ...

    def list_versions(self, key: str) -> list[dict[str, object]]: ...


class S3SdkObjectStore:
    """Thin adapter over an already-created AWS-compatible S3 SDK client.

    The caller owns client construction, credentials, bucket authorization, and
    the external provider gate.  This class only translates the established
    SDK calls used by the addon protocol.
    """

    def __init__(
        self,
        client: Any,
        bucket: str,
        capabilities: CapabilityProfile,
    ) -> None:
        if client is None or not isinstance(bucket, str) or not bucket.strip():
            raise ValueError("an injected SDK client and explicit bucket are required")
        self.client = client
        self.bucket = bucket
        self._capabilities = capabilities

    @property
    def capabilities(self) -> CapabilityProfile:
        return self._capabilities

    def put(self, key: str, data: bytes, *, if_absent: bool = False) -> None:
        params: dict[str, object] = {"Bucket": self.bucket, "Key": key, "Body": data}
        if if_absent:
            params["IfNoneMatch"] = "*"
        try:
            self.client.put_object(**params)
        except Exception as exc:
            if if_absent and _sdk_status_code(exc) in {409, 412}:
                raise ObjectAlreadyExists(key) from exc
            raise ProviderError("S3 put failed") from exc

    def get(self, key: str, *, version_id: str | None = None) -> bytes:
        params: dict[str, object] = {"Bucket": self.bucket, "Key": key}
        if version_id is not None:
            params["VersionId"] = version_id
        try:
            response = self.client.get_object(**params)
            body = response.get("Body")
            if hasattr(body, "read"):
                body = body.read()
            if not isinstance(body, (bytes, bytearray)):
                raise TypeError("SDK get_object body is not bytes")
            return bytes(body)
        except ObjectNotFound:
            raise
        except Exception as exc:
            if _sdk_status_code(exc) == 404:
                raise ObjectNotFound(key) from exc
            raise ProviderError("S3 get failed") from exc

    def delete(self, key: str, *, version_id: str | None = None) -> None:
        params: dict[str, object] = {"Bucket": self.bucket, "Key": key}
        if version_id is not None:
            params["VersionId"] = version_id
        try:
            self.client.delete_object(**params)
        except Exception as exc:
            raise ProviderError("S3 delete failed") from exc

    def list_versions(self, key: str) -> list[dict[str, object]]:
        try:
            response = self.client.list_object_versions(Bucket=self.bucket, Prefix=key)
            versions = response.get("Versions", [])
            return [dict(item) for item in versions if item.get("Key") == key]
        except Exception as exc:
            raise ProviderError("S3 version listing failed") from exc


@dataclass(frozen=True)
class _ObjectVersion:
    version_id: str
    data: bytes


class InMemoryObjectStore:
    """Deterministic fake used by P0 tests; it never performs network I/O."""

    def __init__(self, capabilities: CapabilityProfile | None = None) -> None:
        self._capabilities = capabilities or CapabilityProfile(
            conditional_create=True,
            provider_checksums=False,
            versioning=False,
            retention=False,
        )
        self._objects: dict[str, list[_ObjectVersion]] = {}
        self._counter = 0
        self.put_order: list[str] = []

    @property
    def capabilities(self) -> CapabilityProfile:
        return self._capabilities

    def put(self, key: str, data: bytes, *, if_absent: bool = False) -> None:
        if if_absent and key in self._objects:
            raise ObjectAlreadyExists(key)
        if not isinstance(data, bytes):
            raise TypeError("object data must be bytes")
        self._counter += 1
        version = _ObjectVersion(f"v{self._counter}", data)
        if not self._capabilities.versioning:
            self._objects[key] = [version]
        else:
            self._objects.setdefault(key, []).append(version)
        self.put_order.append(key)

    def get(self, key: str, *, version_id: str | None = None) -> bytes:
        versions = self._objects.get(key)
        if not versions:
            raise ObjectNotFound(key)
        if version_id is None:
            return versions[-1].data
        for version in versions:
            if version.version_id == version_id:
                return version.data
        raise ObjectNotFound(f"{key}@{version_id}")

    def delete(self, key: str, *, version_id: str | None = None) -> None:
        if version_id is None:
            self._objects.pop(key, None)
            return
        versions = self._objects.get(key, [])
        retained = [version for version in versions if version.version_id != version_id]
        if retained:
            self._objects[key] = retained
        else:
            self._objects.pop(key, None)

    def list_versions(self, key: str) -> list[dict[str, object]]:
        return [
            {"Key": key, "VersionId": version.version_id, "IsLatest": index == len(self._objects[key]) - 1}
            for index, version in enumerate(self._objects.get(key, []))
        ]

    def tamper(self, key: str, data: bytes) -> None:
        """Test-only corruption hook; production adapters do not expose this."""

        if key not in self._objects:
            raise ObjectNotFound(key)
        self._objects[key][-1] = _ObjectVersion(self._objects[key][-1].version_id, data)

    def has(self, key: str) -> bool:
        return key in self._objects

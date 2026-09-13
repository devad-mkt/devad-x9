"""Immutable generation, verification, restore, and rollback protocol."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from pathlib import PurePosixPath
from typing import Mapping, MutableMapping
import unicodedata

from .config import ContaboS3Config
from .crypto import ClientSideEncryptor, DecryptionError, EncryptedPayload
from .provider import (
    CapabilityError,
    CapabilityProfile,
    CapabilityReport,
    ObjectAlreadyExists,
    ObjectNotFound,
    ObjectStore,
    ProviderError,
)


class ValidationError(ValueError):
    """Raised for invalid project, generation, or object identity."""


class GenerationConflict(RuntimeError):
    """Raised when immutable generation bytes already exist."""


class GenerationIncomplete(RuntimeError):
    """Raised when a generation has no final commit marker."""


class GenerationVerificationError(RuntimeError):
    """Raised when manifest, ciphertext, or plaintext verification fails."""


class RestoreConflict(RuntimeError):
    """Raised when restore is configured to fail on a non-empty target."""


class RollbackUnavailable(RuntimeError):
    """Raised when no committed predecessor generation is recorded."""


class SelectionState(str, Enum):
    INCLUDED = "INCLUDED"
    EXCLUDED = "EXCLUDED"
    AMBIGUOUS = "AMBIGUOUS"


@dataclass(frozen=True)
class ProjectSelection:
    project_id: str
    state: SelectionState

    def require_included(self) -> str:
        project_id = _safe_component(self.project_id, "project_id")
        if self.state is not SelectionState.INCLUDED:
            raise ValidationError("only explicitly INCLUDED projects may be backed up")
        return project_id


@dataclass(frozen=True)
class RestoreReceipt:
    project_id: str
    generation_id: str
    restored_keys: tuple[str, ...]
    quarantined_keys: tuple[str, ...]


@dataclass(frozen=True)
class GenerationReceipt:
    project_id: str
    generation_id: str
    predecessor_generation_id: str | None
    manifest_key: str
    commit_key: str
    manifest_sha256: str
    object_count: int
    capability_report: CapabilityReport


@dataclass(frozen=True)
class _CommittedGeneration:
    project_id: str
    generation_id: str
    predecessor_generation_id: str | None
    objects: Mapping[str, bytes]
    marker: Mapping[str, object]


def canonical_json(value: object) -> bytes:
    try:
        encoded = json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise ValidationError("value cannot be encoded as canonical JSON") from exc
    return (encoded + "\n").encode("utf-8")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _safe_component(value: str, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValidationError(f"{field} must be non-empty text")
    normalized = unicodedata.normalize("NFC", value)
    if normalized != value:
        value = normalized
    if value in {".", ".."} or "/" in value or "\\" in value:
        raise ValidationError(f"{field} must be one path-safe component")
    if any(ord(char) < 32 for char in value):
        raise ValidationError(f"{field} contains a control character")
    return value


def _safe_path(value: str, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValidationError(f"{field} must be non-empty text")
    normalized = unicodedata.normalize("NFC", value)
    if normalized.startswith("/") or "\\" in normalized:
        raise ValidationError(f"{field} must be a relative POSIX path")
    path = PurePosixPath(normalized)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise ValidationError(f"{field} contains an unsafe path component")
    if any(ord(char) < 32 for char in normalized):
        raise ValidationError(f"{field} contains a control character")
    return "/".join(path.parts)


def _content_root(entries: list[dict[str, object]]) -> str:
    leaves = [
        {"key": entry["key"], "ciphertext_sha256": entry["ciphertext_sha256"]}
        for entry in entries
    ]
    return _sha256(canonical_json(leaves))


class S3ContinuityAddon:
    """Provider-independent continuity protocol over an injected object store."""

    schema = "x9-s3-continuity-v1"
    manifest_name = "MANIFEST.json"
    commit_name = "GENERATION_COMMITTED.json"

    def __init__(
        self,
        store: ObjectStore,
        encryptor: ClientSideEncryptor,
        config: ContaboS3Config | None = None,
    ) -> None:
        if not isinstance(store, ObjectStore):
            raise TypeError("store must satisfy the ObjectStore protocol")
        self.store = store
        self.encryptor = encryptor
        self.config = config or ContaboS3Config()

    def negotiate_capabilities(self) -> CapabilityReport:
        capabilities = self.store.capabilities
        if not isinstance(capabilities, CapabilityProfile):
            raise CapabilityError("provider capability profile is missing")
        if not capabilities.conditional_create:
            raise CapabilityError(
                "conditional object creation is required for immutable generations"
            )
        return CapabilityReport(
            conditional_create=True,
            provider_checksums=capabilities.provider_checksums,
            versioning=capabilities.versioning,
            retention=capabilities.retention,
            commit_allowed=True,
            checksum_mode=(
                "provider-and-client" if capabilities.provider_checksums else "client-only"
            ),
            restore_mode=(
                "provider-versioned" if capabilities.versioning else "generation-addressed"
            ),
            retention_mode=(
                "provider-retention" if capabilities.retention else "owner-controlled"
            ),
        )

    def create_generation(
        self,
        selection: ProjectSelection,
        objects: Mapping[str, bytes],
        *,
        generation_id: str,
        predecessor_generation_id: str | None = None,
    ) -> GenerationReceipt:
        project_id = selection.require_included()
        generation_id = _safe_component(generation_id, "generation_id")
        if predecessor_generation_id is not None:
            predecessor_generation_id = _safe_component(
                predecessor_generation_id, "predecessor_generation_id"
            )
        report = self.negotiate_capabilities()
        if not objects:
            raise ValidationError("a generation must contain at least one object")

        root = self._generation_root(project_id, generation_id)
        entries: list[dict[str, object]] = []
        normalized_keys: set[str] = set()
        for original_key in sorted(objects):
            logical_key = _safe_path(original_key, "object key")
            if logical_key in normalized_keys:
                raise ValidationError("normalized object key collision")
            normalized_keys.add(logical_key)
            plaintext = objects[original_key]
            if not isinstance(plaintext, bytes):
                raise ValidationError("object values must be bytes")
            object_key = f"{root}/objects/{logical_key}"
            payload = self.encryptor.encrypt(plaintext, generation_id, object_key)
            entries.append(
                {
                    "algorithm": payload.algorithm,
                    "ciphertext_sha256": _sha256(payload.ciphertext),
                    "ciphertext_size": len(payload.ciphertext),
                    "key": object_key,
                    "key_id": payload.key_id,
                    "logical_key": logical_key,
                    "plaintext_sha256": _sha256(plaintext),
                    "plaintext_size": len(plaintext),
                }
            )
            self._put_immutable(object_key, payload.ciphertext)

        manifest = {
            "schema": self.schema,
            "project_id": project_id,
            "generation_id": generation_id,
            "predecessor_generation_id": predecessor_generation_id,
            "objects": entries,
        }
        manifest_bytes = canonical_json(manifest)
        manifest_key = f"{root}/{self.manifest_name}"
        self._put_immutable(manifest_key, manifest_bytes)
        stored_manifest = self._get_required(manifest_key)
        if stored_manifest != manifest_bytes:
            raise GenerationVerificationError("manifest changed after immutable put")
        self._verify_entries(project_id, generation_id, entries)

        marker = {
            "schema": self.schema,
            "project_id": project_id,
            "generation_id": generation_id,
            "predecessor_generation_id": predecessor_generation_id,
            "manifest_key": manifest_key,
            "manifest_sha256": _sha256(manifest_bytes),
            "object_count": len(entries),
            "content_root": _content_root(entries),
            "capabilities": report.as_dict(),
        }
        commit_key = f"{root}/{self.commit_name}"
        self._put_immutable(commit_key, canonical_json(marker))
        return GenerationReceipt(
            project_id=project_id,
            generation_id=generation_id,
            predecessor_generation_id=predecessor_generation_id,
            manifest_key=manifest_key,
            commit_key=commit_key,
            manifest_sha256=_sha256(manifest_bytes),
            object_count=len(entries),
            capability_report=report,
        )

    def restore_into(
        self,
        selection: ProjectSelection,
        generation_id: str,
        target: MutableMapping[str, bytes],
        *,
        conflict_policy: str = "quarantine",
    ) -> RestoreReceipt:
        project_id = selection.require_included()
        if conflict_policy not in {"quarantine", "fail"}:
            raise ValidationError("conflict_policy must be quarantine or fail")
        record = self._load_committed(project_id, generation_id)
        conflicts = tuple(key for key in record.objects if key in target)
        if conflicts and conflict_policy == "fail":
            raise RestoreConflict(",".join(conflicts))
        for key, value in record.objects.items():
            if key not in target:
                target[key] = value
        restored = tuple(key for key in record.objects if key not in conflicts)
        return RestoreReceipt(project_id, record.generation_id, restored, conflicts)

    def rollback_to_previous(
        self,
        selection: ProjectSelection,
        generation_id: str,
        target: MutableMapping[str, bytes],
    ) -> RestoreReceipt:
        project_id = selection.require_included()
        record = self._load_committed(project_id, generation_id)
        predecessor = record.predecessor_generation_id
        if predecessor is None:
            raise RollbackUnavailable("generation has no committed predecessor")
        return self.restore_into(selection, predecessor, target, conflict_policy="quarantine")

    def _generation_root(self, project_id: str, generation_id: str) -> str:
        return f"{self.config.namespace}/projects/{project_id}/generations/{generation_id}"

    def _put_immutable(self, key: str, data: bytes) -> None:
        try:
            self.store.put(key, data, if_absent=True)
        except ObjectAlreadyExists as exc:
            raise GenerationConflict(key) from exc
        except ProviderError:
            raise
        except Exception as exc:
            raise ProviderError("object store put failed") from exc

    def _get_required(self, key: str) -> bytes:
        try:
            return self.store.get(key)
        except ObjectNotFound as exc:
            raise GenerationVerificationError(f"required object missing: {key}") from exc
        except ProviderError:
            raise
        except Exception as exc:
            raise ProviderError("object store get failed") from exc

    def _verify_entries(
        self,
        project_id: str,
        generation_id: str,
        entries: list[dict[str, object]],
    ) -> dict[str, bytes]:
        values: dict[str, bytes] = {}
        seen: set[str] = set()
        for entry in entries:
            logical_key = _safe_path(str(entry["logical_key"]), "manifest logical key")
            object_key = _safe_path(str(entry["key"]), "manifest object key")
            if logical_key in seen or str(entry["key"]) != object_key:
                raise GenerationVerificationError("manifest contains duplicate or unsafe keys")
            seen.add(logical_key)
            ciphertext = self._get_required(object_key)
            if len(ciphertext) != entry["ciphertext_size"] or _sha256(ciphertext) != entry["ciphertext_sha256"]:
                raise GenerationVerificationError(f"ciphertext verification failed: {logical_key}")
            payload = EncryptedPayload(
                key_id=str(entry["key_id"]),
                algorithm=str(entry["algorithm"]),
                ciphertext=ciphertext,
            )
            try:
                plaintext = self.encryptor.decrypt(payload, generation_id, object_key)
            except DecryptionError as exc:
                raise GenerationVerificationError(f"decryption failed: {logical_key}") from exc
            if len(plaintext) != entry["plaintext_size"] or _sha256(plaintext) != entry["plaintext_sha256"]:
                raise GenerationVerificationError(f"plaintext verification failed: {logical_key}")
            values[logical_key] = plaintext
        return values

    def _load_committed(self, project_id: str, generation_id: str) -> _CommittedGeneration:
        generation_id = _safe_component(generation_id, "generation_id")
        root = self._generation_root(project_id, generation_id)
        commit_key = f"{root}/{self.commit_name}"
        try:
            marker_bytes = self.store.get(commit_key)
        except ObjectNotFound as exc:
            raise GenerationIncomplete(generation_id) from exc
        except ProviderError:
            raise
        except Exception as exc:
            raise ProviderError("object store get failed") from exc
        try:
            marker = json.loads(marker_bytes.decode("utf-8"))
            if marker.get("schema") != self.schema:
                raise ValueError("marker schema mismatch")
            if marker.get("project_id") != project_id or marker.get("generation_id") != generation_id:
                raise ValueError("marker identity mismatch")
            manifest_key = _safe_path(str(marker["manifest_key"]), "marker manifest key")
            manifest_bytes = self._get_required(manifest_key)
            if _sha256(manifest_bytes) != marker["manifest_sha256"]:
                raise ValueError("manifest hash mismatch")
            manifest = json.loads(manifest_bytes.decode("utf-8"))
            if manifest.get("schema") != self.schema or manifest.get("project_id") != project_id:
                raise ValueError("manifest identity mismatch")
            if manifest.get("generation_id") != generation_id:
                raise ValueError("manifest generation mismatch")
            entries = list(manifest.get("objects", []))
            if len(entries) != marker.get("object_count"):
                raise ValueError("object count mismatch")
            if _content_root(entries) != marker.get("content_root"):
                raise ValueError("content root mismatch")
            values = self._verify_entries(project_id, generation_id, entries)
            return _CommittedGeneration(
                project_id=project_id,
                generation_id=generation_id,
                predecessor_generation_id=manifest.get("predecessor_generation_id"),
                objects=values,
                marker=marker,
            )
        except GenerationVerificationError:
            raise
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise GenerationVerificationError(f"committed generation is invalid: {generation_id}") from exc

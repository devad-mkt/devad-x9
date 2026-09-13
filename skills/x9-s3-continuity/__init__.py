"""Standalone, provider-offline S3 continuity primitives.

The package deliberately stops at an injected S3 SDK adapter.  It never
discovers credentials, creates a client, or performs a provider call by
itself.  ``ContaboS3Config`` supplies the non-secret options that an external
gate can use when constructing an established S3 SDK client.
"""

from .config import ConfigError, ContaboS3Config
from .crypto import (
    ClientSideEncryptor,
    DecryptionError,
    EncryptionUnavailable,
    EncryptedPayload,
)
from .provider import (
    CapabilityError,
    CapabilityProfile,
    CapabilityReport,
    InMemoryObjectStore,
    ObjectAlreadyExists,
    ObjectNotFound,
    ObjectStore,
    ProviderError,
    S3SdkObjectStore,
)
from .protocol import (
    GenerationConflict,
    GenerationIncomplete,
    GenerationReceipt,
    GenerationVerificationError,
    ProjectSelection,
    RestoreConflict,
    RestoreReceipt,
    RollbackUnavailable,
    S3ContinuityAddon,
    SelectionState,
    ValidationError,
)

__all__ = [
    "CapabilityError",
    "CapabilityProfile",
    "CapabilityReport",
    "ClientSideEncryptor",
    "ConfigError",
    "ContaboS3Config",
    "DecryptionError",
    "EncryptedPayload",
    "EncryptionUnavailable",
    "GenerationConflict",
    "GenerationIncomplete",
    "GenerationReceipt",
    "GenerationVerificationError",
    "InMemoryObjectStore",
    "ObjectAlreadyExists",
    "ObjectNotFound",
    "ObjectStore",
    "ProjectSelection",
    "ProviderError",
    "RestoreConflict",
    "RestoreReceipt",
    "RollbackUnavailable",
    "S3ContinuityAddon",
    "S3SdkObjectStore",
    "SelectionState",
    "ValidationError",
]

__version__ = "0.1.0"

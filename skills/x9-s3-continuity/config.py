"""Non-secret configuration for the Contabo-first S3 adapter boundary."""

from __future__ import annotations

from dataclasses import dataclass
import os
import re
from urllib.parse import urlparse


class ConfigError(ValueError):
    """Raised when addon configuration cannot be safely accepted."""


_ENV_NAME = re.compile(r"^[A-Z][A-Z0-9_]{1,127}$")
_NAMESPACE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")


def _env_name(value: str, field: str) -> str:
    if not isinstance(value, str) or not _ENV_NAME.fullmatch(value):
        raise ConfigError(f"{field} must be an uppercase environment variable name")
    return value


def _parse_bool(value: str, field: str) -> bool:
    normalized = str(value).strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ConfigError(f"{field} must be a boolean")


@dataclass(frozen=True)
class ContaboS3Config:
    """Safe SDK options; credential values are intentionally not fields."""

    provider: str = "contabo"
    endpoint: str = "https://eu2.contabostorage.com"
    region: str = "default"
    use_path_style_endpoint: bool = True
    bucket_env: str = "X9_CONTABO_S3_BUCKET"
    access_key_env: str = "X9_CONTABO_S3_ACCESS_KEY"
    secret_key_env: str = "X9_CONTABO_S3_SECRET"
    namespace: str = "x9-continuity"

    def __post_init__(self) -> None:
        if self.provider != "contabo":
            raise ConfigError("only the Contabo-first provider profile is supported")
        parsed = urlparse(self.endpoint)
        if (
            parsed.scheme != "https"
            or not parsed.netloc
            or parsed.path not in {"", "/"}
            or parsed.query
            or parsed.fragment
        ):
            raise ConfigError("endpoint must be an HTTPS origin without query or fragment")
        if not self.use_path_style_endpoint:
            raise ConfigError("path-style endpoint access is required for this profile")
        if not isinstance(self.region, str) or not self.region.strip():
            raise ConfigError("region must be non-empty")
        _env_name(self.bucket_env, "bucket_env")
        _env_name(self.access_key_env, "access_key_env")
        _env_name(self.secret_key_env, "secret_key_env")
        if not isinstance(self.namespace, str) or not _NAMESPACE.fullmatch(self.namespace):
            raise ConfigError("namespace must be a lowercase path-safe identifier")

    @classmethod
    def from_env(cls, environ: dict[str, str] | None = None) -> "ContaboS3Config":
        """Read only non-secret options and credential *names* from an env map."""

        env = os.environ if environ is None else environ
        return cls(
            endpoint=env.get("X9_CONTABO_S3_ENDPOINT", cls.endpoint),
            region=env.get("X9_CONTABO_S3_REGION", cls.region),
            use_path_style_endpoint=_parse_bool(
                env.get("X9_CONTABO_S3_USE_PATH_STYLE", "true"),
                "X9_CONTABO_S3_USE_PATH_STYLE",
            ),
            bucket_env=env.get("X9_CONTABO_S3_BUCKET_ENV", cls.bucket_env),
            access_key_env=env.get("X9_CONTABO_S3_ACCESS_KEY_ENV", cls.access_key_env),
            secret_key_env=env.get("X9_CONTABO_S3_SECRET_ENV", cls.secret_key_env),
            namespace=env.get("X9_CONTABO_S3_NAMESPACE", cls.namespace),
        )

    def sdk_options(self) -> dict[str, object]:
        """Return options safe to pass to an established S3 SDK factory.

        A caller must inject credentials and the bucket through its own
        owner-approved external gate.  This method never reads or returns
        credential values.
        """

        return {
            "version": "latest",
            "region": self.region,
            "endpoint": self.endpoint,
            "use_path_style_endpoint": self.use_path_style_endpoint,
        }

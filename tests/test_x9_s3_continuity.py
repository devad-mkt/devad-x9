from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "skills" / "x9-s3-continuity"


def load_package():
    spec = importlib.util.spec_from_file_location(
        "x9_s3_continuity",
        PACKAGE / "__init__.py",
        submodule_search_locations=[str(PACKAGE)],
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load S3 continuity package")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


x9 = load_package()


class S3ContinuityAddonTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = x9.ContaboS3Config()
        self.store = x9.InMemoryObjectStore(
            x9.CapabilityProfile(
                conditional_create=True,
                provider_checksums=True,
                versioning=True,
                retention=False,
            )
        )
        self.addon = x9.S3ContinuityAddon(
            self.store,
            x9.ClientSideEncryptor("test-key-v1", b"k" * 64),
            self.config,
        )
        self.selection = x9.ProjectSelection("project-alpha", x9.SelectionState.INCLUDED)

    def test_config_is_path_style_and_never_contains_credential_values(self) -> None:
        options = self.config.sdk_options()
        self.assertEqual("https://eu2.contabostorage.com", options["endpoint"])
        self.assertTrue(options["use_path_style_endpoint"])
        self.assertNotIn("key", options)
        self.assertNotIn("secret", options)
        configured = x9.ContaboS3Config.from_env(
            {
                "X9_CONTABO_S3_ENDPOINT": "https://storage.example.invalid",
                "X9_CONTABO_S3_USE_PATH_STYLE": "true",
                "X9_CONTABO_S3_BUCKET_ENV": "OWNER_BUCKET_NAME",
            }
        )
        self.assertEqual("OWNER_BUCKET_NAME", configured.bucket_env)
        self.assertEqual("https://storage.example.invalid", configured.endpoint)

    def test_selection_is_explicit_and_ambiguous_selection_fails_closed(self) -> None:
        for state in (x9.SelectionState.EXCLUDED, x9.SelectionState.AMBIGUOUS):
            with self.subTest(state=state):
                with self.assertRaises(x9.ValidationError):
                    self.addon.create_generation(
                        x9.ProjectSelection("project-alpha", state),
                        {"state.json": b"state"},
                        generation_id="gen-1",
                    )

    def test_aes_siv_binds_key_identity_and_object_identity(self) -> None:
        encryptor = x9.ClientSideEncryptor("key-v1", b"a" * 64)
        payload = encryptor.encrypt(b"secret", "gen-1", "objects/state")
        self.assertNotEqual(b"secret", payload.ciphertext)
        self.assertEqual(b"secret", encryptor.decrypt(payload, "gen-1", "objects/state"))
        with self.assertRaises(x9.DecryptionError):
            encryptor.decrypt(payload, "gen-2", "objects/state")
        with self.assertRaises(x9.DecryptionError):
            x9.ClientSideEncryptor("other-key", b"b" * 64).decrypt(
                payload, "gen-1", "objects/state"
            )

    def test_generation_puts_objects_and_manifest_before_commit_marker(self) -> None:
        receipt = self.addon.create_generation(
            self.selection,
            {"state.json": b"state", "memory/item.txt": b"memory"},
            generation_id="gen-1",
        )
        self.assertEqual(2, receipt.object_count)
        self.assertTrue(self.store.has(receipt.commit_key))
        self.assertEqual(receipt.commit_key, self.store.put_order[-1])
        self.assertIn("/MANIFEST.json", receipt.manifest_key)
        target: dict[str, bytes] = {}
        restored = self.addon.restore_into(self.selection, "gen-1", target)
        self.assertEqual(("memory/item.txt", "state.json"), restored.restored_keys)
        self.assertEqual({"state.json": b"state", "memory/item.txt": b"memory"}, target)

    def test_missing_conditional_create_blocks_before_any_put(self) -> None:
        store = x9.InMemoryObjectStore(x9.CapabilityProfile(conditional_create=False))
        addon = x9.S3ContinuityAddon(
            store, x9.ClientSideEncryptor("key-v1", b"a" * 64), self.config
        )
        with self.assertRaises(x9.CapabilityError):
            addon.create_generation(
                self.selection, {"state.json": b"state"}, generation_id="gen-1"
            )
        self.assertEqual([], store.put_order)

    def test_collision_and_incomplete_generation_fail_closed(self) -> None:
        self.addon.create_generation(
            self.selection, {"state.json": b"state"}, generation_id="gen-1"
        )
        with self.assertRaises(x9.GenerationConflict):
            self.addon.create_generation(
                self.selection, {"state.json": b"different"}, generation_id="gen-1"
            )
        self.store.delete("x9-continuity/projects/project-alpha/generations/gen-1/GENERATION_COMMITTED.json")
        with self.assertRaises(x9.GenerationIncomplete):
            self.addon.restore_into(self.selection, "gen-1", {})

    def test_every_object_is_verified_before_restore(self) -> None:
        receipt = self.addon.create_generation(
            self.selection, {"state.json": b"state"}, generation_id="gen-1"
        )
        object_key = next(
            key
            for key in self.store.put_order
            if key.endswith("/objects/state.json")
        )
        self.store.tamper(object_key, b"tampered")
        with self.assertRaises(x9.GenerationVerificationError):
            self.addon.restore_into(self.selection, "gen-1", {})
        self.assertTrue(self.store.has(receipt.commit_key))

    def test_restore_quarantines_existing_target_without_overwrite(self) -> None:
        self.addon.create_generation(
            self.selection,
            {"state.json": b"new-state", "new.txt": b"new"},
            generation_id="gen-1",
        )
        target = {"state.json": b"local-state"}
        receipt = self.addon.restore_into(self.selection, "gen-1", target)
        self.assertEqual(("new.txt",), receipt.restored_keys)
        self.assertEqual(("state.json",), receipt.quarantined_keys)
        self.assertEqual({"state.json": b"local-state", "new.txt": b"new"}, target)
        with self.assertRaises(x9.RestoreConflict):
            self.addon.restore_into(
                self.selection, "gen-1", {"state.json": b"local"}, conflict_policy="fail"
            )

    def test_rollback_restores_explicit_predecessor_without_delete(self) -> None:
        self.addon.create_generation(
            self.selection, {"state.json": b"one"}, generation_id="gen-1"
        )
        self.addon.create_generation(
            self.selection,
            {"state.json": b"two"},
            generation_id="gen-2",
            predecessor_generation_id="gen-1",
        )
        target: dict[str, bytes] = {}
        receipt = self.addon.rollback_to_previous(self.selection, "gen-2", target)
        self.assertEqual("gen-1", receipt.generation_id)
        self.assertEqual({"state.json": b"one"}, target)
        self.assertTrue(self.store.has("x9-continuity/projects/project-alpha/generations/gen-2/GENERATION_COMMITTED.json"))

    def test_fake_store_versions_and_bounded_delete_are_explicit(self) -> None:
        store = x9.InMemoryObjectStore(
            x9.CapabilityProfile(conditional_create=True, versioning=True)
        )
        store.put("versioned", b"one")
        store.put("versioned", b"two")
        versions = store.list_versions("versioned")
        self.assertEqual(2, len(versions))
        self.assertEqual(b"one", store.get("versioned", version_id=versions[0]["VersionId"]))
        self.assertEqual(b"two", store.get("versioned"))
        store.delete("versioned", version_id=versions[0]["VersionId"])
        self.assertEqual(1, len(store.list_versions("versioned")))

    def test_sdk_adapter_uses_path_style_and_conditional_put_without_constructing_client(self) -> None:
        class FakeClient:
            def __init__(self) -> None:
                self.calls: list[tuple[str, dict[str, object]]] = []

            def put_object(self, **kwargs):
                self.calls.append(("put_object", kwargs))

            def get_object(self, **kwargs):
                self.calls.append(("get_object", kwargs))
                return {"Body": b"data"}

            def delete_object(self, **kwargs):
                self.calls.append(("delete_object", kwargs))

            def list_object_versions(self, **kwargs):
                self.calls.append(("list_object_versions", kwargs))
                return {"Versions": []}

        client = FakeClient()
        store = x9.S3SdkObjectStore(
            client,
            "explicit-bucket-from-external-gate",
            x9.CapabilityProfile(conditional_create=True),
        )
        store.put("key", b"data", if_absent=True)
        self.assertEqual("*", client.calls[0][1]["IfNoneMatch"])
        self.assertEqual("explicit-bucket-from-external-gate", client.calls[0][1]["Bucket"])
        self.assertEqual(b"data", store.get("key"))

    def test_sdk_adapter_maps_conditional_collision_and_missing_object_statuses(self) -> None:
        class SdkError(Exception):
            def __init__(self, status: int) -> None:
                super().__init__(str(status))
                self.response = {"ResponseMetadata": {"HTTPStatusCode": status}}

        class ErrorClient:
            def put_object(self, **kwargs):
                raise SdkError(412)

            def get_object(self, **kwargs):
                raise SdkError(404)

        store = x9.S3SdkObjectStore(
            ErrorClient(), "explicit-bucket", x9.CapabilityProfile(conditional_create=True)
        )
        with self.assertRaises(x9.ObjectAlreadyExists):
            store.put("key", b"data", if_absent=True)
        with self.assertRaises(x9.ObjectNotFound):
            store.get("missing")


if __name__ == "__main__":
    unittest.main()

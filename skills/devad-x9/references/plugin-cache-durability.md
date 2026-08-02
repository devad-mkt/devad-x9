# Plugin Cache Durability

`devad-x9` and `cdx9-workspace-layout.md` are the canonical Devad workspace
policy. Files below `.codex\plugins\cache` are replaceable installation bytes;
a plugin update may overwrite a local safety amendment.

## Current bound override

| Item | Exact identity |
|---|---|
| Cached skill | `C:\Users\A-haj\.codex\plugins\cache\openai-curated-remote\superpowers\6.1.1\skills\using-git-worktrees\SKILL.md` |
| Expected SHA-256 | `40327EAFCEA2FF62EAC8B1A6F68EC2891E09DFF3CFCA92983BEB60CEAD8522DB` |
| User-owned patch | `..\assets\superpowers-6.1.1-devad-worktree-override.patch` |
| Patch SHA-256 | `7CCC3D2712BBBF7D02CCB974EEBCC30B9DFB38AEF37CEF3F62CE1C66A9F388A7` |

The cached skill must state that Devad uses only an already verified worktree
or a host-created native worktree under `D:\CDx9\0-cdx-wt`, disables manual
Step 1b and `.worktrees` fallback, and preserves active/dirty/unknown
worktrees.

## Drift handling

1. Hash-check the cached skill before Devad worktree creation or dispatch.
2. On exact match, continue under `devad-x9` authority.
3. On missing file, new plugin version, or hash mismatch, return
   `PLUGIN_CACHE_NON_DURABLE` and make no worktree/path mutation.
4. Inspect the new upstream skill and the user-owned patch. Reapply the
   invariant through the skill-update workflow only when it still fits the new
   version; never auto-apply a stale patch to unknown bytes.
5. Forward-test the bad root-level-helper scenario, validate the skill, and
   update this version/path/hash record after acceptance.

The patch is recovery input, not permission to mutate a plugin cache or create
a worktree.

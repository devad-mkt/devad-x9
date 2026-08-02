# Devad X9 Existing-System Ownership Miss

## Repository Lesson

Before a Devad Worker adds or replaces behavior, verify the current branch
contains the expected accepted app-domain commits and locate the canonical
owner through current call sites. A handoff or Sheet without matching current
bytes is advisory; a merge without an ownership rebind is incomplete context.

For cross-app work, preserve the owning service/API. Do not duplicate provider
lists, destination catalogs, settings, queues, policies, or tables inside the
consumer domain. Bind one focused seam test. If ownership remains unknown,
pause only that claim and continue non-conflicting work.

## Semantic Merge Rebind

Commit ancestry is provenance, not behavioral acceptance. A merge can contain
the accepted predecessor as a parent while retaining a stale blob or resolving
the user-visible behavior incorrectly.

For an owner-approved surface that crosses divergent histories:

1. Before integration, bind the accepted commit, decisive paths, expected
   blobs where byte identity is still valid, and the smallest semantic
   regression test.
2. After the merge or cherry-pick, inspect the resulting integration-tip
   blobs and rerun that regression test there. Do not accept reachability,
   conflict-free merge output, CI, or deployment health as semantic parity.
3. Let later legitimate changes differ byte-for-byte only when the focused
   contract still proves the approved behavior.
4. Start downstream Workers from the refreshed integration SHA. Do not use an
   old release branch as the continuing source or replay its whole history.

For Devad release generations, frozen R0 is historical foundation and rollback
provenance; current integrated `main` is source authority. R1 Workers return
narrow reviewed changes to that current authority. Consumer domains must use
the current owning app seam instead of copying an older app version.

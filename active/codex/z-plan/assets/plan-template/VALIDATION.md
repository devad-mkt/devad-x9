# <Project or Feature> Plan Package Validation

Date: <YYYY-MM-DD>
Scope: documentation package only
Status: `PASS/FAIL/PENDING`

| Check | Result | Evidence |
|---|---|---|
| Canonical PLAN exists | `<status>` | `<path/hash>` |
| Routed paths resolve | `<status>` | `<check>` |
| Authority/receipt identities match | `<status>` | `<paths/hashes>` |
| Preserved artifacts unchanged | `<status>` | `<bytes/hashes>` |
| Encoding/final newline/Markdown | `<status>` | `<check>` |
| Intended files only | `<status>` | `<Git status>` |
| Runtime/browser/connector checks | `<status>` | `<PASS/NOT_RUN/N/A>` |
| Durability | `<status>` | `<commit/push identity or LOCAL_ONLY>` |

This validates plan-package integrity. It does not prove product behavior.

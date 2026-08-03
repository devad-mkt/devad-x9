# Source-Backed Project Intelligence

Before planning and before the first behavioral edit, bind current repository
evidence instead of relying on chat memory.

For each touched capability, record the current Git SHA and the smallest source
evidence needed to answer:

```text
EXISTING_FEATURE / UI_SETTINGS / SERVER_AUTHORITY
PERSISTENCE_OR_RUNTIME / INTEGRATED_HISTORY / TEST_PROOF
GAP / CHANGE_MODE: REUSE | EXTEND | NEW | REPLACE_AUTHORIZED
```

`NEW` requires source-backed absence in the claimed scope.
`REPLACE_AUTHORIZED` requires an explicit owner decision. Memory, chat, RAG,
screenshots, and external notes may locate evidence but cannot prove authority.

A compact `CONTEXT_CAPSULE.json` may bind repository-relative paths, file
hashes, spans, and proof references. Re-read its source evidence before coding
when the current SHA has changed. The capsule and any docs/memory generated
from it are advisory; current Git and accepted result receipts remain truth.

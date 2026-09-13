# chunk-<NN> — <short-title>

**Wave <N>. <Serial|Parallel>. Depends on chunk-<XX>. <BLOCKS everything else | optional>**

## Goal

Add the "<short-title>" capability to `<plugin-name>` so <state> can <behavior>. Everything here runs against local fakes; no real network calls, no `sys.path`, no scope creep beyond this chunk's files.

## Files to write

### 1. NEW `<build-root>\<plugin-name>\helpers\<feature>.py`

Full module. Implement exactly these functions (signatures from `03-target-architecture.md` §3):

```python
def <signature>(config: "dict", <arg>) -> "<ret>": ...
    """<one-line behavior>"""
```

All persistence via the secure-write helper; all deletes confined to plugin-owned paths.

### 2. REWRITE `<build-root>\<plugin-name>\helpers\<old>.py`

Keep the entire existing module. Change only:
- add a new `<key>` to <scopes map>
- add `<api>` and `<version>` to <service map>
- replace <logic> to use the keyed path from the new helper
- keep every existing public function and its signature

## Acceptance

```bash
cd <build-root>\<plugin-name>
python -m py_compile helpers\<new>.py helpers\<old>.py
python -c "import sys; sys.path.insert(0,'.'); from helpers import <new>, <old>; print('imports OK')"
python -m pytest tests\<test>.py -q    # if the test exists yet; else note and skip
```

PASS = compiles + imports OK (+ tests green if the file exists). Report exact output.

## DO NOT
- Do not change any tool files in this chunk.
- Do not remove existing public functions.
- Do not add new pip dependencies.
- Do not touch files outside the paths listed above.
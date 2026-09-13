# AUDIT-REPORT — <plugin-name>

Audit date: <date> · Plugin root: `<plugin-root>` · Contract ref: `ref/a0-plugin-contract.md`

## Summary

< 1-2 lines: verdict healthy / needs fixes; how many FAIL / WARN items >

## Checklist results

| # | Check | Result | Evidence (file:line / command output) |
|---|-------|--------|----------------------------------------|
| 1 | hooks side effects / uninstall parity | <PASS/FAIL/WARN> | <evidence> |
| 2 | filename / stale refs |  |  |
| 3 | imports (`usr.plugins`, no `sys.path`) |  |  |
| 4 | frontend Store Gate / notifications |  |  |
| 5 | manifest + configs parse |  |  |
| 6 | gates re-run (compile/yaml/pytest/sim) |  |  |
| 7 | counts vs claim |  |  |

Full shop checklist: `ref/audit-checklist.md` (run every item even ones that pass; record PASS with evidence).

## Real commands run

```bash
python -m py_compile <new files...>        # exit 0
python -c "import yaml; yaml.safe_load(open('plugin.yaml'))"
python -m pytest tests -q
python tests/simulate_e2e.py               # ALL PASS, exit 0
<frontend greps: store gate / toastFrontend / sys.path / initialize\.py>
```

## Fix plan (from FAIL/WARN items)

| Priority | File | Change | Risk | Status |
|----------|------|--------|------|--------|
| <high/med/low> | <path> | <1-line fix> | <low/med> | <done | recommended> |

Order smallest-first: rename → import → frontend.

Grub: even "minor" FAILs matter (orphan skill dirs, stale UI error blocks, misspoken README counts).
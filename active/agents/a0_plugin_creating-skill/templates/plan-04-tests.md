# 04 — Test Strategy (dry-run only)

## Rule

No real network calls anywhere. Every Google/external API and credential store is replaced with a local fake. Test files under the plugin's `tests\` folder, shipped with the build.

## 1. Mock strategy

| Layer | Fake | How |
| --- | --- | --- |
| `<external> client build` | fake service object | monkeypatch `build(...)` to return a chainable `FakeService` |
| `<api>` responses | fake method returns canned JSON | `FakeMethod` record-with-result |
| credential/state files | temp dirs + registry freezes | tests create their own `data/` |
| time/PKCE (if any) | deterministic, per-key temp files | prevents two flows clobbering |

## 2. Test files

| File | Proves |
| --- | --- |
| `test_<feature1>.py` | multi-<item> keying, resolution order, migration |
| `test_<feature2>.py` | new enabled service tools honor toggles + account param |
| `test_<plugin>\_test.py` (separate plugin) | separate-plugin routing + imports |
| `simulate_e2e.py` | full user journey against fakes; prints `ALL PASS`, exit 0 |

## 3. Simulation harness

`tests/simulate_e2e.py` bootstraps the plugin with fakes on a real Python path, walks the happy path (auth → register → tool call → response), prints `ALL PASS`, and exits 0. Gate: must run before declaring the build complete.

## 4. Gates that must pass (in order)

```bash
cd <build-root>\<plugin-name>
python -m py_compile helpers\*.py tools\*.py api\*.py          # syntax
python -c "import yaml; yaml.safe_load(open('plugin.yaml'))"    # manifest parses
python -m pytest tests -q                                       # unit
python tests\simulate_e2e.py                                     # ALL PASS, exit 0
```

PASS = every command exits 0. Fix and re-run only the failing command.
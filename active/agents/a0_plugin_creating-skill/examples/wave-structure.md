# Execution waves excerpt (from a0-gsp-builder/SKILL.md)

The builder skill defines the whole build as serial/parallel waves with hard gates. The wave chart (below, verbatim) is the skeleton every implementation must respect.

## 1. Execution waves (respect dependencies)

```
WAVE 0 (serial):   chunk-00  scaffold
WAVE 1 (serial):   chunk-01  auth core (accounts.py + google_auth.py rewrite)
WAVE 2 (serial):   chunk-02  config API + Accounts WebUI tab
WAVE 3 (serial):   chunk-03  patch 23 existing tools with account param
GATE A: run syntax gate + test_multi_account.py — must pass before continuing
WAVE 4 (PARALLEL — spawn up to 4 sub-agents, one per chunk):
                   chunk-04  docs service
                   chunk-05  slides service
                   chunk-06  ga4 service
                   chunk-07  gsc service
WAVE 5 (serial):   chunk-08  WebUI new-service tabs + default_config update
WAVE 6 (PARALLEL — 2 sub-agents):
                   chunk-09  new skills (docs/slides/analytics)
                   chunk-10  google_ads plugin (full separate plugin)
GATE B: syntax gate + test_new_services.py + test_ads.py
WAVE 7 (serial):   chunk-11  test suite + simulate_e2e harness (must exit 0)
WAVE 8 (serial):   chunk-12  docs/README + final validation report
```

Note the pattern: serial foundation waves (long serial wave 0-3), a gate, then parallel execution waves for independent services, then more gates and final waves.
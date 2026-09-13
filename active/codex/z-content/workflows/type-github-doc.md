# Workflow: GitHub / Developer Doc — compact

Handles READMEs, API references, CLI tutorials, SDK guides, and repository docs. Load `SKILL.md` first.

## Required order

```text
title + one-sentence architecture → exact prerequisites/install
→ runnable quickstart → API/parameter table → examples
→ troubleshooting → configuration → contribution/license
```

Start with one SVO sentence describing the module. State exact versions, OS limits, dependencies, defaults, and working directory. Use copy-paste commands with comments and expected output where useful. Make code examples syntactically valid, runnable, and realistic; explain non-obvious parameters inline.

## Reference tables and errors

Include every source parameter with exact `Type`, `Required` (`Yes`/`No`), default (`—` when absent), valid values, constraints, and behavior:

`| Parameter | Type | Required | Default | Description & constraints |`

Cover the top 5–10 real errors when evidence exists. Each row states the exact symptom, specific root cause, and copy-paste command or exact configuration fix. Do not write “check your input”.

## Style and QA

Use imperative instructions: Run, Configure, Pass, Install, Build, Test, Set, Verify, or Specify. Remove marketing language and filler such as “simply”, “just”, “let’s”, and “as you can see”. Explain behavior through code, parameters, and constraints.

- Every code block is valid and runnable.
- Every source parameter appears in the table.
- Versions and errors are precise.
- Instructions use imperative mood.
- No invented API behavior, limits, or credentials.

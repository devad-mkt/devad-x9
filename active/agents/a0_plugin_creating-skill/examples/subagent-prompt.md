# Sub-agent prompt excerpt (from a0-gsp-builder/SKILL.md)

For each parallel wave, the builder must spawn a subordinate agent using a strict prompt template so cheap models stay on-rails.

## 2. Sub-agent protocol (waves 4 and 6)

For each parallel chunk, spawn a subordinate agent with a prompt shaped exactly like:

```
You are implementing <chunk-file-name> of the a0-google-suite-plus build.
Read these two files first:
1. $DEVAD_TOOLS_ROOT\10-Other\0a-plugins\a0_google_suite_plus\plan_search-files\03-target-architecture.md
2. $DEVAD_TOOLS_ROOT\10-Other\0a-plugins\a0_google_suite_plus\skills\a0-gsp-builder\chunks\<chunk-file-name>
Write ONLY the files listed in the chunk's "Files to write" section, at the exact paths given.
Run the chunk's acceptance commands. Report back: files written, command output, PASS/FAIL.
Do not touch any other file. Do not redesign. Follow the chunk literally.
```

Collect all sub-agent reports before starting the next wave. If any sub-agent reports FAIL, fix its chunk yourself before continuing.
# Content Agent refresh-snapshot source-map lesson

- Task type: read-only Laravel source map before a bounded implementation slice.
- What helped: the reader identified `AiTaskDistributionSnapshotService::copyCanonical()` as the existing canonical seam and separated future task configuration from current-generation lifecycle state.
- Quality gain: this avoided inventing a draft generation or a second snapshot service, preserved the one-open-automation invariant, and focused proof on immutable generation N plus refreshed generation N+1.
- Cost control: one source-map pass was enough; no second architecture review was needed before TDD.
- Reuse: for future immutable-activation systems, ask the reader to find the mutable future-config seam, immutable runtime boundary, and narrowest existing canonical rebuild method.

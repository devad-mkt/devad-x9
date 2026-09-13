# Loop Subagents v1.1 lessons

## What worked

- One product slice at a time kept evidence, implementation, and review bounded.
- Independent acceptance review found conditional-state and lifecycle gaps that implementation reports missed.
- Parent-side hash checks, focused tests, and browser proof caught different classes of defects.

## Known limitation

- The contract verified the accepted current slice but did not require an explicit historical feature-retention denominator. A narrow packet could therefore pass while an older, richer implementation remained silently absent.

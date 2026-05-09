# Final Audit

## Scope

This repo was audited for:

- extraction correctness
- config behavior under environment overrides
- repository hygiene
- GitHub discoverability readiness

## Fixes applied

- Added derived field synchronization for `PageSignals`
- Hardened JSON-LD schema extraction for nested and non-trivial payloads
- Fixed config cache invalidation so env-based tests and runtime overrides behave correctly
- Corrected an incorrect unit-test expectation for title length
- Added missing professional repo files such as `LICENSE`, `AUTHORS.md`, `CONTRIBUTING.md`, `SECURITY.md`, issue templates, and `CODEOWNERS`
- Added GitHub-facing description/topic metadata and a repo-health workflow

## Verification

Run:

```bash
python -m pytest tests -q
```

Expected result after the fixes:

- all tests passing

## Notes

`docs/social-preview.svg` is included as a repository hero asset. If you want GitHub link cards to use it, upload it manually in the repo's **Settings > Social preview** UI.

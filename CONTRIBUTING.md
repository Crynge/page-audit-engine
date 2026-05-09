# Contributing

Thanks for contributing to `page-audit-engine`.

## Development flow

1. Fork the repository.
2. Create a focused branch.
3. Make changes with tests.
4. Run:

```bash
python -m pytest tests -q
```

5. Open a pull request with:
   - what changed
   - why it changed
   - how it was verified

## Scope

Good contributions include:

- extraction accuracy improvements
- provider compatibility fixes
- JSON contract hardening
- CLI usability improvements
- audit quality upgrades for GEO, AEO, and VEO
- docs and sample automation improvements

## Standards

- Prefer small, reviewable pull requests.
- Keep public output deterministic where possible.
- Preserve the JSON response contract unless clearly versioned.

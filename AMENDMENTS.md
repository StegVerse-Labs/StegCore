# Amendments — How to Change StegCore

StegCore changes are constitutional.

## Required Process

1. Open a Pull Request against `main`
2. Describe:
   - What boundary/authority/accountability rule changes
   - Why the change is necessary (failure mode addressed)
   - Expected impacts on downstream modules
3. Update:
   - `CONSTITUTIONAL_CHANGELOG.md`
4. Ensure:
   - BCAT Gate passes
   - Human review approves

## Forbidden

- Direct pushes to `main`
- Unreviewed authority changes
- Removing refusal-as-success invariants

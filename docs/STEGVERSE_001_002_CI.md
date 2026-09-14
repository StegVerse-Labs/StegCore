# StegVerse-001 / StegVerse-002 CI

Canonical workflow: `.github/workflows/stegverse-001-002-validator.yml`.

The workflow validates baseline vectors, unit tests, registry paths, activation-registry tests, activation-updater tests, and a non-mutating updater dry-run. Normal CI must not promote the registry; promotion follows only after a passing CI result and uses the guarded updater semantics.

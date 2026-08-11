# Changelog

All notable current-product changes are recorded here using Semantic Versioning.
Historical governance, schema, receipt, and research artifact versions retain their own independent version identities.

## [Unreleased]

### Changed
- Keep live product documentation, runtime identity, packaging, and consumer evidence aligned through the repository consistency verifier.

## [0.2.0] - 2026-08-10

### Added
- Canonical StegGate HTTP service with `/health`, `/v1/runtime-identity`, `/v1/capabilities`, `/v1/evaluate`, and `/v1/self-test`.
- Four-disposition `ALLOW | DENY | REVIEW | FAIL_CLOSED` evaluation surface bound to the canonical three-layer StegCore runtime.
- Transport-independent runtime identity contract.
- Portable `steggate` CLI for identity inspection, self-test, JSON evaluation, and local service execution.
- Canonical portable-product documentation and consistency verification.

### Changed
- Product/package/service version identity is aligned at `0.2.0`.
- README now describes the implemented runtime rather than the earlier documentation-first scaffold posture.
- StegGate interfaces are explicitly adapters onto one canonical admissibility path; they are not independent policy engines.

### Preserved boundaries
- `ALLOW` does not imply execution.
- StegCore does not mint Continuity receipts or become identity, custody, publication, or provider authority.
- Historical artifact/schema versions are not rewritten to match the current product version.

## [0.1.0] - 2026-01-14

### Added
- Initial public StegCore governance boundary, documentation baseline, and supporting substrate.

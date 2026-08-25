# Changelog

All notable current-product changes are recorded here using Semantic Versioning.
Historical governance, schema, receipt, and research artifact versions retain their own independent version identities.

## [Unreleased]

### Added
- AdmittedCode performance policy, benchmark runner, hosted benchmark workflow, benchmark contract tests, and versioned JSON performance receipts.
- Measurement coverage for decision correctness, false ALLOW/DENY behavior, FAIL_CLOSED integrity, candidate binding, semantic replay, cross-interface equivalence, latency percentiles, throughput, CPU/memory observations, cold start, governance overhead, runtime identity, and four-application integration progress.
- Provisional hosted performance baseline grounded in two successful comparable workflow receipts, with versioned regression reports and conservative warning bands.
- Hosted localhost HTTP-path timing/identity/correctness measurement for the packaged service surface.
- Automated clean-environment onboarding rehearsal plus a separate unfamiliar-human observation template; CI is explicitly prohibited from fabricating human usability timing.

### Changed
- Keep live product documentation, runtime identity, packaging, consumer evidence, performance baselines, onboarding evidence, and release measurement surfaces aligned through repository consistency verification.
- Release candidates now compare against the compatible AdmittedCode hosted baseline and retain HTTP/performance regression evidence before a release PR is opened.

## [0.3.0] - 2026-08-25

### Added
- Canonical SPE standing receipt verification and fail-closed standing binding for standing-required consequences.
- Exact interlock, participant, package, transition, and run identity continuity checks across the standing boundary.
- Bounded public interlock traversal through current standing, canonical StegGate admissibility, commit coherence, and exactly one bounded consequence.
- Negative-path coverage proving missing, stale, tampered, denied, or mismatched standing/interlock evidence cannot invoke the bounded consequence executor.

### Changed
- Product/package/service identity advances to `0.3.0` while preserving runtime identity `stegverse:steggate:canonical:three-layer:v1`.
- Product consistency now includes the current standing-required consequence semantics and release-candidate identity surfaces.

### Preserved boundaries
- SPE standing ALLOW does not itself authorize execution.
- StegGate ALLOW does not prove execution occurred.
- StegCore does not mint SPE standing, Continuity receipts, Master Records custody, credential authority, or release authority.
- Release and credential authority remain TV/TVC.

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

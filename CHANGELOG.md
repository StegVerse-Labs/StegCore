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
- Canonical fail-closed verification of required SDK/SPE standing evidence inside `governed_steggate_execute`.
- Exact package, transition, run, participant, ingress-interlock, candidate, envelope, standing-receipt, and bridge hash binding before consequence execution.
- Canonical bounded public-interlock traversal proof from participant/interlock identity through standing, StegGate admissibility, commit coherence, and exactly one bounded executor invocation.
- Negative proof that missing, stale, DENY, tampered, or mismatched standing/interlock evidence remains unable to reach the executor.

### Preserved boundaries
- SDK and SPE remain non-authorizing.
- Canonical StegGate remains the present-tense admissibility and consequence boundary.
- Master Records custody does not grant execution or admissibility authority.
- Model output, transport identity, workflow success, and release metadata do not grant execution authority.

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

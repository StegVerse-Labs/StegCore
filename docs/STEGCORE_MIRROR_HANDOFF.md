# StegCore Mirror Handoff

## Current goal

```text
Goal: bind StegCore decisions to a fail-closed runtime boundary
Repository: StegVerse-Labs/StegCore
Branch: build/governed-runtime-v7
Task: issue #16
Pull request: #17
Source of truth: repository-local docs and validators
```

## Repository boundary

StegCore decides whether an action is permitted given already-verified continuity evidence. It does not verify or mint continuity receipts and does not store identity. Those responsibilities remain with StegID and the Continuity receipt-governance layer.

Documentation wins if implementation and documentation diverge.

## Session decisions preserved

1. StegCore is the correct repository for runtime-governance and consequence-bearing execution checks.
2. The retained execution flow is:

   `verified continuity input -> StegCore decision -> execute or refuse -> local execution observation`

3. Prior prototype bundles `stegcore_gate_bundle_v1` through `stegcore_gate_bundle_v6` are design evidence only and must not be installed wholesale.
4. Retained concepts:
   - mandatory fail-closed execution boundary;
   - explicit `allow`, `deny`, and `defer` handling;
   - deterministic pre/post hashing;
   - structured execution/refusal observation;
   - injected execution callback rather than an unrestricted command endpoint.
5. Superseded prototype components:
   - embedded authority signing and demo HMAC secret;
   - local continuity-signature verification;
   - receipt-chain minting inside StegCore;
   - public unrestricted command execution;
   - a new standalone workflow for this task.

## Built files

```text
src/stegcore/runtime.py
tests/test_runtime.py
src/stegcore/__init__.py
docs/STEGCORE_MIRROR_HANDOFF.md
```

## Runtime behavior

`src/stegcore/runtime.py`:

- accepts the canonical `DecisionRequest`;
- calls `decide()` from `src/stegcore/decision.py`;
- invokes the injected callback only when the decision is `allow`;
- never invokes the callback for `deny` or `defer`;
- captures callback failure as `failed` without converting it into successful execution;
- emits `stegcore.execution_observation`, explicitly not a continuity receipt;
- records deterministic pre-state and post-state SHA-256 hashes over declared JSON-compatible state.

## Tests added

`tests/test_runtime.py` covers:

- allow executes exactly once;
- deny invokes the executor zero times;
- defer invokes the executor zero times;
- execution observations have no receipt identifier or signature surface;
- executor exceptions produce a failed observation.

## Known blockers and cautions

- Validation has not yet been observed through repository CI or an external test run.
- Policy shapes remain descriptive in v0.1; this implementation binds the canonical decision output but does not invent a new policy engine.
- The execution observation is local evidence only and must not be presented as a continuity receipt.
- Integrating applications remain responsible for the actual callback and for forwarding evidence to the appropriate external receipt layer.

## Ownership

```text
Implementation owner: branch build/governed-runtime-v7
Durable task owner: StegVerse-Labs/StegCore issue #16
Review and validation owner: StegVerse-Labs/StegCore pull request #17
Review/merge owner: repository maintainers
Continuity verification and receipt owner: StegID / Continuity layers
```

## Remaining work

1. Obtain test validation and attach results to pull request #17 or issue #16.
2. Correct any review or CI findings.
3. Merge after repository maintainers accept the runtime boundary.
4. After merge, assess release/tag readiness.
5. If release-ready, create a follow-up verification task for propagation or references in:
   - `StegVerse-Labs/Site`;
   - `GCAT-BCAT-Engine/Publisher`;
   - `StegVerse-Labs/admissibility-wiki`;
   - the canonical StegGuardian wiki repository.

## Permitted continuation scope

The continuation may modify the minimal runtime boundary, tests, exports, documentation, task records, and PR evidence necessary to prove that StegCore decisions bind execution. It must not absorb identity, continuity verification, continuity receipt minting, or unrestricted command orchestration.

## Archive readiness

```text
thread_archive_ready: true
reason: all session-specific decisions, code, ownership, blockers, remaining work, validation requirements, and continuation scope are durable in this handoff, issue #16, branch build/governed-runtime-v7, and draft pull request #17
pending_validation_owner: pull request #17 and repository maintainers
conversation_required_for_continuation: false
```

## Progress snapshot

```text
StegVerse-Labs - 82% complete
StegCore - 75% complete
StegCore - 90% complete TO GOAL ACTIVATION
Fully developed files vs scaffolding and stubs: 71% developed / 29% scaffolding and unvalidated runtime surfaces
Delta: the prior unintegrated v1-v6 prototype line is now a repository-aligned fail-closed runtime implementation with durable issue, branch, handoff, and draft PR ownership; only recorded validation, review, and merge remain.
```

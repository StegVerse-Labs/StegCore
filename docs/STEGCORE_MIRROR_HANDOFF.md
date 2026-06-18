# StegCore Mirror Handoff

Generated: 2026-06-17

## Purpose

This file is the local StegCore handoff equivalent for mirror/build continuity.

It exists because this session is not currently working inside `/Site` or `/Publisher`, but the current build still needs a repo-local handoff source of truth before continuing additional mirror-style or cross-repo integration work.

## Active Repository

`StegVerse-Labs/StegCore`

## Active Branch

`build/001-002-decision-bridge`

## Active Pull Request

PR #15: Add 001/002 decision bridge

## Current Goal

Activate the StegVerse-001 / StegVerse-002 controlled continuity + master-record ingestion baseline inside StegCore.

## Current Scope

This repo is responsible for the commit-time admissibility and native decision bridge layer.

StegCore is not the continuity truth system.

StegCore does not mint receipts.

StegCore does not store identity.

StegCore consumes verified or schema-shaped continuity/entity records and produces native decision posture.

## Installed Work on Main Before This Branch

The following 001/002 adapter baseline was installed on main before the decision-bridge branch:

```text
docs/STEGCORE_001_002_REPO_ALIGNED_ADAPTER.md
src/stegcore/adapters/__init__.py
src/stegcore/adapters/entity_001_002.py
tests/test_entity_001_002_adapter.py
tests/fixtures/entity_records/continuity_allow.json
tests/fixtures/entity_records/master_ingestion_public_raw_deny.json
tests/fixtures/entity_records/master_ingestion_refusal.json
tests/fixtures/entity_records/master_ingestion_override_required.json
.github/workflows/validate-001-002-adapter.yml
```

## Current Branch Work

The current branch adds:

```text
.github/workflows/validate-001-002-decision-bridge.yml
docs/STEGCORE_001_002_DECISION_BRIDGE.md
docs/STEGCORE_001_002_PROOF_PATH.md
docs/STEGCORE_MIRROR_HANDOFF.md
src/stegcore/adapters/decision_bridge.py
tests/test_001_002_proof_path_matrix.py
tests/test_entity_001_002_decision_bridge.py
```

## Decision Bridge Mapping

| Adapter Status | Native StegCore Decision | Reason Code |
|---|---|---|
| allow | allow | entity_001_002.allow |
| deny | deny | entity_001_002.deny |
| drift | defer | entity_001_002.drift |
| stale | defer | entity_001_002.stale |
| refusal | defer | entity_001_002.refusal |
| override_required | defer | entity_001_002.override_required |

## Proof Path Cases

| Case | Entity | Native Decision | Reason Code |
|---|---|---|---|
| Valid continuity record | StegVerse-001 | allow | entity_001_002.allow |
| Evidence requires review | StegVerse-001 | defer | entity_001_002.stale |
| Restricted records access violation | StegVerse-002 | deny | entity_001_002.deny |
| Reviewer refusal | StegVerse-002 | defer | entity_001_002.refusal |
| Override authority not verified | StegVerse-002 | defer | entity_001_002.override_required |

## Governance Rules Preserved

Continuity is not approval.

Execution is not admissibility.

Visibility is not governance.

Discovery is not execution authority.

Reviewer is not override authority.

A refusal must bind consequence unless explicit override authority exists.

## Verification Command

Run:

```bash
PYTHONPATH=src python -m unittest discover -s tests
```

## Known Delta

The standalone JSON proof-path runner was built and locally verified in a downloadable pack but was not installed directly because the connector blocked the script write.

The repo branch now includes equivalent proof-path matrix coverage in `tests/test_001_002_proof_path_matrix.py`.

## Next Build Step

1. Confirm PR #15 CI status.
2. If CI passes, merge PR #15 or prepare final review notes.
3. After merge, add the next integration layer that connects StegCore decisions back to the StegVerse-001 / StegVerse-002 activation manifest registry.

## Archive Readiness

This handoff captures the current StegCore thread state so a future session can continue without needing the full chat transcript.

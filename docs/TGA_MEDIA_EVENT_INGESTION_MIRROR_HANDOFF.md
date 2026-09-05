# TGA_MEDIA_EVENT_INGESTION_MIRROR_HANDOFF.md

Status: ACTIVE_SOURCE_BUILD
Updated: 2026-09-05
Organization: StegVerse-Labs
Repository: StegVerse-Labs/StegCore
Branch: feature/tga-media-ingestion
Goal ID: TGA-MEDIA-001
Parent goal: TGA-001
Parent handoff: `docs/TEMPORAL_GOVERNED_ANALYSIS_MIRROR_HANDOFF.md`

## Mission

Build the generalized governed media/event-ingestion adapter that converts externally addressable temporal media references and bounded observation assertions into canonical TGA event inputs without acquiring, redistributing, or asserting custody of the underlying media.

## Source-of-truth boundary

This handoff is the canonical continuation record for the TGA media/event-ingestion successor. It supplements the repository-wide StegCore handoff and the completed TGA-001 handoff.

## Core invariants

1. Media custody is separate from analysis ingestion.
2. A source reference is not proof of source authenticity.
3. Exact temporal windows are mandatory for event-level media analysis.
4. Source hashes are retained when supplied; absence of a hash remains explicit.
5. Observation assertions remain interpretive encodings, not ground truth.
6. No media downloader, scraper, platform credential, or redistribution path is part of this goal.
7. No legal, officiating, enforcement, publication, or adjudicative authority is created.
8. Ingestion may fail closed on malformed windows, unsupported custody claims, or missing provenance.
9. Multiple observation assertions may bind to the same temporal window while preserving independent evidence references and uncertainty.
10. The adapter outputs canonical TGA event input only; rule/law evaluation remains owned by `stegcore.temporal_governed_analysis`.

## Source-complete target

- generalized media-source reference schema;
- temporal-window normalization and validation;
- custody posture vocabulary that never implies ownership from availability;
- deterministic event-ingestion adapter producing TGA temporal-event compatible records;
- source/provenance binding and non-ground-truth assertion enforcement;
- tests for exact offsets, missing hashes, external-reference-only custody, invalid windows, and observation uncertainty preservation;
- no network fetch or media acquisition in tests or source.

## Authority boundary

```text
authority_effect = NONE_ANALYSIS_INGESTION_ONLY
media_custody = NOT_INFERRED
network_fetch = NONE
runtime_activation_claim = NONE
```

## Planned files

Destination `StegVerse-Labs/StegCore`:

- `schemas/media-source-reference.schema.json`
- `src/stegcore/temporal_media_ingestion.py`
- `tests/test_temporal_media_ingestion.py`
- `fixtures/temporal-governed-analysis/media-reference-baseball.json`
- `.github/workflows/temporal-media-ingestion.yml`

## Downstream after validated merge

- update StegIndex `tga_media_ingestion_adapter_available` only after canonical evidence exists;
- Site projection remains separately orchestrated and must not be claimed while Site disallows external task ownership;
- Publisher/admissibility-wiki/stegguardian-wiki remain pending their own owner evidence.

```yaml
source_state: ACTIVE_BUILD
validation_state: NOT_YET_OBSERVED
merge_state: NOT_YET_MERGED
user_action_required: false
thread_archive_ready: false
```

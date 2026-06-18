# Install: StegVerse-001 AI Systems Comparison Package

Generated: `2026-06-15`

## Assumptions

- Target repository uses a standard documentation directory.
- The intended target path is `docs/comparisons/`.
- This package is documentation-only.
- No runtime code, workflow, or deployment behavior is changed by installing it.

## What done looks like

Installation is complete when:

1. all files in this package are present under `docs/comparisons/`;
2. the root README or site includes the short comparison excerpt;
3. the canonical long-form file is linked from the README or documentation index;
4. the machine-readable JSON file validates as JSON;
5. public-facing language does not claim model superiority, consciousness, sovereignty, or self-accreditation.

## Files to add

Copy the following files into the target repository:

```text
docs/comparisons/STEGVERSE_001_AND_CONTEMPORARY_AI_SYSTEMS.md
docs/comparisons/README_COMPARISON_EXCERPT.md
docs/comparisons/stegverse_001_ai_systems_comparison.json
docs/comparisons/INDEX.md
docs/comparisons/INSTALL.md
docs/comparisons/comparison_manifest.json
```

## Suggested README patch

Add this section to the repository root README where comparison or positioning language belongs:

```markdown
## Comparison to Contemporary AI Systems

StegVerse-001 is not a frontier-model competitor.

It is a governance/control-plane architecture for consequence-bearing AI transitions.

Contemporary AI systems mostly govern what models may say, access, or call. StegVerse governs whether a proposed transition may become part of system reality.

In this context, an **AI entity** means:

> A bounded, receipt-bearing, consequence-capable work-entity whose authority is externally accredited and revocable.

See [`docs/comparisons/STEGVERSE_001_AND_CONTEMPORARY_AI_SYSTEMS.md`](docs/comparisons/STEGVERSE_001_AND_CONTEMPORARY_AI_SYSTEMS.md) for the canonical comparison.
```

## Validation

From the repository root, validate the JSON file with:

```bash
python -m json.tool docs/comparisons/stegverse_001_ai_systems_comparison.json >/dev/null
python -m json.tool docs/comparisons/comparison_manifest.json >/dev/null
```

Optional content check:

```bash
grep -R "Contemporary AI systems mostly govern" docs/comparisons README.md
grep -R "bounded, receipt-bearing, consequence-capable" docs/comparisons README.md
```

## Commit message

Suggested commit message:

```text
docs: add StegVerse-001 contemporary AI systems comparison
```

## Public-facing caution

Do not summarize this package as a claim that StegVerse-001 is smarter than GPT-4o, Claude, Gemini, Llama, Copilot, LangGraph, AutoGPT, or Waymo.

The supported claim is narrower and stronger:

> StegVerse relocates governance to the consequence-binding transition.

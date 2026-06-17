# AI Safety to Transition Admissibility

**Status:** Repo-local positioning cross-reference  
**Generated:** 2026-06-17  
**Canonical public copy:** `StegVerse-Labs/Site/docs/public-positioning/ai-safety-to-transition-admissibility.md`

---

## Purpose

This note records how the public AI-safety positioning artifact relates to `StegVerse-Labs/StegCore`.

StegCore is the commit-time decision layer. It answers whether a proposed action is permitted now, under the current authority, policy, consent, continuity, and evidence conditions.

The canonical public essay lives in the Site repository because Site is the public mirror. This repository-local note exists so StegCore can reference the positioning without becoming the public publication surface.

---

## StegCore Relationship

The public positioning claim is:

> Prior evaluation is not commit-time standing.

For StegCore, that means:

- a prior AI-safety evaluation is not itself permission to execute;
- a previous approval is not enough if evidence, authority, consent, policy, or identity has drifted;
- execution must be admitted at the action boundary;
- denial must be deterministic and explainable through machine-readable reason codes;
- receipt and replay systems must be able to reconstruct why commitment was allowed, denied, or deferred.

---

## Boundary

StegCore does not claim to replace AI safety research, alignment work, interpretability, institutional review, or post-event evidentiary systems.

StegCore contributes the commit-time admissibility decision surface:

```text
intent + verified continuity + policy + authority + consent + evidence posture
→ allow | deny | defer
```

---

## Associated Components

| Component | Role |
|---|---|
| StegCore | Commit-time decision and admissibility posture |
| GLM | Machine-readable boundary declaration |
| EVIDE | Post-event reconstructability |
| Admissibility Receipt | Portable proof envelope and replay anchor |
| Site | Public mirror and publication surface |

---

## Use in Future Work

Future StegCore docs and examples should cite the canonical Site document when explaining why StegVerse distinguishes:

- evaluation from commitment;
- execution from admissibility;
- review from authority;
- reconstruction from gating.

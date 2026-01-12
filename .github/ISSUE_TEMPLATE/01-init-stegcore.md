---
name: "Init: StegCore baseline structure & policies"
about: "StegVerse build step (v1.2)"
---

## Goal
Bootstrap StegCore spine: entities, policies, tools, finance stubs, and CI.

## Tasks
- Ensure folders exist: `entities/registry`, `policies`, `tools`, `finance`, `docs`, `.github/workflows`
- Add AI entity manifests + policies from bundle v1.0
- Ensure `Entity Supervisor CI` passes
- Confirm `python tools/EntitySupervisor.py` generates `out/entity_plan.json`

## Acceptance criteria
- CI green
- `out/entity_plan.json` exists in CI run


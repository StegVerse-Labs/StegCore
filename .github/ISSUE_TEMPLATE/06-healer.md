---
name: "Feat: Healer policy drift checks"
about: "StegVerse build step (v1.2)"
---

## Goal
Monitor cross-repo drift vs StegCore policies and open issues on mismatch.

## Tasks
- In StegVerse-Healer, add checker job
- Compare risk tags + vault tiers across repos
- Emit labeled issues on mismatch

## Acceptance criteria
- Simulated mismatch creates an issue


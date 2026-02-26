# Constitutional Changelog — StegCore

This file records **constitutional amendments** to StegCore.

StegCore is the **root evaluation authority** for StegVerse governance decisions.
Changes to StegCore are treated as **constitutional**, not feature updates.

## Amendment Rules

A change is "constitutional" if it modifies any of:
- Authority source/scope/renewal/expiry/revocation
- Trust continuity assumptions/signals/break handling
- Boundary conditions or policy shape semantics
- Degradation behavior (refusal/defer semantics)
- Human accountability or escalation rules
- Determinism / replay protections / binding fields in decisions

All constitutional changes MUST:
- Be made via Pull Request (no direct pushes to main)
- Pass BCAT Gate
- Receive human review/approval
- Update this changelog
- Update `constitution.lock` (generated artifact)

## Non-retroactivity

Issued decisions are immutable. New information produces **new decisions**.
Policy changes do not rewrite past legitimacy.

---

## v1.0 — Constitution Established (stegcore-v1.0-constitution)

- BCAT Gate: GRANTED
- Governance scope declared and frozen under amendment rules
- Decision model hardened (binding + expiry + revocation + determinism)
- Policy shapes frozen as constitutional primitives
- Anti-drift invariants published and enforced via CI checks

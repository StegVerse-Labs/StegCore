# StegVerse-001 / StegVerse-002 Validator

`tools/evaluate_admissibility.py` deterministically evaluates the declared baseline vectors. ALLOW requires continuous evidence, a canonical record, valid authority/policy/identity, and current evidence. Declared continuity gaps, stale evidence, policy drift, invalid identity, binding reviewer refusal without valid override, or noncanonical records deny.

This validator is evidence/admissibility logic only and does not execute consequences.

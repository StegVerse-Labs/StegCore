# StegCore Enforcement Hooks (Drop-in)

Drop-in templates to enforce:
- valid AI entity class assignments
- prohibited transitions (Class I -> Class III)
- required approvals/safeguards for promotions to Class III
- entity acknowledgement requirement

Files:
- `validate_ai_registry.py` — validates registry entries and class transitions
- `workflow_ai_registry_validate.yml` — CI gate on PRs touching registry/ethics

Missing inputs fail closed: if `registry/ai_entity_schema.json` or
`ethics/ai_classes.yaml` is absent, the validator prints one JSON line with
`"disposition": "FAIL_CLOSED"` and the failed predicate
(`AI_REGISTRY_SCHEMA_PRESENT` or `AI_CLASSES_PRESENT`) and exits 2. A repo
that cannot provide these files must declare an exemption rather than copy
the hook without them.

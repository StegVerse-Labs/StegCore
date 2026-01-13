# StegCore Enforcement Hooks (Drop-in)

Drop-in templates to enforce:
- valid AI entity class assignments
- prohibited transitions (Class I -> Class III)
- required approvals/safeguards for promotions to Class III
- entity acknowledgement requirement

Files:
- `validate_ai_registry.py` — validates registry entries and class transitions
- `workflow_ai_registry_validate.yml` — CI gate on PRs touching registry/ethics

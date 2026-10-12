import json, pathlib

def fail(msg):
    print(f"ERROR: {msg}")
    raise SystemExit(2)

def fail_closed(failed_predicate, rel_path):
    # Missing required evidence is a decision failure, never a silent pass.
    print(json.dumps({
        "disposition": "FAIL_CLOSED",
        "failed_predicate": failed_predicate,
        "required_evidence_or_repair": f"add {rel_path} or declare an exemption",
        "authority_effect": "NONE",
    }, sort_keys=True))
    raise SystemExit(2)

def main():
    # Expected layout when copied into a repo:
    # ethics/ai_classes.yaml
    # registry/ai_entity_schema.json
    # registry/entities/*.json
    root = pathlib.Path(".").resolve()

    schema_path = root / "registry" / "ai_entity_schema.json"
    classes_path = root / "ethics" / "ai_classes.yaml"
    entities_dir = root / "registry" / "entities"

    if not schema_path.exists():
        fail_closed("AI_REGISTRY_SCHEMA_PRESENT", "registry/ai_entity_schema.json")
    if not classes_path.exists():
        fail_closed("AI_CLASSES_PRESENT", "ethics/ai_classes.yaml")

    # Imported after the presence checks so a missing input fails closed
    # even where the validation dependencies are not installed.
    import yaml
    from jsonschema import Draft202012Validator

    schema = json.loads(schema_path.read_text())
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)

    prohibited = {(t["from"], t["to"]) for t in yaml.safe_load(classes_path.read_text())["transitions"]["prohibited"]}

    # An empty population is not evidence: a missing or empty entities directory
    # validates nothing, so it fails closed rather than reporting OK.
    entity_files = sorted(entities_dir.glob("*.json")) if entities_dir.is_dir() else []
    if not entity_files:
        fail_closed("AI_REGISTRY_ENTITIES_PRESENT", "registry/entities/*.json")

    for p in entity_files:
        data = json.loads(p.read_text())
        errs = sorted(validator.iter_errors(data), key=lambda e: e.path)
        if errs:
            fail(f"{p.name}: schema validation failed: " + "; ".join([e.message for e in errs]))

        for t in data.get("class_history", []):
            if (t["from"], t["to"]) in prohibited:
                fail(f"{p.name}: prohibited transition {t['from']} -> {t['to']}")

        if not data.get("acknowledgements"):
            fail(f"{p.name}: missing acknowledgements")

    print("AI registry validation OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

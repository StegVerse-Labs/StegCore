import json, pathlib
import yaml
from jsonschema import Draft202012Validator

def fail(msg):
    print(f"ERROR: {msg}")
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

    if not schema_path.exists() or not classes_path.exists():
        print("Missing ethics/registry files; skipping.")
        return 0

    schema = json.loads(schema_path.read_text())
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)

    prohibited = {(t["from"], t["to"]) for t in yaml.safe_load(classes_path.read_text())["transitions"]["prohibited"]}

    if not entities_dir.exists():
        print("No registry/entities directory; skipping.")
        return 0

    for p in entities_dir.glob("*.json"):
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

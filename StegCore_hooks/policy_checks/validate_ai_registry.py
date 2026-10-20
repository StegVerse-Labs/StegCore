import hashlib, importlib.util, json, pathlib

# Vendored StegVerse-SDK structural validator (contract 1.6, stdlib only), loaded by path.
VALIDATOR_PATH = (pathlib.Path(__file__).resolve().parents[2]
                  / "src" / "stegcore" / "_vendor" / "structural_validator.py")


class SchemaError(ValueError):
    """A schema the vendored validator refuses (invalid or outside its contract)."""


def load_structural_validator():
    spec = importlib.util.spec_from_file_location("_stegcore_vendored_structural_validator", VALIDATOR_PATH)
    if spec is None or spec.loader is None or not VALIDATOR_PATH.is_file():
        raise ImportError(f"vendored structural validator not found at {VALIDATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

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
    try:
        import yaml
        structural = load_structural_validator()
    except (ImportError, OSError) as exc:
        fail_closed("AI_REGISTRY_VALIDATOR_DEPENDENCIES_PRESENT", type(exc).__name__)

    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        # Unsupported keywords/formats are refused at admission: fail closed, never ignored.
        schema_digest = hashlib.sha256(structural.canonical_bytes(schema)).hexdigest()
        admitted = structural.check_schema(schema, schema_digest)
        if not admitted["valid"]:
            raise SchemaError([f"{e['path'] or '/'}:{e['code']}" for e in admitted["errors"]])
        classes = yaml.safe_load(classes_path.read_text(encoding="utf-8"))
        transitions = classes["transitions"]["prohibited"]
        if not isinstance(transitions, list):
            raise ValueError("prohibited transitions must be an array")
        prohibited = {(t["from"], t["to"]) for t in transitions}
    except (OSError, ValueError, TypeError, KeyError, SchemaError) as exc:
        fail_closed("AI_REGISTRY_POLICY_INPUTS_VALID", f"valid schema/classes ({type(exc).__name__})")

    # An empty population is not evidence: a missing or empty entities directory
    # validates nothing, so it fails closed rather than reporting OK.
    entity_files = sorted(entities_dir.glob("*.json")) if entities_dir.is_dir() else []
    if not entity_files:
        fail_closed("AI_REGISTRY_ENTITIES_PRESENT", "registry/entities/*.json")

    for p in entity_files:
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            errs = sorted(f"{e['path'] or '/'}:{e['code']}"
                          for e in structural.validate(data, schema, schema_digest)["errors"])
            if errs:
                fail_closed("AI_REGISTRY_ENTITY_SCHEMA_VALID", f"{p.name} ({errs[0]})")
            if not isinstance(data, dict):
                raise ValueError("entity must be an object")
            history = data.get("class_history", [])
            if not isinstance(history, list):
                raise ValueError("class_history must be an array")
            for transition in history:
                if not isinstance(transition, dict):
                    raise ValueError("class_history entries must be objects")
                origin, destination = transition["from"], transition["to"]
                if (origin, destination) in prohibited:
                    fail_closed("AI_REGISTRY_PROHIBITED_TRANSITION_ABSENT", p.name)
            if not data.get("acknowledgements"):
                fail_closed("AI_REGISTRY_ACKNOWLEDGEMENTS_PRESENT", p.name)
        except (OSError, ValueError, TypeError, KeyError, RecursionError) as exc:
            fail_closed("AI_REGISTRY_ENTITY_INPUT_VALID", f"{p.name} ({type(exc).__name__})")

    print("AI registry validation OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

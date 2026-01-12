#!/usr/bin/env python3
import yaml, json, datetime, pathlib

def main():
    base = pathlib.Path("entities/registry")
    entities = []
    for p in sorted(base.glob("*.yaml")):
        with open(p, "r", encoding="utf-8") as f:
            entities.append(yaml.safe_load(f))
    out = {"generated": datetime.datetime.utcnow().isoformat()+"Z", "entities": entities}
    pathlib.Path("out").mkdir(exist_ok=True)
    with open("out/entity_plan.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print("Generated entity plan for", len(entities), "entities")

if __name__ == "__main__":
    main()

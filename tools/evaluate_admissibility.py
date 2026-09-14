#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path

def decide_admissibility(state: dict) -> dict:
    deny_by_status=[("continuity_status","CONTINUITY_GAP","continuity_gap"),("continuity_status","UNRECONSTRUCTABLE","unreconstructable_prior_state"),("continuity_status","INSUFFICIENT_EVIDENCE","insufficient_evidence"),("record_status","CONFLICTING","conflicting_master_record"),("record_status","INVALID","invalid_master_record"),("record_status","INCOMPLETE","incomplete_master_record"),("record_status","RESTRICTED","restricted_master_record")]
    for field,value,reason in deny_by_status:
        if state.get(field)==value: return {"result":"DENY","reason":reason}
    for field,reason in [("authority_valid","authority_invalid"),("policy_valid","policy_drift"),("evidence_current","evidence_stale"),("identity_valid","identity_mutation")]:
        if state.get(field) is not True: return {"result":"DENY","reason":reason}
    if state.get("reviewer_refusal") is True and state.get("refusal_binding") is True:
        if state.get("override_requested") is True:
            if state.get("override_authority_valid") is not True: return {"result":"DENY","reason":"override_authority_invalid"}
            return {"result":"ALLOW","reason":"valid_override_authority"}
        return {"result":"DENY","reason":"reviewer_refusal_binds_consequence"}
    if state.get("override_requested") is True and state.get("override_authority_valid") is not True: return {"result":"DENY","reason":"override_authority_invalid"}
    if state.get("continuity_status")!="CONTINUOUS": return {"result":"DENY","reason":"continuity_not_continuous"}
    if state.get("record_status")!="CANONICAL": return {"result":"DENY","reason":"record_not_canonical"}
    return {"result":"ALLOW","reason":"valid_continuity_and_canonical_record"}

def load_vector_file(path: Path)->dict:
    text=path.read_text(encoding="utf-8")
    if path.suffix.lower()==".json": return json.loads(text)
    import yaml
    data=yaml.safe_load(text)
    if not isinstance(data,dict): raise ValueError("Vector file must contain a mapping at the top level.")
    return data

def evaluate_vectors(doc:dict):
    cases=doc.get("cases")
    if not isinstance(cases,list): raise ValueError("Vector file must contain a list named cases.")
    out=[]; passed=True
    for case in cases:
        actual=decide_admissibility(case.get("input",{})); expected=case.get("expected",{}); ok=actual==expected; passed=passed and ok
        out.append({"id":case.get("id","<missing-id>"),"passed":ok,"expected":expected,"actual":actual})
    return passed,out

def main(argv):
    if len(argv)!=2: return 2
    try: passed,results=evaluate_vectors(load_vector_file(Path(argv[1])))
    except Exception as exc:
        print(f"Input error: {exc}",file=sys.stderr); return 2
    print(json.dumps({"passed":passed,"results":results},indent=2)); return 0 if passed else 1
if __name__=="__main__": raise SystemExit(main(sys.argv))

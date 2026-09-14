from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parents[1]; EVALUATOR=ROOT/'tools'/'evaluate_admissibility.py'
def load_evaluator():
    spec=importlib.util.spec_from_file_location('evaluate_admissibility',EVALUATOR); module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module
def test_allow_valid_internal_entity_manifest():
    e=load_evaluator(); assert e.decide_admissibility({'continuity_status':'CONTINUOUS','record_status':'CANONICAL','authority_valid':True,'policy_valid':True,'evidence_current':True,'identity_valid':True,'reviewer_refusal':False,'override_requested':False})=={'result':'ALLOW','reason':'valid_continuity_and_canonical_record'}
def test_deny_on_policy_drift():
    e=load_evaluator(); assert e.decide_admissibility({'continuity_status':'CONTINUOUS','record_status':'CANONICAL','authority_valid':True,'policy_valid':False,'evidence_current':True,'identity_valid':True})=={'result':'DENY','reason':'policy_drift'}
def test_deny_on_stale_evidence():
    e=load_evaluator(); assert e.decide_admissibility({'continuity_status':'CONTINUOUS','record_status':'CANONICAL','authority_valid':True,'policy_valid':True,'evidence_current':False,'identity_valid':True})=={'result':'DENY','reason':'evidence_stale'}
def test_deny_when_reviewer_refusal_binds():
    e=load_evaluator(); assert e.decide_admissibility({'continuity_status':'CONTINUOUS','record_status':'CANONICAL','authority_valid':True,'policy_valid':True,'evidence_current':True,'identity_valid':True,'reviewer_refusal':True,'refusal_binding':True,'override_requested':False})=={'result':'DENY','reason':'reviewer_refusal_binds_consequence'}
def test_deny_invalid_override():
    e=load_evaluator(); assert e.decide_admissibility({'continuity_status':'CONTINUOUS','record_status':'CANONICAL','authority_valid':True,'policy_valid':True,'evidence_current':True,'identity_valid':True,'reviewer_refusal':True,'refusal_binding':True,'override_requested':True,'override_authority_valid':False})=={'result':'DENY','reason':'override_authority_invalid'}

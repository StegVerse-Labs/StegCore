import hashlib,json
from stegcore.render_successor_spec import evaluate_render_successor_spec

def sha(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def base():
    s={'source_service_id':'srv-1','name':'api','source_type':'web','successor_class':'container_service','region':'oregon','plan':'starter','runtime':'python','repo':'org/repo','branch':'main','build_command_present':True,'start_command_present':True,'environment_value_count':None,'environment_values_retained':False}; s['spec_sha256']=sha(s)
    p={'schema':'stegverse.governance.render_successor_spec.v1','provider_id':'render','state':'SUCCESSOR_SPEC_READY','source_report_sha256':'a'*64,'services':[s],'repository_configurations':[],'service_count':1,'configuration_count':0,'blockers':[],'manual_action_required':False,'credentials_required_from_user':False,'environment_values_retained':False,'production_mutation_allowed':False,'execution_authority':False,'traffic_cutover_authority':False,'cancellation_authority':False,'provider_retirement_authority':False,'continuity_receipt_minted':False}; p['spec_sha256']=sha(p); return p

def test_allow_safe_spec(): assert evaluate_render_successor_spec(base())['decision']=='ALLOW_SUCCESSOR_SPEC_EVIDENCE_ONLY'
def test_deny_hidden_authority():
    p=base(); p['execution_authority']=True; p['spec_sha256']=sha({k:v for k,v in p.items() if k!='spec_sha256'}); assert evaluate_render_successor_spec(p)['decision']=='DENY'
def test_deny_tampered_service():
    p=base(); p['services'][0]['name']='changed'; p['spec_sha256']=sha({k:v for k,v in p.items() if k!='spec_sha256'}); assert evaluate_render_successor_spec(p)['decision']=='DENY'
def test_deny_unsupported_ready():
    p=base(); p['services'][0]['successor_class']='unsupported_service'; p['services'][0]['spec_sha256']=sha({k:v for k,v in p['services'][0].items() if k!='spec_sha256'}); p['spec_sha256']=sha({k:v for k,v in p.items() if k!='spec_sha256'}); assert evaluate_render_successor_spec(p)['decision']=='DENY'

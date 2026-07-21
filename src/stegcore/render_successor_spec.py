from __future__ import annotations
import hashlib, json
SCHEMA='stegverse.governance.render_successor_spec.v1'
FORBIDDEN=('manual_action_required','credentials_required_from_user','environment_values_retained','production_mutation_allowed','execution_authority','traffic_cutover_authority','cancellation_authority','provider_retirement_authority','continuity_receipt_minted')

def _canon(v): return json.dumps(v,sort_keys=True,separators=(',',':')).encode()
def _sha(v): return hashlib.sha256(_canon(v)).hexdigest()
def _hex(v): return isinstance(v,str) and len(v)==64 and all(c in '0123456789abcdef' for c in v)

def evaluate_render_successor_spec(payload:dict)->dict:
    reasons=[]
    if payload.get('schema')!=SCHEMA: reasons.append('schema_mismatch')
    if payload.get('provider_id')!='render': reasons.append('provider_mismatch')
    for k in FORBIDDEN:
        if payload.get(k) is not False: reasons.append(f'forbidden_or_missing:{k}')
    if not _hex(payload.get('spec_sha256')): reasons.append('invalid_spec_hash')
    else:
        x=dict(payload); h=x.pop('spec_sha256',None)
        if _sha(x)!=h: reasons.append('spec_hash_mismatch')
    services=payload.get('services')
    if not isinstance(services,list): reasons.append('services_not_list'); services=[]
    for i,s in enumerate(services):
        if s.get('environment_values_retained') is not False: reasons.append(f'service_{i}_environment_retained')
        if s.get('successor_class')=='unsupported_service' and payload.get('state')=='SUCCESSOR_SPEC_READY': reasons.append(f'service_{i}_unsupported_but_ready')
        if not _hex(s.get('spec_sha256')): reasons.append(f'service_{i}_invalid_hash')
        else:
            x=dict(s); h=x.pop('spec_sha256',None)
            if _sha(x)!=h: reasons.append(f'service_{i}_hash_mismatch')
    ready=payload.get('state')=='SUCCESSOR_SPEC_READY' and bool(services) and not reasons
    return {'schema':'stegverse.stegcore.render_successor_admissibility.v1','decision':'ALLOW_SUCCESSOR_SPEC_EVIDENCE_ONLY' if ready else 'DENY','provider_id':'render','source_spec_sha256':payload.get('spec_sha256'),'service_count':len(services),'reasons':sorted(set(reasons+([] if ready else payload.get('blockers',[])))),'evidence_only':True,'successor_health_verified':False,'parallel_operation_verified':False,'manual_action_required':False,'production_mutation_allowed':False,'execution_authority':False,'traffic_cutover_authority':False,'cancellation_authority':False,'provider_retirement_authority':False,'continuity_receipt_minted':False}

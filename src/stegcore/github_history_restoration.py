from __future__ import annotations
import hashlib,json
from typing import Any

FORBIDDEN=('source_retained','bundle_retained','successor_retained','manual_action_required','production_mutation_allowed','execution_authority','traffic_cutover_authority','cancellation_authority','provider_retirement_authority','continuity_receipt_minted')

def _hash(v: object)->str:
    return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def evaluate_github_history_restoration(report: dict[str,Any])->dict[str,Any]:
    blockers=[]
    for field in FORBIDDEN:
        if report.get(field) is not False: blockers.append(f'forbidden_or_missing:{field}')
    records=report.get('records')
    if not isinstance(records,list) or not records: blockers.append('records_missing')
    else:
        for rec in records:
            if not isinstance(rec,dict): blockers.append('invalid_record'); continue
            if rec.get('state')=='PASS_ISOLATED_COMPLETE_HISTORY_RESTORATION':
                for field in FORBIDDEN:
                    if rec.get(field) is not False: blockers.append(f"{rec.get('repository')}:{field}")
                required=('source_ref_hash','restored_ref_hash','bundle_sha256','record_hash')
                for field in required:
                    if not rec.get(field): blockers.append(f"{rec.get('repository')}:missing_{field}")
                if rec.get('source_ref_hash')!=rec.get('restored_ref_hash'): blockers.append(f"{rec.get('repository')}:ref_hash_mismatch")
                if rec.get('source_commit_count')!=rec.get('restored_commit_count'): blockers.append(f"{rec.get('repository')}:commit_count_mismatch")
                if rec.get('source_loose_object_count')!=rec.get('restored_loose_object_count'): blockers.append(f"{rec.get('repository')}:object_count_mismatch")
    decision='ALLOW_ISOLATED_RESTORATION_EVIDENCE_ONLY' if not blockers and report.get('passed_count',0)>0 else 'DENY'
    out={'decision':decision,'blockers':sorted(set(blockers)),'source_report_hash':report.get('report_hash'),'production_mutation_allowed':False,'execution_authority':False,'traffic_cutover_authority':False,'cancellation_authority':False,'provider_retirement_authority':False,'continuity_receipt_minted':False}
    out['evaluation_hash']=_hash(out)
    return out

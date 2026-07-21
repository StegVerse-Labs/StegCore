from stegcore.github_history_restoration import evaluate_github_history_restoration


def good_report():
    record={'repository':'StegVerse-Labs/Governance','state':'PASS_ISOLATED_COMPLETE_HISTORY_RESTORATION','source_ref_hash':'a','restored_ref_hash':'a','source_commit_count':3,'restored_commit_count':3,'source_loose_object_count':2,'restored_loose_object_count':2,'bundle_sha256':'b','record_hash':'c','source_retained':False,'bundle_retained':False,'successor_retained':False,'manual_action_required':False,'production_mutation_allowed':False,'execution_authority':False,'traffic_cutover_authority':False,'cancellation_authority':False,'provider_retirement_authority':False,'continuity_receipt_minted':False}
    return {'report_hash':'r','passed_count':1,'records':[record],'source_retained':False,'bundle_retained':False,'successor_retained':False,'manual_action_required':False,'production_mutation_allowed':False,'execution_authority':False,'traffic_cutover_authority':False,'cancellation_authority':False,'provider_retirement_authority':False,'continuity_receipt_minted':False}


def test_allows_isolated_evidence_only():
    assert evaluate_github_history_restoration(good_report())['decision']=='ALLOW_ISOLATED_RESTORATION_EVIDENCE_ONLY'


def test_denies_ref_mismatch():
    d=good_report(); d['records'][0]['restored_ref_hash']='x'
    assert evaluate_github_history_restoration(d)['decision']=='DENY'


def test_denies_hidden_authority():
    d=good_report(); d['records'][0]['execution_authority']=True
    assert evaluate_github_history_restoration(d)['decision']=='DENY'


def test_denies_missing_records():
    d=good_report(); d['records']=[]
    assert evaluate_github_history_restoration(d)['decision']=='DENY'

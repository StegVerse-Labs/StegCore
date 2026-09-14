from pathlib import Path
import importlib.util,json
ROOT=Path(__file__).resolve().parents[1]; UPDATER=ROOT/'tools'/'update_activation_status.py'
def load_updater():
    spec=importlib.util.spec_from_file_location('update_activation_status',UPDATER); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
def test_check_required_paths_reports_missing(tmp_path):
    u=load_updater(); a=tmp_path/'a'; a.write_text('x'); r=u.check_required_paths({'required_paths':[str(a),str(tmp_path/'missing')]}); assert r['passed'] is False
def test_check_required_paths_passes_when_all_exist(tmp_path):
    u=load_updater(); a=tmp_path/'a'; a.write_text('x'); assert u.check_required_paths({'required_paths':[str(a)]})['passed'] is True
def test_build_activation_report_denies_when_command_fails():
    u=load_updater(); r=u.build_activation_report({'activation_target':'x'},'activated',{'passed':True},{'passed':False}); assert r['decision']=='DENY_STATUS_UPDATE'
def test_apply_status_update_sets_current_result():
    u=load_updater(); d=u.apply_status_update({'status':'activation_candidate'},'activated',{'decision':'ALLOW_STATUS_UPDATE','reason':'activation_gates_passed','evaluated_at':'2026-06-17T00:00:00+00:00'}); assert d['status']=='activated' and d['current_registry_result']['status']=='ACTIVATED'
def test_json_roundtrip_for_updated_registry(tmp_path):
    u=load_updater(); p=tmp_path/'r.json'; u.write_json(p,u.apply_status_update({'status':'activation_candidate'},'activated',{'decision':'ALLOW_STATUS_UPDATE','reason':'activation_gates_passed','evaluated_at':'2026-06-17T00:00:00+00:00'})); assert json.loads(p.read_text())['status']=='activated'

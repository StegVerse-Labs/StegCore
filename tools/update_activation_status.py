#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,subprocess
from datetime import datetime,timezone
from pathlib import Path
DEFAULT_JSON_REGISTRY=Path('registry/stegverse-001-002.activation.json'); DEFAULT_YAML_REGISTRY=Path('registry/stegverse-001-002.activation.yml'); ALLOWED_TARGET_STATUSES={'activation_candidate','activated'}
def utc_now(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def load_json(path):
    if not path.exists(): raise FileNotFoundError(f'registry not found: {path}')
    data=json.loads(path.read_text());
    if not isinstance(data,dict): raise ValueError('registry JSON must contain an object at the top level')
    return data
def write_json(path,data): path.write_text(json.dumps(data,indent=2)+'\n')
def check_required_paths(registry):
    required=registry.get('required_paths',[])
    if not isinstance(required,list): return {'passed':False,'reason':'required_paths_not_list','missing_paths':[],'checked_paths':0}
    missing=[p for p in required if not Path(str(p)).exists()]; return {'passed':not missing,'reason':'all_required_paths_present' if not missing else 'required_paths_missing','missing_paths':missing,'checked_paths':len(required)}
def run_required_commands(registry):
    required=registry.get('required_commands',[])
    if not isinstance(required,list): return {'passed':False,'reason':'required_commands_not_list','results':[]}
    results=[]; ok=True
    for command in required:
        c=subprocess.run(str(command),shell=True,text=True,capture_output=True); passed=c.returncode==0; ok=ok and passed; results.append({'command':str(command),'passed':passed,'returncode':c.returncode,'stdout':c.stdout[-4000:],'stderr':c.stderr[-4000:]})
    return {'passed':ok,'reason':'all_required_commands_passed' if ok else 'required_command_failed','results':results}
def build_activation_report(registry,target_status,path_check,command_check):
    passed=path_check.get('passed') is True and command_check.get('passed') is True
    return {'passed':passed,'target_status':target_status,'activation_target':registry.get('activation_target'),'path_check':path_check,'command_check':command_check,'decision':'ALLOW_STATUS_UPDATE' if passed else 'DENY_STATUS_UPDATE','reason':'activation_gates_passed' if passed else 'activation_gates_failed','evaluated_at':utc_now()}
def apply_status_update(registry,target_status,report):
    d=dict(registry); d['status']=target_status; d['last_activation_status_update']={'status':target_status,'decision':report['decision'],'reason':report['reason'],'updated_at':report['evaluated_at']}; d['current_registry_result']={'status':target_status.upper(),'reason':'activation_gates_passed_and_status_updated','updated_at':report['evaluated_at']}; return d
def maybe_update_yaml_registry(path,target_status,report):
    if not path.exists(): return {'attempted':False,'updated':False,'reason':'yaml_registry_not_found','path':str(path)}
    try: import yaml
    except ImportError: return {'attempted':True,'updated':False,'reason':'pyyaml_not_available','path':str(path)}
    d=yaml.safe_load(path.read_text()); d['status']=target_status; d['last_activation_status_update']={'status':target_status,'decision':report['decision'],'reason':report['reason'],'updated_at':report['evaluated_at']}; d['current_registry_result']={'status':target_status.upper(),'reason':'activation_gates_passed_and_status_updated','updated_at':report['evaluated_at']}; path.write_text(yaml.safe_dump(d,sort_keys=False)); return {'attempted':True,'updated':True,'reason':'yaml_registry_updated','path':str(path)}
def main(argv):
    p=argparse.ArgumentParser(); p.add_argument('--registry',default=str(DEFAULT_JSON_REGISTRY)); p.add_argument('--yaml-registry',default=str(DEFAULT_YAML_REGISTRY)); p.add_argument('--target-status',default='activated',choices=sorted(ALLOWED_TARGET_STATUSES)); p.add_argument('--dry-run',action='store_true'); p.add_argument('--skip-commands',action='store_true'); a=p.parse_args(argv)
    try:
        r=load_json(Path(a.registry)); pc=check_required_paths(r); cc={'passed':True,'reason':'commands_skipped','results':[]} if a.skip_commands else run_required_commands(r); report=build_activation_report(r,a.target_status,pc,cc)
        if not report['passed']: print(json.dumps(report,indent=2)); return 1
        if a.dry_run: report.update({'dry_run':True,'registry_updated':False}); print(json.dumps(report,indent=2)); return 0
        write_json(Path(a.registry),apply_status_update(r,a.target_status,report)); yr=maybe_update_yaml_registry(Path(a.yaml_registry),a.target_status,report); report.update({'dry_run':False,'registry_updated':True,'json_registry':a.registry,'yaml_registry':yr}); print(json.dumps(report,indent=2)); return 0
    except Exception as exc: print(json.dumps({'passed':False,'reason':'updater_error','error':str(exc)},indent=2)); return 2
if __name__=='__main__': import sys; raise SystemExit(main(sys.argv[1:]))

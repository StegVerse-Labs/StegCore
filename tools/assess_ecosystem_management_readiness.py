#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    'docs/STEGVERSE_ECOSYSTEM_MANAGEMENT_MIRROR_HANDOFF.md',
    'ecosystem_management/task_registry.yml',
    'ecosystem_management/ae_task_conformance.v1.json',
    'management/admissible-existence-capability-registry.json',
    'tools/verify_ae_handoff_task_conformance.py',
    'tools/assess_ecosystem_management_readiness.py',
    '.github/workflows/verify-task-registry.yml',
]
CAPABILITIES = [
    'mirror_handoff_present',
    'machine_readable_task_registry_present',
    'completion_criteria_declared',
    'next_integration_candidate_declared',
    'verification_command_declared',
    'report_artifact_declared',
    'parallel_session_non_overlap_declared',
    'archive_readiness_declared',
    'admissible_existence_capability_binding_declared',
    'ae_conformance_verification_declared',
]
AE_REPORT = ROOT / 'brain_reports/ae_handoff_task_conformance_report.json'
def sha256_json(data: dict) -> str:
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
def main() -> int:
    checks = [{'path': p, 'exists': (ROOT / p).exists()} for p in REQUIRED]
    registry = ROOT / 'ecosystem_management/task_registry.yml'
    text = registry.read_text(encoding='utf-8') if registry.exists() else ''
    cap_checks = [{'capability': c, 'declared': c in text or c.replace('_','-') in text} for c in CAPABILITIES]
    missing = [c['path'] for c in checks if not c['exists']]
    missing_caps = [c['capability'] for c in cap_checks if not c['declared']]
    ae_report = None
    ae_conformant = False
    if AE_REPORT.exists():
        try:
            ae_report = json.loads(AE_REPORT.read_text(encoding='utf-8'))
            ae_conformant = ae_report.get('valid') is True
        except (OSError, json.JSONDecodeError):
            ae_report = None
    outcome = 'STEGVERSE_ECOSYSTEM_MANAGEMENT_HANDOFF_CAPABLE' if not missing and not missing_caps and ae_conformant else 'STEGVERSE_ECOSYSTEM_MANAGEMENT_HANDOFF_INCOMPLETE'
    report = {
        'receipt_type': 'stegverse_ecosystem_management_readiness_report',
        'timestamp_unix': int(time.time()),
        'outcome': outcome,
        'checks': checks,
        'missing_items': missing,
        'capability_checks': cap_checks,
        'missing_capabilities': missing_caps,
        'ae_conformance_required': True,
        'ae_conformance_valid': ae_conformant,
        'ae_conformance_report': str(AE_REPORT.relative_to(ROOT)),
        'ae_conformance_report_sha256': None if not ae_report else ae_report.get('report_sha256'),
        'current_repo': 'StegVerse-Labs/stegfin-provider-banking',
        'next_integration_candidate': 'StegVerse-Labs/stegfin-provider-acquisition-close',
        'handoff_capable_without_current_thread': outcome.endswith('CAPABLE'),
        'archive_readiness': 'ready only when handoff capable and canonical AE conformance is valid',
        'credential_authority': 'TV/TVC',
        'github_token_runtime_authority': 'NONE',
    }
    report['report_sha256'] = sha256_json(report)
    out = ROOT / 'brain_reports/stegverse_ecosystem_management_readiness_report.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(outcome)
    print(f'report_path={out.relative_to(ROOT)}')
    print(f"report_sha256={report['report_sha256']}")
    print(f"ae_conformance_valid={report['ae_conformance_valid']}")
    print(f"next_integration_candidate={report['next_integration_candidate']}")
    return 0 if outcome.endswith('CAPABLE') else 1
if __name__ == '__main__':
    raise SystemExit(main())

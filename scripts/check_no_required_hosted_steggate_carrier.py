#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = (
    ROOT / '.github/workflows/steggate-heartbeat-worker-reusable.yml',
    ROOT / '.github/workflows/steggate-fallback-public-runtime.yml',
)

FORBIDDEN = (
    'cloud' + 'flared',
    'try' + 'cloudflare.com',
    'nohup ' + 'uvicorn',
    'repository_' + 'dispatch:',
    'contents: ' + 'write',
    'issues: ' + 'write',
    'pull-requests: ' + 'write',
    'gh ' + 'api',
    'gh ' + 'pr create',
    'git ' + 'push',
    'upload-' + 'artifact@',
    'finalize_steggate_live_activation.py',
)

for path in WORKFLOWS:
    if not path.exists():
        raise SystemExit(f'HOSTED_STEGGATE_CARRIER_FAIL: missing {path.relative_to(ROOT)}')
    text = path.read_text(encoding='utf-8')
    for marker in FORBIDDEN:
        if marker in text:
            raise SystemExit(
                f'HOSTED_STEGGATE_CARRIER_FAIL: {path.relative_to(ROOT)} contains {marker}'
            )
    if 'permissions: {}' not in text:
        raise SystemExit(f'HOSTED_STEGGATE_CARRIER_FAIL: {path.relative_to(ROOT)} permissions not empty')

heartbeat = WORKFLOWS[0].read_text(encoding='utf-8')
fallback = WORKFLOWS[1].read_text(encoding='utf-8')
if 'RESIDENT_RUNTIME_REQUIRED' not in heartbeat:
    raise SystemExit('HOSTED_STEGGATE_CARRIER_FAIL: reusable heartbeat path does not fail toward resident runtime')
if 'STEGGATE_CANONICAL_RUNTIME=RESIDENT_STEGVERSE' not in fallback:
    raise SystemExit('HOSTED_STEGGATE_CARRIER_FAIL: fallback path does not declare resident canonical runtime')
if 'STEGGATE_FALLBACK_SELECTION=EXPLICIT_OPT_IN_ONLY' not in fallback:
    raise SystemExit('HOSTED_STEGGATE_CARRIER_FAIL: fallback path is not explicit-opt-in only')

print('HOSTED_STEGGATE_CARRIER_RETIREMENT=PASS')
print('CANONICAL_RUNTIME=RESIDENT_STEGVERSE')
print('THIRD_PARTY_CARRIER_REQUIRED=false')
print('GITHUB_RUNTIME_AUTHORITY=NONE')

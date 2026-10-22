#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = (
    ROOT / '.github/workflows/steggate-heartbeat-worker-reusable.yml',
    ROOT / '.github/workflows/steggate-fallback-public-runtime.yml',
)

# Match executable YAML/shell behavior rather than words that may legitimately
# appear inside regression assertions or explanatory comments.
FORBIDDEN_EXECUTABLE_PATTERNS = (
    'repository_dispatch:',
    'permissions:\n  contents: write',
    'permissions:\n  issues: write',
    'permissions:\n  pull-requests: write',
    'uses: actions/upload-artifact@',
    'uses: actions/setup-python@',
    'nohup "$RUNNER_TEMP/cloudflared"',
    'https://github.com/cloudflare/cloudflared/releases/',
    '.trycloudflare.com',
    'nohup uvicorn ',
    'gh api "repos/',
    'gh pr create ',
    'git push ',
    'run: python scripts/finalize_steggate_live_activation.py',
    'Supervise and self-heal runtime through heartbeat lease window',
)

for path in WORKFLOWS:
    if not path.exists():
        raise SystemExit(f'HOSTED_STEGGATE_CARRIER_FAIL: missing {path.relative_to(ROOT)}')
    text = path.read_text(encoding='utf-8')
    for marker in FORBIDDEN_EXECUTABLE_PATTERNS:
        if marker in text:
            raise SystemExit(
                f'HOSTED_STEGGATE_CARRIER_FAIL: {path.relative_to(ROOT)} contains executable marker {marker}'
            )

heartbeat = WORKFLOWS[0].read_text(encoding='utf-8')
fallback = WORKFLOWS[1].read_text(encoding='utf-8')
if 'permissions: {}' not in heartbeat:
    raise SystemExit('HOSTED_STEGGATE_CARRIER_FAIL: heartbeat compatibility surface permissions not empty')
if 'permissions: {}' not in fallback:
    raise SystemExit('HOSTED_STEGGATE_CARRIER_FAIL: fallback declaration permissions not empty')
if 'RESIDENT_RUNTIME_REQUIRED' not in heartbeat:
    raise SystemExit('HOSTED_STEGGATE_CARRIER_FAIL: reusable heartbeat path does not fail toward resident runtime')
if 'STEGGATE_CANONICAL_RUNTIME=RESIDENT_STEGVERSE' not in fallback:
    raise SystemExit('HOSTED_STEGGATE_CARRIER_FAIL: fallback path does not declare resident canonical runtime')
if 'STEGGATE_FALLBACK_SELECTION=DISABLED' not in fallback:
    raise SystemExit('HOSTED_STEGGATE_CARRIER_FAIL: third-party fallback is not disabled')

print('HOSTED_STEGGATE_CARRIER_RETIREMENT=PASS')
print('CANONICAL_RUNTIME=RESIDENT_STEGVERSE')
print('THIRD_PARTY_CARRIER_REQUIRED=false')
print('GITHUB_RUNTIME_AUTHORITY=NONE')

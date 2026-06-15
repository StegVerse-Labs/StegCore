from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]

class TestRepoReadiness(unittest.TestCase):
    def test_readme_exists(self):
        self.assertTrue((ROOT / 'README.md').exists() or (ROOT / 'README.MD').exists())

    def test_workflow_extensions_are_valid(self):
        workflows = ROOT / '.github' / 'workflows'
        if workflows.exists():
            bad = sorted(p.name for p in workflows.glob('*.ym'))
            self.assertEqual(bad, [])

    def test_json_files_parse(self):
        for path in ROOT.rglob('*.json'):
            if any(part in {'.git', 'node_modules', '.venv', 'venv'} for part in path.parts):
                continue
            with self.subTest(path=str(path.relative_to(ROOT))):
                json.loads(path.read_text(encoding='utf-8'))

if __name__ == '__main__':
    unittest.main()

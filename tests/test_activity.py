"""Behavior checks for public profile activity; no network or credentials."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from xml.etree import ElementTree as ET

SCRIPT = Path(__file__).parents[1] / 'scripts' / 'update_activity.py'


class ActivityTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(SCRIPT.exists(), 'The activity generator has not been implemented')
        spec = importlib.util.spec_from_file_location('activity', SCRIPT)
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)

    def test_only_public_original_active_repositories_are_shown(self):
        base = dict(private=False, fork=False, archived=False, pushed_at='2026-10-20T12:00:00Z')
        records = [dict(base, name='Original & useful'), dict(base, name='fork', fork=True),
                   dict(base, name='private', private=True), dict(base, name='archive', archived=True),
                   dict(base, name='girinataraj'), dict(base, name='newer', pushed_at='2026-10-27T00:00:00Z')]
        self.assertEqual([r['name'] for r in self.module.select_repositories(records)],
                         ['newer', 'Original & useful'])

    def test_card_is_valid_svg_and_escapes_repository_names(self):
        svg = self.module.render_card([dict(name='A & <B>', pushed_at='2026-10-20T12:00:00Z')], '2026-10-28')
        root = ET.fromstring(svg)
        self.assertEqual(root.tag, '{http://www.w3.org/2000/svg}svg')
        self.assertIn('A & <B>', ''.join(root.itertext()))
        self.assertIn('2026-10-20', svg)

    def test_network_failure_preserves_last_good_card(self):
        with tempfile.TemporaryDirectory() as tmp:
            card = Path(tmp) / 'activity.svg'
            card.write_text('last good card', encoding='utf-8')
            def failed_fetch():
                raise OSError('offline')
            with self.assertRaises(OSError):
                self.module.update(card, failed_fetch)
            self.assertEqual(card.read_text(encoding='utf-8'), 'last good card')

    def test_empty_account_has_honest_empty_state(self):
        svg = self.module.render_card([], '2026-10-28')
        ET.fromstring(svg)
        self.assertIn('No public project pushes to show yet', svg)


if __name__ == '__main__':
    unittest.main()

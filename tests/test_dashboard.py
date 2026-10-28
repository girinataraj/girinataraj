"""Profile data rendering and failure-preservation behavior."""
import importlib.util
from datetime import date, timedelta
from pathlib import Path
import tempfile
import unittest
from xml.etree import ElementTree as ET

SCRIPT = Path(__file__).parents[1] / 'scripts' / 'update_activity.py'
spec = importlib.util.spec_from_file_location('activity', SCRIPT)
activity = importlib.util.module_from_spec(spec)
spec.loader.exec_module(activity)


class DashboardTests(unittest.TestCase):
    def test_calendar_window_requires_every_date_in_the_displayed_year(self):
        self.assertTrue(hasattr(activity, 'validate_calendar'), 'Complete-window validation is not implemented')
        days = [((date(2025, 10, 29)+timedelta(days=i)).isoformat(), 0) for i in range(365)]
        activity.validate_calendar(days, '2026-10-28')
        del days[100]
        with self.assertRaises(ValueError):
            activity.validate_calendar(days, '2026-10-28')

    def test_calendar_reads_real_dates_and_intensity_in_date_order(self):
        self.assertTrue(hasattr(activity, 'parse_calendar'), 'Calendar parser is not implemented')
        html = '<table><td data-date="2026-10-27" data-level="3"></td><td data-date="2026-10-26" data-level="0"></td></table>'
        self.assertEqual(activity.parse_calendar(html), [('2026-10-26', 0), ('2026-10-27', 3)])

    def test_missing_or_invalid_calendar_is_rejected(self):
        self.assertTrue(hasattr(activity, 'parse_calendar'), 'Calendar parser is not implemented')
        for html in ['<html>Rate limited</html>', '<td data-date="2026-10-27" data-level="9"></td>']:
            with self.assertRaises(ValueError):
                activity.parse_calendar(html)

    def test_failed_calendar_fetch_keeps_both_previous_visuals(self):
        self.assertTrue(hasattr(activity, 'update_workshop'), 'Dashboard updater is not implemented')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root/'activity.svg').write_text('old activity')
            (root/'contributions.svg').write_text('old calendar')
            def offline():
                raise OSError('unavailable')
            with self.assertRaises(OSError):
                activity.update_workshop(root, lambda: [], offline)
            self.assertEqual((root/'activity.svg').read_text(), 'old activity')
            self.assertEqual((root/'contributions.svg').read_text(), 'old calendar')

    def test_dashboard_counts_original_repositories_and_preserves_xml(self):
        self.assertTrue(hasattr(activity, 'render_dashboard'), 'Dashboard renderer is not implemented')
        records = [dict(name='A & B', fork=False, private=False, archived=False, language='Python'),
                   dict(name='Fork', fork=True, private=False, archived=False, language='Rust')]
        svg = activity.render_dashboard(records, [('2026-10-26', 0), ('2026-10-27', 3)], '2026-10-28')
        text = ''.join(ET.fromstring(svg).itertext())
        self.assertIn('1 original public repository', text)
        self.assertIn('1 active day', text)
        self.assertIn('Python', text)
        self.assertNotIn('Rust', text)


if __name__ == '__main__':
    unittest.main()

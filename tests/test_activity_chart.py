import sys
import unittest
import xml.etree.ElementTree as ElementTree
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from activity_chart import ActivityChart  # noqa: E402
from contributions import DailyContribution, _to_daily_contributions  # noqa: E402

SVG = "{http://www.w3.org/2000/svg}"
START = date(2026, 9, 1)


def given_counts(*counts: int) -> list[DailyContribution]:
    return [DailyContribution(START + timedelta(days=offset), count) for offset, count in enumerate(counts)]


def render(contributions: list[DailyContribution]) -> ElementTree.Element:
    return ElementTree.fromstring(ActivityChart("Ali's Contribution Graph", contributions).to_svg())


def y_axis_labels(svg: ElementTree.Element) -> list[str]:
    return [text.text for text in svg.iter(f"{SVG}text") if text.get("text-anchor") == "end"]


class ActivityChartTest(unittest.TestCase):
    def test_renders_valid_svg_with_escaped_title(self):
        svg = render(given_counts(1, 2, 3))
        self.assertEqual("Ali's Contribution Graph", svg.get("aria-label"))

    def test_plots_one_point_per_day(self):
        svg = render(given_counts(0, 4, 2, 7, 1))
        self.assertEqual(5, len(list(svg.iter(f"{SVG}circle"))))

    def test_y_axis_rounds_up_to_cover_the_busiest_day(self):
        svg = render(given_counts(0, 9))
        self.assertEqual(["0", "3", "6", "9", "12"], y_axis_labels(svg))

    def test_y_axis_still_has_ticks_when_there_are_no_contributions(self):
        svg = render(given_counts(0, 0, 0))
        self.assertEqual(["0", "1", "2", "3", "4"], y_axis_labels(svg))

    def test_x_axis_labels_every_fifth_day(self):
        svg = render(given_counts(*[1] * 11))
        labels = [text.text for text in svg.iter(f"{SVG}text") if text.get("text-anchor") == "middle"][1:]
        self.assertEqual(["Sep 01", "Sep 06", "Sep 11"], labels)

    def test_single_day_does_not_divide_by_zero(self):
        svg = render(given_counts(5))
        self.assertEqual(1, len(list(svg.iter(f"{SVG}circle"))))

    def test_rejects_empty_contributions(self):
        with self.assertRaises(ValueError):
            ActivityChart("title", [])


class ContributionParsingTest(unittest.TestCase):
    def test_flattens_calendar_weeks_into_days(self):
        calendar = {"weeks": [
            {"contributionDays": [{"date": "2026-09-01", "contributionCount": 2}]},
            {"contributionDays": [{"date": "2026-09-02", "contributionCount": 0}]},
        ]}
        self.assertEqual(given_counts(2, 0), _to_daily_contributions(calendar))


if __name__ == "__main__":
    unittest.main()

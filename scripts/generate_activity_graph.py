"""Draws the last month of GitHub contributions as an SVG line chart for the profile README.

Usage: GITHUB_TOKEN=... python scripts/generate_activity_graph.py <login> <display name> <output path>
"""
import os
import sys
from pathlib import Path

from activity_chart import ActivityChart
from contributions import fetch_recent_contributions

DAYS_SHOWN = 31


def main() -> None:
    login, display_name, output_path = sys.argv[1:4]
    contributions = fetch_recent_contributions(login, os.environ["GITHUB_TOKEN"], DAYS_SHOWN)
    chart = ActivityChart(f"{display_name}'s Contribution Graph", contributions)
    Path(output_path).write_text(chart.to_svg(), encoding="utf-8")


if __name__ == "__main__":
    main()

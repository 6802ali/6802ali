import math
from xml.sax.saxutils import escape

from contributions import DailyContribution

WIDTH = 850
HEIGHT = 300
MARGIN_LEFT = 50
MARGIN_RIGHT = 25
MARGIN_TOP = 50
MARGIN_BOTTOM = 40
Y_TICK_COUNT = 4
X_LABEL_EVERY_N_DAYS = 5

STYLE = """
  .background { fill: #ffffff; }
  .title { fill: #0969da; font: 600 16px 'Segoe UI', Ubuntu, sans-serif; }
  .axis-label { fill: #57606a; font: 11px 'Segoe UI', Ubuntu, sans-serif; }
  .grid { stroke: #d0d7de; stroke-dasharray: 3 3; }
  .line { fill: none; stroke: #0969da; stroke-width: 2; stroke-linejoin: round; }
  .area { fill: #0969da; fill-opacity: 0.12; }
  .point { fill: #0969da; }
  @media (prefers-color-scheme: dark) {
    .background { fill: #0d1117; }
    .title { fill: #58a6ff; }
    .axis-label { fill: #8b949e; }
    .grid { stroke: #30363d; }
    .line { stroke: #58a6ff; }
    .area { fill: #58a6ff; }
    .point { fill: #58a6ff; }
  }
"""


class ActivityChart:
    """Line chart of daily contributions, rendered as a standalone SVG that follows the viewer's color scheme."""

    def __init__(self, title: str, contributions: list[DailyContribution]):
        if not contributions:
            raise ValueError("An activity chart needs at least one day of contributions")
        self._title = title
        self._contributions = contributions
        self._y_step = max(1, math.ceil(max(day.count for day in contributions) / Y_TICK_COUNT))

    def to_svg(self) -> str:
        return "\n".join([
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
            f'viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="{escape(self._title)}">',
            f"<style>{STYLE}</style>",
            f'<rect class="background" width="{WIDTH}" height="{HEIGHT}" rx="6"/>',
            f'<text class="title" x="{WIDTH / 2}" y="30" text-anchor="middle">{escape(self._title)}</text>',
            *self._y_axis(),
            *self._x_axis(),
            *self._plot(),
            "</svg>",
        ])

    def _y_axis(self) -> list[str]:
        elements = []
        for tick in range(Y_TICK_COUNT + 1):
            value = tick * self._y_step
            y = self._y_of(value)
            elements.append(f'<line class="grid" x1="{MARGIN_LEFT}" x2="{WIDTH - MARGIN_RIGHT}" y1="{y}" y2="{y}"/>')
            label_x = MARGIN_LEFT - 10
            elements.append(f'<text class="axis-label" x="{label_x}" y="{y + 4}" text-anchor="end">{value}</text>')
        return elements

    def _x_axis(self) -> list[str]:
        label_y = HEIGHT - MARGIN_BOTTOM + 20
        return [
            f'<text class="axis-label" x="{self._x_of(index)}" y="{label_y}" text-anchor="middle">'
            f"{day.day.strftime('%b %d')}</text>"
            for index, day in enumerate(self._contributions)
            if index % X_LABEL_EVERY_N_DAYS == 0
        ]

    def _plot(self) -> list[str]:
        points = [(self._x_of(index), self._y_of(day.count)) for index, day in enumerate(self._contributions)]
        line = " ".join(f"{x},{y}" for x, y in points)
        baseline = self._y_of(0)
        area = f"{points[0][0]},{baseline} {line} {points[-1][0]},{baseline}"
        return [
            f'<polygon class="area" points="{area}"/>',
            f'<polyline class="line" points="{line}"/>',
            *(f'<circle class="point" cx="{x}" cy="{y}" r="3"/>' for x, y in points),
        ]

    def _x_of(self, index: int) -> float:
        plot_width = WIDTH - MARGIN_LEFT - MARGIN_RIGHT
        gaps = max(1, len(self._contributions) - 1)
        return round(MARGIN_LEFT + plot_width * index / gaps, 1)

    def _y_of(self, count: int) -> float:
        plot_height = HEIGHT - MARGIN_TOP - MARGIN_BOTTOM
        y_max = self._y_step * Y_TICK_COUNT
        return round(HEIGHT - MARGIN_BOTTOM - plot_height * count / y_max, 1)

import json
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone

GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"

CONTRIBUTION_CALENDAR_QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""


@dataclass(frozen=True)
class DailyContribution:
    day: date
    count: int


class ContributionFetchError(Exception):
    pass


def fetch_recent_contributions(login: str, token: str, day_count: int) -> list[DailyContribution]:
    today = datetime.now(timezone.utc).date()
    first_day = today - timedelta(days=day_count - 1)
    variables = {
        "login": login,
        "from": datetime.combine(first_day, time.min, timezone.utc).isoformat(),
        "to": datetime.combine(today, time.max, timezone.utc).isoformat(),
    }
    calendar = _query_contribution_calendar(token, variables)
    return _to_daily_contributions(calendar)


def _query_contribution_calendar(token: str, variables: dict) -> dict:
    body = json.dumps({"query": CONTRIBUTION_CALENDAR_QUERY, "variables": variables}).encode()
    request = urllib.request.Request(
        GITHUB_GRAPHQL_URL,
        data=body,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request) as response:
            payload = json.load(response)
    except OSError as error:
        raise ContributionFetchError(f"Could not reach the GitHub GraphQL API: {error}") from error
    if payload.get("errors") or not payload.get("data", {}).get("user"):
        raise ContributionFetchError(f"GitHub returned no contribution data: {payload.get('errors')}")
    return payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]


def _to_daily_contributions(calendar: dict) -> list[DailyContribution]:
    return [
        DailyContribution(date.fromisoformat(day["date"]), day["contributionCount"])
        for week in calendar["weeks"]
        for day in week["contributionDays"]
    ]

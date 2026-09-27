import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


API_URL = "https://api.football-data.org/v4/matches"
TOKEN = os.environ.get("FOOTBALL_DATA_TOKEN")

if not TOKEN:
    raise SystemExit("FOOTBALL_DATA_TOKEN is missing.")

if len(sys.argv) != 2:
    raise SystemExit("Usage: fetch_matches.py OUTPUT_FILE")

OUTPUT_FILE = Path(sys.argv[1])


# Higher number = more important.
COMPETITION_PRIORITY = {
    "WC": 120,   # FIFA World Cup
    "CL": 115,   # UEFA Champions League
    "EL": 100,   # UEFA Europa League
    "PL": 100,   # Premier League
    "PD": 96,    # La Liga
    "SA": 94,    # Serie A
    "BL1": 94,   # Bundesliga
    "FL1": 90,   # Ligue 1
    "PPL": 70,   # Primeira Liga
    "DED": 65,   # Eredivisie
}


STATUS_PRIORITY = {
    "IN_PLAY": 1000,
    "LIVE": 1000,
    "PAUSED": 950,

    "TIMED": 550,
    "SCHEDULED": 550,

    "FINISHED": 250,

    "POSTPONED": 80,
    "SUSPENDED": 60,
    "CANCELLED": 0,
}


STAGE_PRIORITY = {
    "FINAL": 500,
    "SEMI_FINALS": 420,
    "QUARTER_FINALS": 340,
    "LAST_16": 260,
    "ROUND_OF_16": 260,
    "PLAYOFFS": 220,
    "GROUP_STAGE": 120,
    "REGULAR_SEASON": 60,
}


# Extra weight for globally prominent clubs.
# This is only a local ranking preference; it does not create extra API calls.
IMPORTANT_TEAM_NAMES = {
    "Real Madrid CF",
    "FC Barcelona",
    "Manchester City FC",
    "Manchester United FC",
    "Liverpool FC",
    "Arsenal FC",
    "Chelsea FC",
    "Tottenham Hotspur FC",
    "FC Bayern München",
    "Borussia Dortmund",
    "Paris Saint-Germain FC",
    "Juventus FC",
    "FC Internazionale Milano",
    "AC Milan",
    "SSC Napoli",
    "Club Atlético de Madrid",
}


def calculate_priority(match):
    competition = match.get("competition") or {}
    home = match.get("homeTeam") or {}
    away = match.get("awayTeam") or {}

    value = (
        STATUS_PRIORITY.get(match.get("status"), 100)
        + COMPETITION_PRIORITY.get(competition.get("code"), 20)
        + STAGE_PRIORITY.get(match.get("stage"), 0)
    )

    if home.get("name") in IMPORTANT_TEAM_NAMES:
        value += 35

    if away.get("name") in IMPORTANT_TEAM_NAMES:
        value += 35

    return value


def normalize(match):
    competition = match.get("competition") or {}
    home = match.get("homeTeam") or {}
    away = match.get("awayTeam") or {}
    score = match.get("score") or {}

    return {
        "id": match.get("id"),

        "competition": {
            "id": competition.get("id"),
            "code": competition.get("code"),
            "name": competition.get("name"),
            "emblem": competition.get("emblem"),
        },

        "utcDate": match.get("utcDate"),
        "status": match.get("status"),
        "minute": match.get("minute"),
        "injuryTime": match.get("injuryTime"),
        "stage": match.get("stage"),
        "matchday": match.get("matchday"),

        "home": {
            "id": home.get("id"),
            "name": home.get("name"),
            "shortName": home.get("shortName"),
            "tla": home.get("tla"),
            "crest": home.get("crest"),
        },

        "away": {
            "id": away.get("id"),
            "name": away.get("name"),
            "shortName": away.get("shortName"),
            "tla": away.get("tla"),
            "crest": away.get("crest"),
        },

        "score": {
            "winner": score.get("winner"),
            "duration": score.get("duration"),
            "fullTime": score.get("fullTime"),
            "halfTime": score.get("halfTime"),
        },

        "priority": calculate_priority(match),
        "lastUpdated": match.get("lastUpdated"),
    }


request = urllib.request.Request(
    API_URL,
    headers={
        "X-Auth-Token": TOKEN,
        "User-Agent": "KothaFootballCollector/1.0",
        "Accept": "application/json",
    },
)


try:
    with urllib.request.urlopen(request, timeout=30) as response:
        raw = json.loads(response.read().decode("utf-8"))
        remaining = response.headers.get("X-Requests-Available-Minute")

except urllib.error.HTTPError as exc:
    body = exc.read().decode("utf-8", errors="replace")
    raise SystemExit(
        f"football-data.org returned HTTP {exc.code}: {body}"
    ) from exc

except urllib.error.URLError as exc:
    raise SystemExit(
        f"Could not reach football-data.org: {exc}"
    ) from exc


matches = [
    normalize(match)
    for match in raw.get("matches", [])
]


matches.sort(
    key=lambda match: (
        -match["priority"],
        match.get("utcDate") or "",
    )
)


output = {
    "updatedAt": datetime.now(timezone.utc).isoformat(),
    "source": "football-data.org",

    "rateLimit": {
        "remainingThisMinute": remaining,
    },

    "count": len(matches),

    # Android can use this directly for the priority section.
    "important": matches[:10],

    # Full returned match set.
    "matches": matches,
}


OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE.write_text(
    json.dumps(output, ensure_ascii=False, indent=2),
    encoding="utf-8",
)


print(f"Fetched {len(matches)} matches.")
print(f"Wrote: {OUTPUT_FILE}")
print(f"Requests remaining this minute: {remaining}")

if matches:
    print("\nTop priority matches:")
    for match in matches[:10]:
        print(
            f"[{match['priority']}] "
            f"{match['home']['name']} vs {match['away']['name']} "
            f"({match['status']})"
        )

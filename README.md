# Football Data

Drop-in public GitHub repository for periodically fetching football data.

## Required setup

1. this repository is PUBLIC.
2. `main` as the default branch.
3. free `FOOTBALL_DATA_TOKEN` use to pull
5. A cron workflow is running under github action
7. data is populated under `data/matches.json`

anysystem can later read:

`https://raw.githubusercontent.com/mahbub-java/football-data-starter/main/data/matches.json`

The workflow updates approximately every 10 minutes.

Important:
- free plan may provide delayed scores rather than true real-time scores.

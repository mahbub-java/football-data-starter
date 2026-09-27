# Football Data

Periodically fetching football data with github actions bot.

## Required setup

No setup required

## How system work

1. can run cron workflow under github action
2. `FOOTBALL_DATA_TOKEN` use to pull 10 days matches data
3. The workflow updates approximately every 10 minutes.
4. data will automatically populated under `data/matches.json`

# How to use

Just read:

`https://raw.githubusercontent.com/mahbub-java/football-data-starter/main/data/matches.json`

# Important:
- free plan may provide delayed scores rather than true real-time scores.

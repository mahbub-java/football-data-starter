# Kotha Football Data

Drop-in public GitHub repository for periodically fetching football data.

## Required setup

1. Keep this repository PUBLIC.
2. Keep `main` as the default branch.
3. Go to:
   Settings -> Secrets and variables -> Actions -> New repository secret
4. Create:
   `FOOTBALL_DATA_TOKEN`
5. Paste your football-data.org API token.
6. Go to:
   Actions -> Update Football Data -> Run workflow
7. Verify:
   `data/matches.json`

Android can later read:

`https://raw.githubusercontent.com/<OWNER>/<REPO>/main/data/matches.json`

The workflow updates approximately every 10 minutes.

Important:
- Never put the football-data.org token in Android.
- Never commit the API token to this public repository.
- The football-data.org free plan may provide delayed scores rather than true real-time scores.

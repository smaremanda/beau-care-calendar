# Beau Care Calendar

Track **Beau's** daily Apoquel medication and baths. A Flask + Google Sheets web app
(same stack as the Bars / Fat Dog training apps), deployed on Railway.

- **`app/`** — the Flask application (see [`app/README.md`](app/README.md) for setup & deploy)
- **`beau-care-data-2026-05-30.csv`** — original data export (seeded into the Google Sheet)
- **`beau-care-build-prompt-2026-05-30.md`** — original GitHub Spark build prompt (design reference)

The Google Sheet is the source of truth. The app reads and writes it through the Sheets API;
logging a day upserts that date's row.

## Quick start
See [`app/README.md`](app/README.md) for full Google Cloud / Sheet / Railway setup.

```bash
cd app
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # set APP_PIN, SECRET_KEY, SHEET_ID
python3 populate_sheet.py   # one-time seed from the CSV
python3 app.py              # http://localhost:5001
```

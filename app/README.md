# Beau Care Calendar

A small Flask web app to track **Beau's** daily Apoquel medication and baths, with an optional
note per day. Data lives in a Google Sheet (the source of truth); the app reads and writes it
through the Google Sheets API. Same stack as the Bars / Fat Dog training apps.

- **Backend:** Flask + Google Sheets API v4
- **Frontend:** single-file `index.html` SPA (month/week calendar + analytics), Outfit font, cream/terracotta theme
- **Auth:** optional PIN (`APP_PIN`), 30-day Flask session
- **Hosting:** Railway (Procfile → gunicorn)

## Sheet schema (`Sheet1`)

| A (Date) | B (Apoquel) | C (Bath) | D (Notes) |
|----------|-------------|----------|-----------|
| `YYYY-MM-DD` | `Yes`/`No` | `Yes`/`No` | free text |

Logging a day is an **upsert**: an existing date's row is updated in place; a new date is appended.

## One-time setup

### 1. Google Cloud
1. Create a GCP project (e.g. `beau-care`).
2. Enable the **Google Sheets API**.
3. Create a **service account**, add a **JSON key**, download it.
4. Save the key as `app/credentials.json` (git-ignored).

### 2. Google Sheet
1. Create a new Google Sheet. Note its ID from the URL
   (`https://docs.google.com/spreadsheets/d/<SHEET_ID>/edit`).
2. **Share** the sheet (Editor) with the service-account email
   (`...@<project>.iam.gserviceaccount.com`).
3. Put the ID in `.env` as `SHEET_ID` (read by both `app.py` and `populate_sheet.py`).

### 3. Seed from the CSV
```bash
cd app
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then edit APP_PIN, SECRET_KEY, SHEET_ID
python3 populate_sheet.py --dry-run   # preview
python3 populate_sheet.py             # write to the sheet
```

### 4. Run locally
```bash
python3 app.py        # http://localhost:5001
```

### 5. Deploy to Railway
1. Push this repo to GitHub (`smaremanda/beau-care-calendar`).
2. New Railway project → deploy from the GitHub repo.
3. Set env vars in Railway:
   - `GOOGLE_CREDENTIALS` — paste the entire service-account key JSON
   - `SHEET_ID` — the sheet ID
   - `APP_PIN` — the access PIN
   - `SECRET_KEY` — a random string
4. Auto-deploys on push to `main`.

## Files
- `app.py` — Flask server, Sheets I/O, PIN auth, `/api/activities`, `/api/log`
- `index.html` — calendar SPA
- `populate_sheet.py` — one-time CSV → Sheet seeder
- `requirements.txt`, `Procfile`, `.env.example`, `manifest.json`, icons

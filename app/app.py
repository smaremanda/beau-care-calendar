import os
import json
import threading
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, send_from_directory, jsonify, request, session
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='.', static_url_path='')
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-change-in-prod')
app.permanent_session_lifetime = timedelta(days=30)

APP_PIN = os.environ.get('APP_PIN', '')


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not APP_PIN:          # no PIN configured → open access
            return f(*args, **kwargs)
        if not session.get('authenticated'):
            return jsonify({'error': 'unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated


SPREADSHEET_ID = os.environ.get('SHEET_ID', 'REPLACE_WITH_SHEET_ID')
SHEET_NAME = 'Sheet1'
ABOUT_TAB = 'About'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Column indices (0-based)
COL_DATE = 0
COL_APOQUEL = 1
COL_BATH = 2
COL_NOTES = 3


# The Sheets client wraps an httplib2 connection, which isn't thread-safe, so
# cache one client per thread rather than one per process.
_local = threading.local()


def get_service():
    service = getattr(_local, 'service', None)
    if service is None:
        creds_json = os.environ.get('GOOGLE_CREDENTIALS')
        if creds_json:
            info = json.loads(creds_json)
            creds = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
        else:
            creds = service_account.Credentials.from_service_account_file(
                'credentials.json', scopes=SCOPES
            )
        service = _local.service = build('sheets', 'v4', credentials=creds)
    return service


def get_all_rows():
    service = get_service()
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f'{SHEET_NAME}!A2:D2000'
    ).execute()
    return result.get('values', [])


def yn_to_bool(val):
    return str(val).strip().lower() in ('yes', 'true', '1', 'y')


def bool_to_yn(val):
    return 'Yes' if val else 'No'


def today_iso():
    return datetime.now().strftime('%Y-%m-%d')


# ── Routes ────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


@app.route('/api/auth', methods=['POST'])
def api_auth():
    if not APP_PIN:
        return jsonify({'status': 'ok'})
    data = request.json or {}
    if str(data.get('pin', '')).strip() == str(APP_PIN).strip():
        session.permanent = True
        session['authenticated'] = True
        return jsonify({'status': 'ok'})
    return jsonify({'error': 'wrong pin'}), 401


@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'status': 'ok'})


@app.route('/api/me')
def api_me():
    """Tell the frontend whether a PIN is required and if we're authed."""
    return jsonify({
        'pin_required': bool(APP_PIN),
        'authenticated': (not APP_PIN) or bool(session.get('authenticated')),
    })


@app.route('/api/activities')
@login_required
def api_activities():
    """Return the full {dateKey: {apoquel, bath, comment}} map."""
    rows = get_all_rows()
    activities = {}
    for row in rows:
        if not row or not row[0].strip():
            continue
        date = row[0].strip()
        apoquel = yn_to_bool(row[COL_APOQUEL]) if len(row) > COL_APOQUEL else False
        bath = yn_to_bool(row[COL_BATH]) if len(row) > COL_BATH else False
        comment = row[COL_NOTES] if len(row) > COL_NOTES else ''
        activities[date] = {'apoquel': apoquel, 'bath': bath, 'comment': comment}
    return jsonify(activities)


@app.route('/api/about')
@login_required
def api_about():
    """Return the About-Beau sections [{section, content}] from the About tab."""
    service = get_service()
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=f'{ABOUT_TAB}!A2:B200'
        ).execute()
    except Exception:
        return jsonify([])  # tab may not exist yet
    rows = result.get('values', [])
    sections = []
    for row in rows:
        if not row or not row[0].strip():
            continue
        sections.append({
            'section': row[0].strip(),
            'content': (row[1] if len(row) > 1 else '').strip(),
        })
    return jsonify(sections)


@app.route('/api/log', methods=['POST'])
@login_required
def api_log():
    data = request.json or {}
    date = str(data.get('date', '')).strip()
    if not date:
        return jsonify({'error': 'date required'}), 400

    # Client passes its local date; block logging future days.
    if date > today_iso():
        return jsonify({'error': "Can't log activities for future dates"}), 400

    apoquel = bool_to_yn(data.get('apoquel'))
    bath = bool_to_yn(data.get('bath'))
    comment = str(data.get('comment', ''))

    service = get_service()
    rows = get_all_rows()

    # Upsert: find an existing row with this date, else append.
    target_row = None
    for i, row in enumerate(rows):
        if row and row[0].strip() == date:
            target_row = i + 2  # data starts at sheet row 2
            break

    if target_row:
        service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=f'{SHEET_NAME}!B{target_row}:D{target_row}',
            valueInputOption='USER_ENTERED',
            body={'values': [[apoquel, bath, comment]]}
        ).execute()
    else:
        service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=f'{SHEET_NAME}!A2:D2',
            valueInputOption='USER_ENTERED',
            insertDataOption='INSERT_ROWS',
            body={'values': [[date, apoquel, bath, comment]]}
        ).execute()

    return jsonify({'status': 'ok', 'date': date})


if __name__ == '__main__':
    app.run(debug=True, port=5001)

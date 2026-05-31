"""
One-time script to populate the Beau Care Google Sheet from the exported CSV.

Usage:
    python3 populate_sheet.py
    python3 populate_sheet.py --dry-run   # preview rows without writing
"""

import csv
import sys
import os
import json
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

SPREADSHEET_ID = os.environ.get('SHEET_ID', 'REPLACE_WITH_SHEET_ID')
SHEET_NAME = 'Sheet1'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
CSV_FILE = '../beau-care-data-2026-05-30.csv'

HEADERS = ['Date', 'Apoquel', 'Bath', 'Notes']


def get_service():
    creds_json = os.environ.get('GOOGLE_CREDENTIALS')
    if creds_json:
        info = json.loads(creds_json)
        creds = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
    else:
        creds = service_account.Credentials.from_service_account_file(
            'credentials.json', scopes=SCOPES
        )
    return build('sheets', 'v4', credentials=creds)


def parse_date(raw):
    """Convert 'October 31, 2025' -> '2025-10-31'."""
    raw = raw.strip()
    return datetime.strptime(raw, '%B %d, %Y').strftime('%Y-%m-%d')


def parse_csv(filepath):
    rows = []
    with open(filepath, newline='') as f:
        reader = csv.DictReader(f)
        for r in reader:
            raw_date = (r.get('Date') or '').strip()
            if not raw_date:
                continue
            date_iso = parse_date(raw_date)
            rows.append([
                date_iso,
                (r.get('Apoquel') or 'No').strip(),
                (r.get('Bath') or 'No').strip(),
                (r.get('Notes') or '').strip(),
            ])
    rows.sort(key=lambda x: x[0])
    return rows


def get_sheet_id(service):
    meta = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    for s in meta['sheets']:
        if s['properties']['title'] == SHEET_NAME:
            return s['properties']['sheetId']
    return 0


def clear_sheet(service):
    service.spreadsheets().values().clear(
        spreadsheetId=SPREADSHEET_ID,
        range=f'{SHEET_NAME}!A1:D2000'
    ).execute()


def write_to_sheet(service, rows):
    all_values = [HEADERS] + rows
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f'{SHEET_NAME}!A1',
        valueInputOption='USER_ENTERED',
        body={'values': all_values}
    ).execute()

    sheet_id = get_sheet_id(service)
    service.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={
            'requests': [
                {
                    'repeatCell': {
                        'range': {'sheetId': sheet_id, 'startRowIndex': 0, 'endRowIndex': 1},
                        'cell': {'userEnteredFormat': {'textFormat': {'bold': True}}},
                        'fields': 'userEnteredFormat.textFormat.bold'
                    }
                },
                {
                    'updateSheetProperties': {
                        'properties': {'sheetId': sheet_id, 'gridProperties': {'frozenRowCount': 1}},
                        'fields': 'gridProperties.frozenRowCount'
                    }
                }
            ]
        }
    ).execute()


def main():
    dry_run = '--dry-run' in sys.argv

    csv_path = os.path.join(os.path.dirname(__file__), CSV_FILE)
    print(f'Parsing {csv_path}...')
    rows = parse_csv(csv_path)
    print(f'Found {len(rows)} care-log rows.')

    for r in rows[:5]:
        print(f'  {r[0]} | Apoquel={r[1]} | Bath={r[2]} | {r[3]}')
    if len(rows) > 5:
        print(f'  ... and {len(rows) - 5} more (last: {rows[-1][0]})')

    if dry_run:
        print('\n[DRY RUN] No changes written.')
        return

    print(f'\nWriting to sheet {SPREADSHEET_ID}...')
    service = get_service()
    clear_sheet(service)
    write_to_sheet(service, rows)
    print(f'Done. {len(rows)} rows written + header.')
    print(f'\nOpen: https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}')


if __name__ == '__main__':
    main()

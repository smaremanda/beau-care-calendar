"""
One-time: create an 'About' tab in the Beau Care sheet and seed starter sections.
Section | Content rows. Edit the content later directly in Google Sheets.

Usage: python3 setup_about_tab.py
"""
import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

SPREADSHEET_ID = os.environ.get('SHEET_ID', 'REPLACE_WITH_SHEET_ID')
ABOUT_TAB = 'About'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

HEADERS = ['Section', 'Content']
STARTER = [
    ['Feeding', '1 cup of kibble twice a day — morning (~7am) and evening (~6pm). Fresh water always. No table scraps.'],
    ['Apoquel', 'Allergy medication. Give with food. Track it on the Calendar tab. Skip if his stomach seems off — note it.'],
    ['Bathroom / Walks', 'Walk 2–3x a day. He usually goes right after meals. Bags are by the front door.'],
    ['Vet', 'Clinic: ____   Phone: ____   Address: ____'],
    ['Emergency Vet', '24-hour ER: ____   Phone: ____   Address: ____'],
    ['Allergies / Health', 'Note any known allergies, sensitivities, or ongoing issues here.'],
    ['Temperament & Quirks', 'How he behaves with strangers, other dogs, storms, being alone, favorite spots, commands he knows.'],
    ['Supplies', 'Where the food, leash, treats, poop bags, towels, and crate live.'],
    ['Contacts', 'Sudheer: ____   Backup / neighbor: ____'],
]


def get_service():
    creds_json = os.environ.get('GOOGLE_CREDENTIALS')
    if creds_json:
        info = json.loads(creds_json)
        creds = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
    else:
        creds = service_account.Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
    return build('sheets', 'v4', credentials=creds)


def tab_exists(service):
    meta = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    return any(s['properties']['title'] == ABOUT_TAB for s in meta['sheets'])


def sheet_id_for(service, title):
    meta = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    for s in meta['sheets']:
        if s['properties']['title'] == title:
            return s['properties']['sheetId']
    return None


def main():
    service = get_service()

    if tab_exists(service):
        print(f"'{ABOUT_TAB}' tab already exists — leaving its content untouched.")
        return

    service.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={'requests': [{'addSheet': {'properties': {'title': ABOUT_TAB}}}]}
    ).execute()
    print(f"Created '{ABOUT_TAB}' tab.")

    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f'{ABOUT_TAB}!A1',
        valueInputOption='USER_ENTERED',
        body={'values': [HEADERS] + STARTER}
    ).execute()

    sid = sheet_id_for(service, ABOUT_TAB)
    service.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={'requests': [
            {'repeatCell': {
                'range': {'sheetId': sid, 'startRowIndex': 0, 'endRowIndex': 1},
                'cell': {'userEnteredFormat': {'textFormat': {'bold': True}}},
                'fields': 'userEnteredFormat.textFormat.bold'
            }},
            {'updateSheetProperties': {
                'properties': {'sheetId': sid, 'gridProperties': {'frozenRowCount': 1}},
                'fields': 'gridProperties.frozenRowCount'
            }},
            {'updateDimensionProperties': {
                'range': {'sheetId': sid, 'dimension': 'COLUMNS', 'startIndex': 1, 'endIndex': 2},
                'properties': {'pixelSize': 500},
                'fields': 'pixelSize'
            }},
        ]}
    ).execute()
    print(f"Seeded {len(STARTER)} sections. Edit them anytime in Google Sheets.")
    print(f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}")


if __name__ == '__main__':
    main()

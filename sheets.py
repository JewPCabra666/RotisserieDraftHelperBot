from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import time
import traceback
import threading

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1uch6JNOBZR5F4bBTIC8FH__pJV5-mdbILee0jeHOhQo'
SHEET_ID = '354144647'
SAMPLE_RANGE_NAME = 'Class Data!A2:E'

creds = None
# The file token.pickle stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

service = build('sheets', 'v4', credentials=creds)


def every(delay, task):
    next_time = time.time() + delay
    while True:
        time.sleep(max(0, next_time - time.time()))
        try:
            task()
        except Exception:
            traceback.print_exc()
            # in production code you might want to have this instead of course:
            # logger.exception("Problem while executing repetitive task.")
        # skip tasks if we are behind schedule:
        next_time += (time.time() - next_time) // delay * delay + delay


def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """


    # Call the Sheets API
    result = service.spreadsheets().values().get(
        spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Draft 5 (Commander)!A1:R47").execute()
    print(result)

    values = [
        ["Testing", "Testing2"]
    ]
    body = {
        'values': values
    }
    result = service.spreadsheets().values().update(
        spreadsheetId=SAMPLE_SPREADSHEET_ID, range='Draft 5 (Commander)!J1:L1',
        valueInputOption='RAW', body=body).execute()

    print(result)


def put_value(column, pick_number, value):
    values = [
        [value]
    ]
    body = {
        'values' : values
    }
    result = service.spreadsheets().values().update(
        spreadsheetId=SAMPLE_SPREADSHEET_ID,
        range=f'Draft 5 (Commander)!{column}{pick_number+2}:{column}{pick_number+2}',
        valueInputOption='RAW',
        body=body).execute()
    print(result)



def test():
    t1 = threading.Thread(target=lambda: every(10, get_current_person_and_pick))
    t1.daemon = True
    t1.start()
    while True:
        print("testing?")
        time.sleep(5)


if __name__ == '__main__':
    test()

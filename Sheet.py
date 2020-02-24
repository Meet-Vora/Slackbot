"""To Install: Run `pip install --upgrade google-api-python-client`"""

from __future__ import print_function

import os
import csv

import httplib2 # pylint: disable=import-error
from googleapiclient import discovery # pylint: disable=import-error,no-name-in-module
from oauth2client import client # pylint: disable=import-error
from oauth2client import tools # pylint: disable=import-error
from oauth2client.file import Storage # pylint: disable=import-error

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'Sheets/client_secret.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'
WRITE_MASK = [1,0,0,1,0,1,0,1,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,1]
Mappings = [chr(65+i) for i in range(26)] + ['AA','AB','AC','AD','AE','AF','AG']

#Edit this id with the id in the URL of your spreadsheet!
SPREADSHEET_ID = '10JhC9BtpA4J-HivDTkkjpCVBLOrXIEcczChFhvbT8mQ'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    assert SPREADSHEET_ID != '1sXUXqkYVUML-OCvaezpqjKGK5sZapHF0rFQtr35zFsY'
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        # Needed only for compatibility with Python 2.6
        credentials = tools.run_flow(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

# pylint: disable=too-many-locals
def num_rows(sheet):
    """
    Returns how many rows are in the sheet.

    This is a slow method, so try to save the value that it returns and call it
    only when you need to.
    """
    assert sheet == 'Match Database' or sheet == 'Teams'

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)
    spreadsheetId = SPREADSHEET_ID
    range_name = sheet + ("!A1:AG" if sheet == 'Match Database' else "!A1:D")
    spreadsheet = service.spreadsheets() # pylint: disable=no-member
    game_data = spreadsheet.values().get(
        spreadsheetId=spreadsheetId, range=range_name).execute()
    return len(game_data['values'])

# pylint: disable=too-many-locals
def get_row(sheet, row_number):
    """
    A lot of this is adapted from google quickstart.
    Returns the data in the given row in the given sheet. Returns data as a list.
    Will error if you ask for a row that is out of bounds.

    row_number is 1 indexed!
    """
    assert isinstance(row_number, int)
    assert row_number > 1
    assert sheet == 'Match Database' or sheet == 'Teams'

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)
    spreadsheetId = SPREADSHEET_ID
    range_name = sheet + ("!A1:AG" if sheet == 'Match Database' else "!A1:D")
    spreadsheet = service.spreadsheets() # pylint: disable=no-member
    vals = spreadsheet.values().get(
        spreadsheetId=spreadsheetId, range=range_name).execute()
    try:
        return vals['values'][row_number - 1]
    except:
        raise ValueError('That Row is empty!')

# pylint: disable=too-many-locals
def set_row(sheet, row_number, data):
    """
    Sets the given row in the given sheet to the data that you provide. The data
    should be given as a list.

    Make sure not to write to a row that doesn't exist!

    This function takes a very long time to run, so try not to call it too much!

    row_number is 1 indexed!
    """
    assert isinstance(row_number, int)
    assert row_number > 1
    assert sheet == 'Match Database' or sheet == 'Teams'
    assert len(data) == 33 if sheet == 'Match Database' else 4
    assert isinstance(data, list) or isinstance(data, tuple)
    assert row_number <= num_rows(sheet)

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)
    spreadsheetId = SPREADSHEET_ID
    spreadsheet = service.spreadsheets() # pylint: disable=no-member
    for i in range(len(data)):
        if WRITE_MASK[i] == 0 and sheet == 'Match Database':
            continue
        if sheet == 'Match Database':
            range_name = "'" + sheet + "'!" + Mappings[i] + str(row_number)
        else:
            range_name = sheet + "!" + Mappings[i] + str(row_number)
        vals = spreadsheet.values().get(
            spreadsheetId=spreadsheetId, range=range_name).execute()
        vals['values'] = [[data[i]]]
        spreadsheet.values().update(spreadsheetId=spreadsheetId,
                               range=range_name, body=vals,
                               valueInputOption="RAW").execute()

# pylint: disable=too-many-locals
def name_from_num(num):
    """
    Uses the Teams sheet to translate team numbers to team names.

    Errors if given an invalid team number.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)
    spreadsheetId = SPREADSHEET_ID
    range_name = "Teams!A1:D"
    spreadsheet = service.spreadsheets() # pylint: disable=no-member
    vals = spreadsheet.values().get(
        spreadsheetId=spreadsheetId, range=range_name).execute()
    for i in range(1,num_rows("Teams")):
        if int(vals['values'][i][1]) == num:
            return vals['values'][i][0]
    raise ValueError('That team (' + str(num) + ') does not exist')

def get_row_of_match(num):
    """
    Uses Match Database to find what row a match is entered into.

    Errors if that match does not exist.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)
    spreadsheetId = SPREADSHEET_ID
    range_name = "Match Database!A1:AG"
    spreadsheet = service.spreadsheets() # pylint: disable=no-member
    vals = spreadsheet.values().get(
        spreadsheetId=spreadsheetId, range=range_name).execute()
    for i in range(1,num_rows("Match Database")):
        if int(vals['values'][i][0]) == num:
            return i+1
    raise ValueError('That match (' + str(num) + ') does not exist')

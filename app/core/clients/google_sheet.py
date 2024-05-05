import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pydantic import BaseModel, Field, field_validator


class GoogleSheet:
    def __init__(self, spreadsheet: str, credentials_path: str):
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
        self.spreadsheet = spreadsheet
        self.client = gspread.authorize(creds)

    def get_sheet_data(self, sheet: str):
        worksheet = self.client.open(self.spreadsheet).worksheet(sheet)
        records = worksheet.get_all_values()

        return records




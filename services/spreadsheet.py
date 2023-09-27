from __future__ import print_function

import configparser
import os
import os.path
import json
import gspread
import re
import urllib3
from oauth2client.service_account import ServiceAccountCredentials


class SpreadSheet():
    """
    Helper to work with google spreadsheets
    """

    def __init__(self, document, worksheet):
        # Load config.ini and get configs
        # print(urllib3.__version__)
        currentPath = os.path.dirname(os.path.realpath(__file__))
        creds_path = os.path.dirname(currentPath) + "/config.ini"

        self.DOCUMENT = document
        # API URLs
        self.SCOPES = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/drive"
        ]

        # Attempt to get credentials from creds.json, else use the environment variable
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, self.SCOPES)
        except FileNotFoundError:
            creds_dict = self.get_creds_from_env()
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, self.SCOPES)

        self.gclient = gspread.authorize(creds)
        self.SHEET = self.gclient.open(document).worksheet(worksheet)
        self.RECORDS = self.get_all_records()


    def get_creds_from_env(self):
        raw_creds = os.environ.get("GOOGLE_CREDS")
        if not raw_creds:
            raise ValueError("No credentials found in environment.")
        return json.loads(raw_creds)

    def find_and_fill_cell(self, cell_with_name, fill_row_number, fill_cell_value):
        cell = self.SHEET.find(cell_with_name)
        cell_row = cell.row
        self.SHEET.update_cell(cell_row, fill_row_number, fill_cell_value)

    #def bulk_update_cells(self):
    #    self.SHEET.update_cells()

    def get_all_records(self):
        return self.SHEET.get_all_records(expected_headers=[])

    def get_cell_value(self, cell_name, value_row):
        cell = self.SHEET.find(cell_name)
        return cell["value_row"]

    def check_row_value_exists(self, value):
        if any(obj['id'] == value for obj in self.RECORDS):
            return True
        return False
        # for record in self.RECORDS:
        #     if record["Id"] == value:
        #         return True
        # return False

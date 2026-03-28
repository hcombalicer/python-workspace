"""This is a testing module for connecting to google workspace"""

import json
import os

import gspread
from google.oauth2.service_account import Credentials

api_key = os.environ.get("API_KEY")
sheet_id = os.environ.get("TEST_SHEETID")

if api_key is None:
    raise ValueError("API_KEY environment variable is not set")

if sheet_id is None:
    raise ValueError("TEST_SHEETID environment variable is not set")

scopes = ["https://www.googleapis.com/auth/spreadsheets"]

service_account_info = json.loads(api_key)

creds = Credentials.from_service_account_info(
    service_account_info,
    scopes=scopes,
)

client = gspread.authorize(creds)
sheet = client.open_by_key(sheet_id)

values_list = sheet.sheet1.row_values(1)
print(values_list)

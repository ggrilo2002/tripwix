# from googleapiclient.discovery import build
# from google.oauth2 import service_account

# # Authenticate using the service account
# credentials = service_account.Credentials.from_service_account_file('creds/tripwix-422817-75deae41047c.json')
# drive_service = build('drive', 'v3', credentials=credentials)

# # Get storage quota information
# about = drive_service.about().get(fields='storageQuota').execute()
# print(about['storageQuota'])

import os
import base64
import json
from dotenv import load_dotenv

load_dotenv()

encoded_service_account = os.getenv('SACC')
service_account_info = json.loads(base64.b64decode(encoded_service_account))

from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
import os
from dotenv import load_dotenv
import schedule
import time

load_dotenv()

def transfer_files_between_drive_folders(source_folder_id, target_folder_id):
    import os
    import base64
    import json
    from dotenv import load_dotenv
    load_dotenv()
    encoded_service_account = os.getenv('SACC')
    creds = json.loads(base64.b64decode(encoded_service_account))
    scope = ['https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds, scope)
    drive_service = build('drive', 'v3', credentials=creds)

    # List all files in the source folder
    response = drive_service.files().list(q="'{}' in parents".format(source_folder_id),
                                          fields="files(id, name)").execute()
    source_files = response.get('files', [])

    # List all files in the target folder
    response = drive_service.files().list(q="'{}' in parents".format(target_folder_id),
                                          fields="files(id, name)").execute()
    target_files = response.get('files', [])
    target_file_names = {file['name'] for file in target_files}

    for file in source_files:
        file_name = file['name']
        file_id = file['id']

        if file_name not in target_file_names:
            # Move the file to the target folder
            drive_service.files().update(fileId=file_id,
                                         addParents=target_folder_id,
                                         removeParents=source_folder_id,
                                         fields='id, parents').execute()
        else:
            pass


src_folder = os.getenv('SHEETS_TRIPWIX')
dest_folder = os.getenv('ADMIN_SHEETS_TRIPWIX')
schedule.every().hour.do(transfer_files_between_drive_folders, src_folder, dest_folder)
# Run the scheduler continuously
while True:
    schedule.run_pending()
    time.sleep(86300)
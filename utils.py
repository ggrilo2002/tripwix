from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
import pandas as pd
import gspread
import yaml
from googleapiclient.http import MediaIoBaseDownload
from io import BytesIO
from googleapiclient.http import MediaFileUpload  

      
        
def sheets_creds(parentID, sheetsFileName):
    import os
    import base64
    import json
    from dotenv import load_dotenv
    load_dotenv()
    encoded_service_account = os.getenv('SACC')
    sacc_info = json.loads(base64.b64decode(encoded_service_account))
    scope = ['https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(sacc_info, scope)
    driveService = build('drive', 'v3', credentials=creds)

    def import_sheets_file(sheetsFileName, parentID, driveService):
        query = f"name='{sheetsFileName}' and '{parentID}' in parents and mimeType='application/vnd.google-apps.spreadsheet'"
        files = driveService.files().list(q=query, fields='files(id)').execute().get('files', [])
        
        if files:
            sheets_file_id = files[0]['id']
            return sheets_file_id
        else:
            return None

    if sheetsFileName != "None":
        sheets_file_id = import_sheets_file(sheetsFileName, parentID, driveService)
        if sheets_file_id:
            gc = gspread.service_account_from_dict(sacc_info)
            sh = gc.open_by_key(sheets_file_id)
            worksheet = sh.get_worksheet(0)
            data = worksheet.get_all_values()
            df = pd.DataFrame(data[1:], columns=data[0])
            yaml_data = df.to_dict(orient='records')
            yaml_content = {'credentials': {'usernames': {}}}
            for idx, row in enumerate(yaml_data):
                username = row['Email']
                yaml_content['credentials']['usernames'][username] = {'email': row['Email'], 'name': row['Name'], 'password': row['Password']}

            with open('creds/credentials.yaml', 'w') as yaml_file:
                yaml.dump(yaml_content, yaml_file)
                
            with open('creds/credentials.yaml', 'a') as yaml_file:
                yaml_file.write("\ncookie:\n  expiry_days: 0\n  key: 'Yess'\n  name: 'WantACookie'\npreauthorized:\n  emails:\n")
            return True
        
    return False

def upload_file_to_folder(filePath, folderID, driveService, newFileName):
    if newFileName is None:
        newFileName = filePath.split('/')[-1]  # If new file name is not provided, use the original file name

    file_metadata = {
        'name': newFileName,
        'parents': [folderID]
    }
    media_body = MediaFileUpload(filePath, resumable=True)
    file = driveService.files().create(body=file_metadata, media_body=media_body, fields='id').execute()
    return file.get('id')


def upload_file_thorough(folderID, filePath, fileName):
    import os
    import base64
    import json
    from dotenv import load_dotenv
    load_dotenv()
    encoded_service_account = os.getenv('SACC')
    sacc_info = json.loads(base64.b64decode(encoded_service_account))
    scope = ['https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(sacc_info, scope)

    driveService = build('drive', 'v3', credentials=creds)

    return upload_file_to_folder(filePath, folderID, driveService, fileName)


def upload_file_to_folder(filePath, folderID, driveService, newFileName):
    if newFileName is None:
        newFileName = filePath.split('/')[-1]  # If new file name is not provided, use the original file name

    file_metadata = {
        'name': newFileName,
        'parents': [folderID]
    }
    media_body = MediaFileUpload(filePath, resumable=True)
    file = driveService.files().create(body=file_metadata, media_body=media_body, fields='id').execute()
    return file.get('id')

def get_or_create_folder(driveService, parentFolderID, folderName):
    # Search for the folder with the given name
    query = f"'{parentFolderID}' in parents and name='{folderName}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = driveService.files().list(q=query, fields="files(id, name)").execute()
    items = results.get('files', [])

    if items:
        # Folder exists, return its ID
        return items[0]['id']
    else:
        # Folder does not exist, create it
        file_metadata = {
            'name': folderName,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parentFolderID]
        }
        folder = driveService.files().create(body=file_metadata, fields='id').execute()
        return folder.get('id')

def upload_file_thorough(folderID, filePath, fileName, folderName):
    import os
    import base64
    import json
    from dotenv import load_dotenv
    load_dotenv()
    encoded_service_account = os.getenv('SACC')
    sacc_info = json.loads(base64.b64decode(encoded_service_account))
    scope = ['https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(sacc_info, scope)

    driveService = build('drive', 'v3', credentials=creds)


    targetFolderID = get_or_create_folder(driveService, folderID, folderName)
    return upload_file_to_folder(filePath, targetFolderID, driveService, fileName)
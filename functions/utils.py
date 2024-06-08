from openai import OpenAI
import json
from dotenv import load_dotenv
import os
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
import pandas as pd
import gspread
import yaml
from googleapiclient.http import MediaIoBaseDownload
from io import BytesIO
from googleapiclient.http import MediaFileUpload  
from streamlit_chunk_file_uploader import uploader
import streamlit as st
import requests
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import os
from moviepy.editor import VideoFileClip
import hashlib
import shutil
from google.auth.transport.requests import Request
from google.oauth2 import service_account
import threading
import json
import streamlit.components.v1 as components
import time
from moviepy.editor import ImageClip, concatenate
import re

load_dotenv()

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


def fill_json(template, text):
    client = OpenAI(api_key=open_ai_key)
    prompt = get_prompt(template, text)
                
    response = client.chat.completions.create(
        model="gpt-4o",
       response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=1
    )

    return response.choices[0].message.content


def get_json(task):
    if task == "interior":
        with open('template/interior.json', "r") as json_file:
            return json.load(json_file) 

    elif task == "exterior":
        with open('template/exterior.json', "r") as json_file:
            return json.load(json_file)
    
    elif task == "bedroom":
        with open('template/bedrooms.json', "r") as json_file:
            return json.load(json_file)




def get_prompt(text, template):
    prompt = """Fill in the following JSON fields based on the given text, the new inputs can be booleans, strings or numbers. You should only use numbers or text if the already in place JSON value is "", else, your job is to change the JSON value to true if the feature is in place during the tour, if a feature is not available in the house, it should be kept as false. If there is no information to fill in a given value, it should be kept as false.
                Example:
                    Text: Hi, I am Filipe, and I'll be leading this tour, as you can see in the house, there is air conditioner but we don't provide body soap

                Original JSON:
                        {{
                        "Common": {{
                            "Air condition window": false,
                            "Air conditioning": false,
                            "Bed linens": false,
                            "Body soap": false}}
                            }}
                            
                Output required:
                        {{
                        "Common": {{
                            "Air condition window": false,
                            "Air conditioning": true,
                            "Bed linens": false,
                            "Body soap": false}}
                            }}
                            
                Please complete the JSON fields according to the provided context, be careful with every detail, reference and what is mentioned in the context


                Text: {}

                JSON Template (example):
                {}
                """.format(text, template)
    return prompt


def get_translation_prompt(transcript):
    prompt = """{}
    """.format(transcript)
    
    return prompt

def get_translation(transcript):
    client = OpenAI(api_key=open_ai_key)
    prompt = get_translation_prompt(transcript)
                
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a translation assistant. Your job is to translate text to English without adding or removing any sentence or idea. Preserve the original meaning and nuances."},
            {"role": "user", "content": prompt}
        ],
        temperature=1
    )

    return response.choices[0].message.content


def download_file_from_drive(file_name, folder_id):
    import os
    import base64
    import json
    from dotenv import load_dotenv
    load_dotenv()
    encoded_service_account = os.getenv('SACC')
    sacc_info = json.loads(base64.b64decode(encoded_service_account))
    scope = ['https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(sacc_info, scope)

    drive_service = build('drive', 'v3', credentials=creds)

    # Search for files with the given name in the specified folder
    response = drive_service.files().list(q="name='{}' and '{}' in parents".format(file_name, folder_id),
                                          orderBy="modifiedTime desc",
                                          fields="files(id, modifiedTime)").execute()
                                          
    files = response.get('files', [])
    
    if files:
        # Get the ID of the most recent file
        file_id = files[0]['id']
        request = drive_service.files().get_media(fileId=file_id)
        file_buffer = BytesIO()
        downloader = MediaIoBaseDownload(file_buffer, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        file_buffer.seek(0)
        
        # Convert string to JSON
        json_data = json.load(file_buffer)
        
        return json_data
    else:
        return None

def download_file_from_drive_bytes(file_name, folder_id):
    import os
    import base64
    import json
    from dotenv import load_dotenv
    load_dotenv()
    encoded_service_account = os.getenv('SACC')
    sacc_info = json.loads(base64.b64decode(encoded_service_account))
    scope = ['https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(sacc_info, scope)

    drive_service = build('drive', 'v3', credentials=creds)

    # Search for files with the given name in the specified folder
    response = drive_service.files().list(q="name='{}' and '{}' in parents".format(file_name, folder_id),
                                          orderBy="modifiedTime desc",
                                          fields="files(id, modifiedTime)").execute()
                                          
    files = response.get('files', [])
    
    if files:
        # Get the ID of the most recent file
        file_id = files[0]['id']
        request = drive_service.files().get_media(fileId=file_id)
        file_buffer = BytesIO()
        downloader = MediaIoBaseDownload(file_buffer, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        file_buffer.seek(0)
        
        return file_buffer
    else:
        return None


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



# Function to inject the JavaScript code into the Streamlit app
def st_confirmation_popup():
    # Custom HTML and JavaScript for the confirmation popup
    html_code = """
    <script type="text/javascript">
        window.onbeforeunload = function(event) {
            event.preventDefault();
            event.returnValue = '';
            return 'Are you sure you want to refresh the page?';
        };
    </script>
    """

    # Embed the custom HTML and JavaScript in the Streamlit app
    components.html(html_code, height=0)

def send_request_to_backend(username, tw_property, interior, bedrooms, exterior):
    def post_request():
        url = os.getenv('BACKEND_API')
        payload = {
            "username": username,
            "tw_property": tw_property,
            "interior": interior,
            "bedrooms": bedrooms,
            "exterior": exterior
        }
        print(payload)
        requests.post(url, json=payload)
    
    # Start the request in a separate thread
    threading.Thread(target=post_request).start()
    # Immediately switch to the success message page
    clean_directory('videos')
    clean_directory('audios')
    st.switch_page('pages/success_message.py')
    

def clean_directory(directory):   # use and only keep one record not 0
    # Get a list of all files in the directory
    files = os.listdir(directory)
    for file in files:
        # Construct the full file path
        file_path = os.path.join(directory, file)
        # Check if the file exists and if it's a file (not a directory)
        if os.path.isfile(file_path):
            if file != 'test.json':
                os.remove(file_path)


def verify_bedroom_videos():
    pattern = re.compile(r'uploaded_file_(bedroom_\d+)_(\d+)')
    for key, value in st.session_state.items():
        match = pattern.match(key)
        if match:
            bedroom = match.group(1)
            video_number = match.group(2)
            if st.session_state[f'uploaded_file_{bedroom}_{video_number}']:
                return True
        
    return False


def verify_interior_videos():
    for i in range(40):
        try:
            if st.session_state[f'interior_uploaded_file_{i}']:
                return True
        except:
            pass

    return False
    
def verify_exterior_videos():
    for i in range(40):
        try:
            if st.session_state[f'exterior_uploaded_file_{i}']:
                return True
        except:
            pass

    return False

def file_upload_download(display_text, key):
    file = uploader(display_text, key=key, chunk_size=31, type=['mp4', 'mov'])
    return file


def add_horizontal_divider():
    st.markdown("<hr style='border: 2px solid #eee;'>", unsafe_allow_html=True)

def generate_remove_button(key):
    button_html = f'''
        <button style="border-radius: 50%; width: 30px; height: 30px; line-height: 0; padding: 0; background-color: red; color: white; font-weight: bold;" onclick="removeInteriorVideo('{key}')">X</button>
    '''
    return button_html


def join_videos(video_variables):
  clips = []
  for video in video_variables:
    video_bytes = b''
    for chunk in iter(lambda: video.read(1024), b''):
      video_bytes += chunk

    # Assuming videos are byte data (adjust based on data format)
    clips.append(ImageClip(io.BytesIO(video_bytes)))

  # Concatenate all video clips
  final_clip = concatenate(clips)
  return final_clip

def convert_bedroom_name(name):
    return name.lower().replace(" ", "_")



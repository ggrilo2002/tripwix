import streamlit as st
from utils import upload_file_thorough
from dotenv import load_dotenv
import os
import hashlib
import shutil
import re
from moviepy.editor import VideoFileClip
from functions.utils import send_request_to_backend
import json


load_dotenv()
videos_tripwix = os.getenv('VIDEOS_TRIPWIX')
audios_tripwix = os.getenv('AUDIOS_TRIPWIX')
transcripts_tripwix = os.getenv('TRANSCRIPTS_TRIPWIX')
forms_tripwix = os.getenv('FORMS_TRIPWIX')
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# Function to save uploaded file to a temporary location
def save_uploadedfile(uploadedfile):
    file_hash = hashlib.md5(uploadedfile.getvalue()).hexdigest()
    _, file_extension = os.path.splitext(uploadedfile.name)
    file_name = file_hash + file_extension
    permanent_dir = "videos"  # Specify your permanent directory here
    permanent_file_path = os.path.join(os.getcwd(),permanent_dir, file_name)
    
    # Save the file to the permanent location
    with open(permanent_file_path, "wb") as permanent_file:
        shutil.copyfileobj(uploadedfile, permanent_file)
    
    return permanent_file_path

# Function to extract audio from video and save it to a file
def extract_audio(video_path, output_dir):
    try:
        video_clip = VideoFileClip(video_path)
        audio_path = os.path.splitext(os.path.basename(video_path))[0] + ".mp3"
        audio_path = os.path.join(os.getcwd(), output_dir, audio_path)
        video_clip.audio.write_audiofile(audio_path)
    except:
        video_clip = dict()
        audio_path = os.path.splitext(os.path.basename(video_path))[0] + ".mp3"
        audio_path = os.path.join(os.getcwd(), output_dir, audio_path)
        with open(audio_path, 'w') as f:
            json.dump(video_clip, f)

    return audio_path

def process_bedroom_videos(tw_property, progress_increment, progress_bar):
    bedrooms = []
    pattern = re.compile(r'uploaded_file_(bedroom_\d+)_(\d+)')
    for key, value in st.session_state.items():
        match = pattern.match(key)
        if match:
            bedroom = match.group(1)
            video_number = match.group(2)
            if st.session_state[f'uploaded_file_{bedroom}_{video_number}']:
                bedroom = send_bedrooms(st.session_state[f'uploaded_file_{bedroom}_{video_number}'], tw_property, bedroom, video_number)
                bedrooms.append(bedroom)
                st.session_state['progress'] += progress_increment
                progress_bar.progress(st.session_state['progress'])

    return bedrooms


def send_interior(interior_uploaded_file, tw_property, cont):
    if interior_uploaded_file:
        output_dir = "audios"
        output_dir = os.path.join(os.getcwd(), output_dir)
        os.makedirs(output_dir, exist_ok=True)

        video_path = save_uploadedfile(interior_uploaded_file)
        audio_path = extract_audio(video_path, output_dir)
        upload_file_thorough(videos_tripwix, video_path, f'{tw_property}__interior_{cont}', tw_property)
        upload_file_thorough(audios_tripwix, audio_path, f'{tw_property}__interior_{cont}', tw_property)

    return f'{tw_property}__interior_{cont}'

def send_exterior(exterior_uploaded_file, tw_property, cont):
    if exterior_uploaded_file:
        output_dir = "audios"
        output_dir = os.path.join(os.getcwd(), output_dir)
        os.makedirs(output_dir, exist_ok=True)

        video_path = save_uploadedfile(exterior_uploaded_file)
        audio_path = extract_audio(video_path, output_dir)
        upload_file_thorough(videos_tripwix, video_path, f'{tw_property}__exterior_{cont}', tw_property)
        upload_file_thorough(audios_tripwix, audio_path, f'{tw_property}__exterior_{cont}', tw_property)

    return f'{tw_property}__exterior_{cont}'
        
        
def send_bedrooms(bedroom_uploaded_files, tw_property, bedroom, video):
    if bedroom_uploaded_files:
        # Create audios folder if it doesn't exist
        output_dir = "audios"
        output_dir = os.path.join(os.getcwd(), output_dir)
        os.makedirs(output_dir, exist_ok=True)

        # for uploaded_file in bedroom_uploaded_files:
        video_path = save_uploadedfile(bedroom_uploaded_files)
        audio_path = extract_audio(video_path, output_dir)
        upload_file_thorough(videos_tripwix, video_path, f'{tw_property}__{bedroom}_{video}', tw_property)
        upload_file_thorough(audios_tripwix, audio_path, f'{tw_property}__{bedroom}_{video}', tw_property)
        
    return f'{tw_property}__{bedroom}_{video}'

st.write('Loading...')            
st.session_state['button_clicked'] = True

progress_bar = st.progress(0)  # Initialize the progress bar
progress_increment = 1 / st.session_state['total_videos']
interior_videos = []
for video in range(0,20):
    try:
        if st.session_state[f'interior_uploaded_file_{video}']:
            interior_videos.append(st.session_state[f'interior_uploaded_file_{video}'])
    except:
        pass

interiors = []
cont = 1
for video in interior_videos:
    interior = send_interior(video, st.session_state['twproperty'], cont)
    cont +=1
    st.session_state['progress'] += progress_increment
    progress_bar.progress(st.session_state['progress'])

    interiors.append(interior)



bedrooms = process_bedroom_videos(st.session_state['twproperty'], progress_increment, progress_bar)

exterior_videos = []
for video in range(0,40):
    try:
        if st.session_state[f'exterior_uploaded_file_{video}']:
            exterior_videos.append(st.session_state[f'exterior_uploaded_file_{video}'])
    except:
        pass

cont = 1
exteriors = []
for video in exterior_videos:
    exterior = send_exterior(video, st.session_state['twproperty'], cont)
    st.session_state['progress'] += progress_increment
    cont +=1
    exteriors.append(exterior)

progress_bar.progress(st.session_state['progress'])
send_request_to_backend(
        st.session_state['username'], st.session_state['twproperty'], interiors, bedrooms, exteriors
    )     
import streamlit as st
from dotenv import load_dotenv
import io
import zipfile
from functions.utils import file_upload_download, add_horizontal_divider, verify_interior_videos, verify_bedroom_videos, verify_exterior_videos
from streamlit_extras.stylable_container import stylable_container
import re
import os

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


# Main function to upload and display audio from video
def main():
    # st_confirmation_popup()
    # cookie_manager = CookieManager(key='ck')
    # cookies = cookie_manager.get_all()

    if 'interior_cont' not in st.session_state:
        st.session_state['interior_cont'] = 0

    if 'exterior_cont' not in st.session_state:
        st.session_state['exterior_cont'] = 0

    if 'bedroom_cont' not in st.session_state:
        st.session_state['bedroom_cont'] = 0  

    if 'bedroom_uploads' not in st.session_state:
        st.session_state['bedroom_uploads'] = {}

    st.session_state['interior_uploaded_file_0']=None
    st.session_state['exterior_uploaded_file_0']=None
    st.session_state['bedroom_uploaded_file_0']=None
    # --------------------------------------------------- PROPERTY SECTION ---------------------------------------------- #
    st.markdown(f"<h3><b>🏛️ Tripwix Name of Property </b></h3>", unsafe_allow_html=True)
    tw_property = st.text_input("", placeholder = 'Please enter the TripWix name of property')

    add_horizontal_divider()

    # --------------------------------------------------- INTERIOR SECTION ---------------------------------------------- #
    st.title("🛋️ Interior Video Uploader")

    # Loop for additional uploaders
    for i in range(st.session_state.get('interior_cont', 0)):
        col1, col2 = st.columns([10, 1])  # Adjust the widths of the columns as needed
        with col1:
            st.markdown(f"<h3><b>Interior Video {i + 1}</b></h3>", unsafe_allow_html=True)

        with col2:
            with stylable_container(
                "small_button",
                css_styles="""
                button {
                    background-color: #FF6666;
                    color: white;
                    font-size: 12px;
                    width: 50px;  /* Adjust width here */
                }
                """
            ):
                if st.button('X', key=f'interior_remover_{i}'):
                    st.session_state['interior_cont'] -= 1
                    st.rerun()

        st.session_state[f'interior_uploaded_file_{i}'] = file_upload_download("Record or upload a video of the interior of the house", key=f'file_uploader_interior_{i}')
    

    with stylable_container(
            "light_green",
            css_styles="""
            button {
                background-color: #90EE90;
                color: black;  /* Adjusting text color for better contrast */
            }""",
        ):
            # Button to add more uploaders
            if st.button('Add Interior Video', key='interior_adder'):
                st.session_state['interior_cont'] = st.session_state.get('interior_cont', 0) + 1
                st.rerun()

    add_horizontal_divider()

    
    # # --------------------------------------------------- EXTERIOR SECTION ---------------------------------------------- #
    st.title("🏡 Exterior Video Uploader")

    # Loop for additional uploaders
    for i in range(st.session_state.get('exterior_cont', 0)):
        col1, col2 = st.columns([10, 1])  # Adjust the widths of the columns as needed
        with col1:
            st.markdown(f"<h3><b>Exterior Video {i + 1}</b></h3>", unsafe_allow_html=True)


        with col2:
            with stylable_container(
                "small_button",
                css_styles="""
                button {
                    background-color: #FF6666;
                    color: white;
                    font-size: 12px;
                    width: 50px;  /* Adjust width here */
                }
                """
            ):
                if st.button('X', key=f'exterior_remover_{i}'):
                    st.session_state['exterior_cont'] -= 1
                    st.rerun()

        st.session_state[f'exterior_uploaded_file_{i}'] = file_upload_download("Record or upload a video of the interior of the house", key=f'file_uploader_exterior_{i}')
    

    with stylable_container(
            "light_green",
            css_styles="""
            button {
                background-color: #90EE90;
                color: black;  /* Adjusting text color for better contrast */
            }""",
        ):
        # Button to add more uploaders
        if st.button('Add Exterior Video', key='exterior_adder'):
            st.session_state['exterior_cont'] = st.session_state.get('exterior_cont', 0) + 1
            st.rerun()


    add_horizontal_divider()


    # # --------------------------------------------------- BEDROOM SECTION ---------------------------------------------- #
    st.title("🛏️ Bed + 🛁 Bath Video Uploader")

    # Initialize session state for uploaded files if not already done
    if "file_count" not in st.session_state:
        st.session_state["file_count"] = 0

    if "file_data" not in st.session_state:
        st.session_state["file_data"] = []

    # Function to convert bedroom name to a valid session state key
    def convert_bedroom_name(bedroom_name):
        return bedroom_name.lower().replace(" ", "_")

    # Function to add a new file uploader
    def add_new_file_uploader():
        st.session_state["file_count"] += 1
        st.session_state["file_data"].append({"file": None, "assigned_bedroom": None})

    # Function to remove a file uploader
    def remove_file_uploader(index):
        if index < len(st.session_state["file_data"]):
            file_info = st.session_state["file_data"].pop(index)
            if file_info["assigned_bedroom"]:
                bedroom_key = convert_bedroom_name(file_info["assigned_bedroom"])
                video_number = st.session_state["file_count"]
                session_key = f'uploaded_file_{bedroom_key}_{video_number}'
                if session_key in st.session_state:
                    del st.session_state[session_key]
            st.session_state["file_count"] -= 1

    # Use expander to manage the visibility of file uploaders
    with st.expander("Bed & Bath Videos", expanded=True):
        # Display uploaders for the files
        for i, file_info in enumerate(st.session_state["file_data"]):
            col1, col2, col3 = st.columns([7, 3, 1])
            
            with col1:
                st.markdown(f"<h3><b>Video {i + 1}</b></h3>", unsafe_allow_html=True)
            
            with col2:
                selected_bedroom = st.selectbox(
                    f"Assign to Bedroom", [f'Bedroom {j}' for j in range(1, 21)], key=f'assign_{i}',
                    index=int(file_info["assigned_bedroom"][-1]) - 1 if file_info["assigned_bedroom"] else 0
                )
                file_info["assigned_bedroom"] = selected_bedroom
            
            with col3:
                with stylable_container(
                    "small_button",
                    css_styles="""
                    button {
                        background-color: #FF6666;
                        color: white;
                        font-size: 12px;
                        width: 50px;
                    }
                    """
                ):
                    if st.button('X', key=f'remove_{i}'):
                        remove_file_uploader(i)
                        st.rerun()
            
            bedroom_key = convert_bedroom_name(selected_bedroom)
            session_key = f'uploaded_file_{bedroom_key}_{i + 1}'

            if session_key not in st.session_state:
                st.session_state[session_key] = None
            
            st.session_state[session_key] = file_upload_download(
                f"Record or upload a video for {selected_bedroom}", 
                key=f'file_uploader_{session_key}'
            )
            add_horizontal_divider()


    # Add new uploader button
    with stylable_container(
            "light_green",
            css_styles="""
            button {
                background-color: #90EE90;
                color: black;
            }"""
        ):
        if st.button('Add Bedroom Video', key='adder'):
            add_new_file_uploader()

            st.rerun()

    add_horizontal_divider()


    st.write("""
    <style>
    div.stDownloadButton > button {
        display: block;
        margin: 0 auto;
        width: 150px; /* Adjust the width as needed */
        color: white; /* Text color for better contrast */
    }""", unsafe_allow_html=True)

    st.write("""
    <style>
    div.stButton > button {
        display: block;
        margin: 0 auto;
        width: 200px; /* Adjust the width as needed */
        background-color: #40E0D0; /* Same color as the border */
        color: black; /* Text color for better contrast */
    }
    .stButton>button {
        border: 2px solid #40E0D0
        border-radius: 4px;
        padding: 10px 20px;
    }
    .stDownloadButton>button {
        border: 2px solid #40E0D0;
        border-radius: 4px;
        padding: 10px 20px;
    }
    @keyframes flash {
        0% { box-shadow: 0 0 5px ##92ff00; }
        50% { box-shadow: 0 0 20px #AFEEEE; } /* lighter turquoise for the middle flash */
        100% { box-shadow: 0 0 5px #92ff00; }
    }
    </style>
    """, unsafe_allow_html=True)

    zip_buffer = io.BytesIO()

    cont = 0
    if st.button('Submit Video Files to Tripwix', disabled=st.session_state['button_clicked']):
        st.session_state['progress'] = 0
        st.session_state['total_videos'] = 0


        # ------------------------------------------- COUNT VIDEO NUMBER ----------------------------- #
        st.session_state['total_videos'] += st.session_state['file_count']

        for video in range(0,40):
            try:
                if st.session_state[f'interior_uploaded_file_{video}']:
                    st.session_state['total_videos'] +=1
            except:
                pass

        for video in range(0,40):
            try:
                if st.session_state[f'exterior_uploaded_file_{video}']:
                    st.session_state['total_videos'] +=1
            except:
                pass
        
        if not (verify_interior_videos() and verify_bedroom_videos()):
            st.warning("Please upload interior and bedroom files")
        elif not tw_property:
            st.warning("Please state the property being recorded.")
        else:
            st.session_state['twproperty'] = tw_property
            st.switch_page('pages/loading.py')

        # Reset progress counters
        st.session_state['total_videos'] = 0
        st.session_state['zipped_files'] = set()

        # Count and add interior videos
        for i in range(st.session_state.get('interior_cont', 0)):
            uploaded_file = st.session_state.get(f'interior_uploaded_file_{i}')
            if uploaded_file and uploaded_file.name not in st.session_state['zipped_files']:
                st.session_state['zipped_files'].add(uploaded_file.name)
                st.session_state['total_videos'] += 1
                # Add file to zip
                with zipfile.ZipFile(zip_buffer, "a") as zf:
                    zf.writestr(uploaded_file.name, uploaded_file.getvalue())

        # Count and add exterior videos
        for i in range(st.session_state.get('exterior_cont', 0)):
            uploaded_file = st.session_state.get(f'exterior_uploaded_file_{i}')
            if uploaded_file and uploaded_file.name not in st.session_state['zipped_files']:
                st.session_state['zipped_files'].add(uploaded_file.name)
                st.session_state['total_videos'] += 1
                # Add file to zip
                with zipfile.ZipFile(zip_buffer, "a") as zf:
                    zf.writestr(uploaded_file.name, uploaded_file.getvalue())

        # Count and add bedroom videos
        pattern = re.compile(r'uploaded_file_(bedroom_\d+)_(\d+)')
        for key in st.session_state.keys():
            match = pattern.match(key)
            if match:
                uploaded_file = st.session_state.get(key)
                if uploaded_file and uploaded_file.name not in st.session_state['zipped_files']:
                    st.session_state['zipped_files'].add(uploaded_file.name)
                    st.session_state['total_videos'] += 1
                    # Add file to zip
                    with zipfile.ZipFile(zip_buffer, "a") as zf:
                        zf.writestr(uploaded_file.name, uploaded_file.getvalue())

        zip_buffer.seek(0)

        # Download button
        st.download_button(
            label="Download to Device",
            data=zip_buffer,
            file_name="videos.zip",
            mime="application/zip"
        )

    # Check if at least one file is uploaded
    if not (verify_exterior_videos() or verify_interior_videos() or verify_bedroom_videos()):
        pass
    else:
        with zipfile.ZipFile(zip_buffer, "w") as zf:
            for video in range(0,20):
                try:
                    if st.session_state[f'interior_uploaded_file_{video}']:
                        zf.writestr(st.session_state[f'interior_uploaded_file_{video}'].name, st.session_state[f'interior_uploaded_file_{video}'].getvalue())
                except:
                    pass
            for video in range(0,20):
                try:
                    if st.session_state[f'exterior_uploaded_file_{video}']:
                        zf.writestr(st.session_state[f'exterior_uploaded_file_{video}'].name, st.session_state[f'interior_uploaded_file_{video}'].getvalue())
                except:
                    pass

            pattern = re.compile(r'uploaded_file_(bedroom_\d+)_(\d+)')
            for key, value in st.session_state.items():
                match = pattern.match(key)
                if match:
                    bedroom = match.group(1)
                    video_number = match.group(2)

                    if st.session_state[f'uploaded_file_{bedroom}_{video_number}']:
                        zf.writestr(st.session_state[f'uploaded_file_{bedroom}_{video_number}'].name, st.session_state[f'uploaded_file_{bedroom}_{video_number}'].getvalue())


        zip_buffer.seek(0)
        
        st.write("")

        st.download_button(
            label="Download to Device",
            data=zip_buffer,
            file_name="videos.zip",
            mime="application/zip"
        )    
    
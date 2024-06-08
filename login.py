import streamlit as st
import yaml
from yaml.loader import SafeLoader
from streamlit_authenticator import Authenticate 
import os
from functions.utils import sheets_creds
from dotenv import load_dotenv
from face import main

st.markdown("""
<style>
	[data-testid="stDecoration"] {
		display: none;
	}
</style>""",
unsafe_allow_html=True)

if 'credentials_loaded' not in st.session_state:
    st.session_state['credentials_loaded'] = False

if 'authentication_status' not in st.session_state:
    st.session_state['authentication_status'] = False

if not st.session_state['credentials_loaded']:
    load_dotenv()
    parentID = os.getenv('PARENT_ID')
    sheetsFileName = os.getenv('SHEETS_FILE_NAME')
    sheets_creds(parentID, sheetsFileName)
    st.session_state['credentials_loaded'] = True

if not st.session_state['authentication_status']:
    with open('creds/credentials.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)


    authenticator = Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
    )

if __name__ == "__main__":

    if not st.session_state['authentication_status']:
        st.session_state['name'], st.session_state['authentication_status'], st.session_state['username'] = authenticator.login()
        
    if 'button_clicked' not in st.session_state:
        st.session_state['button_clicked'] = False
        
    if st.session_state['authentication_status'] == False:
        st.error('Username/password is incorrect')

    elif st.session_state['authentication_status'] == None:
        st.warning('Please enter your username and password')
    
    if st.session_state['authentication_status']:
        main()
        # authenticator.logout('Logout', 'main')




import streamlit as st
import time
try:
    st.success(f"🎉 Success! The upload was completed successfully. A confirmation will be sent to {st.session_state['username']}!")
except:
    st.success(f"Your files have been uploaded!")

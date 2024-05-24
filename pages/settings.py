import streamlit as st
import json
from firebase_admin import db

st.title("Settings")

# Function to save threads to Firebase
def save_threads_to_db():
    try:
        user_id = st.session_state.get("user_id")
        if user_id and "threads" in st.session_state:
            ref = db.reference(f'users/{user_id}')
            threads_json = json.dumps(st.session_state.threads)
            ref.update({"json_data": threads_json})
            st.success("Conversations saved to database.")
            st.write(f"Saved threads: {threads_json}")  # Log the saved threads for debugging
        else:
            st.error("User ID or threads not found in session state.")
    except Exception as e:
        st.error(f"Failed to save conversations: {str(e)}")

# Save Conversations manually
st.sidebar.title("Save Conversation")
if st.sidebar.button("Save to Database"):
    save_threads_to_db()

# Load Conversations
st.sidebar.title("Load Conversation")
uploaded_file = st.sidebar.file_uploader("Upload JSON file", type="json")
if uploaded_file:
    uploaded_threads = json.load(uploaded_file)
    # Clear existing threads and replace with uploaded threads
    st.session_state.threads = {}
    for key in list(uploaded_threads.keys()):
        unique_key = key
        counter = 1
        while unique_key in st.session_state.threads:
            unique_key = f"{key}_{counter}"
            counter += 1
        st.session_state.threads[unique_key] = uploaded_threads[key]
    st.session_state.current_thread = list(st.session_state.threads.keys())[0]  # Select the first thread by default
    st.session_state.file_loaded = True
    st.success("Conversations loaded successfully!")
    st.experimental_rerun()  # Reload the app with the newly loaded threads

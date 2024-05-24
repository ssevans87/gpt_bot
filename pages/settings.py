import streamlit as st
import json

st.title("Settings")

# Save Conversations
st.sidebar.title("Save Conversation")
if "threads" in st.session_state:
    threads_json = json.dumps(st.session_state.threads, indent=4)
    st.sidebar.download_button(
        label="Save",
        data=threads_json,
        file_name='gpt_conversations.json',
        mime='application/json'
    )
else:
    st.sidebar.warning("No conversations to save.")

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

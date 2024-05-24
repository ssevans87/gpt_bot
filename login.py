import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import pyrebase
import json

# Check if user is logged in
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Display logged in message if already authenticated
if st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; color: green;'>Logged in</h1>", unsafe_allow_html=True)

# Access secrets from Streamlit
firebase_config = {
    "apiKey": st.secrets["firebase"]["apiKey"],
    "authDomain": st.secrets["firebase"]["authDomain"],
    "databaseURL": st.secrets["firebase"]["databaseURL"],
    "projectId": st.secrets["firebase"]["projectId"],
    "storageBucket": st.secrets["firebase"]["storageBucket"],
    "messagingSenderId": st.secrets["firebase"]["messagingSenderId"],
    "appId": st.secrets["firebase"]["appId"],
    "measurementId": st.secrets["firebase"]["measurementId"]
}

# Load the service account key JSON from secrets
service_account_key = json.loads(st.secrets["firebase"]["serviceAccountKey"])

# Initialize Firebase Admin SDK if not already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate(service_account_key)
    firebase_admin.initialize_app(cred, {
        'databaseURL': st.secrets["firebase"]["databaseURL"]
    })

# Initialize Pyrebase
firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()


# Function to get user data from Realtime Database
def get_user_data(user_id):
    try:
        ref = db.reference(f'users/{user_id}')
        data = ref.get()
        if data:
            return data.get("gpt_api_key"), data.get("json_data")
        else:
            return None, None
    except Exception as e:
        st.error(f"Error accessing database: {str(e)}")
        return None, None


# Streamlit UI
st.title("Login")

# Login form
email = st.text_input("Email")
password = st.text_input("Password", type="password")

if st.button("Login"):
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        st.success("Successfully logged in!")
        st.session_state.logged_in = True
        st.session_state.user_id = user['localId']
        st.session_state.user_token = user['idToken']

        # Attempt to load GPT API key
        api_key, json_data = get_user_data(st.session_state.user_id)
        if api_key:
            st.session_state['key'] = api_key
            st.success("Successfully loaded GPT API key!")
        else:
            st.warning("No GPT API key found.")

        # Store JSON data in session state if loaded
        if json_data:
            st.session_state['json_data'] = json.loads(json_data)
        else:
            st.warning("No JSON data found.")
    except Exception as e:
        st.error(f"Error logging in: {str(e)}")

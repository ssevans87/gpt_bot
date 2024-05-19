import streamlit as st
from llm_agent import LlmChatAgent

st.set_page_config(layout="wide")
# Initialize or reset the main text and input text in the session state
if 'main_text' not in st.session_state:
    st.session_state['main_text'] = ""
if 'input_text' not in st.session_state:
    st.session_state['input_text'] = ""

if 'key' not in st.session_state or not st.session_state['key']:
    with st.form("key_form"):
        key_input = st.text_input("Please enter the key:")
        submitted = st.form_submit_button("Submit")
        if submitted and key_input:
            st.session_state['key'] = key_input
            st.experimental_rerun()


else:
    if 'bot' not in st.session_state or not st.session_state['bot']:
        st.session_state['bot'] = LlmChatAgent(model="gpt-4-0125-preview", api_key=st.session_state['key'])

    models = st.session_state['bot'].list_models()
    if models is None:
        st.session_state['key'] = None
        st.session_state['bot'] = None
        st.error("Invalid key. Please try again.")
        st.experimental_rerun()
    else:
        model_selected = st.selectbox("Select a model", models)
        st.session_state['bot'].set_model(model_selected)
        def submit_text():
            """Append the input text to the main text."""
            if st.session_state.input_text:  # Check if there's any input text
                st.session_state.main_text = st.session_state.bot.converse(st.session_state.input_text)
                st.session_state.input_text = ""  # Clear the input box after submitting

        def reset_text():
            """Clear both the main text and the input box."""
            st.session_state.main_text = ""
            st.session_state.input_text = ""
            st.session_state['bot'] = LlmChatAgent(model="gpt-4-0125-preview")

        # Using the full page layout to maximize space utilization


        # Main text box displayed on the top
        st.text_area("Main Text Box", value=st.session_state['main_text'], height=800, key='main_text_area', disabled=True)

        # Smaller input box (10 lines tall) on the bottom
        st.text_area("Input Text Box", value=st.session_state['input_text'], height=200, key='input_text', max_chars=None)

        col1, col2 = st.columns(2)
        with col1:
            submit_button = st.button("Submit", on_click=submit_text)
        with col2:
            reset_button = st.button("Reset", on_click=reset_text)

import streamlit as st
from openai import OpenAI
import json

# Ensure 'key' and 'client' are set up
if 'key' not in st.session_state or not st.session_state['key']:
    with st.form("key_form"):
        key_input = st.text_input("Please enter the key:")  # Input field for API key
        submitted = st.form_submit_button("Submit")  # Submit button for API key form
        if submitted and key_input:
            st.session_state['key'] = key_input
            st.experimental_rerun()  # Reload the app with the new API key
else:
    # Initialize OpenAI client
    if 'client' not in st.session_state or not st.session_state['client']:
        st.session_state['client'] = OpenAI(api_key=st.session_state['key'])

    # Fetch and store OpenAI models
    if "openai_models" not in st.session_state:
        try:
            models = st.session_state['client'].models.list()
            st.session_state["openai_models"] = [model.id for model in models.data]
        except Exception as e:
            st.session_state['client'] = None
            st.session_state['key'] = None
            st.session_state["openai_models"] = None
            st.experimental_rerun()  # Reload the app if there is an error

    # Find the index of the default model
    try:
        default_index = st.session_state["openai_models"].index("gpt-4")
    except ValueError:
        default_index = 0

    # Initialize threads and current_thread if not already set
    if "threads" not in st.session_state:
        st.session_state.threads = {"Thread1": {"title": "Thread1", "messages": []}}
        st.session_state.current_thread = "Thread1"

    if "current_thread" not in st.session_state:
        st.session_state.current_thread = "Thread1"

    if "file_loaded" not in st.session_state:
        st.session_state.file_loaded = False

    # Sidebar for selecting model and threads
    st.sidebar.title("Current conversation")

    thread = st.session_state.threads[st.session_state.current_thread]
    new_title = st.sidebar.text_input("Thread Title", value=thread["title"])
    st.session_state["openai_model"] = st.sidebar.selectbox("Select a model", st.session_state["openai_models"], index=default_index)

    st.sidebar.title("Thread Management")
    selected_thread = st.sidebar.selectbox("Select a thread", options=list(st.session_state.threads.keys()), index=list(st.session_state.threads.keys()).index(st.session_state.current_thread))

    # Editable title in sidebar

    if new_title != thread["title"]:
        if new_title not in st.session_state.threads:
            st.session_state.threads.pop(thread["title"])
            thread["title"] = new_title
            st.session_state.threads[new_title] = thread
            st.session_state.current_thread = new_title
            st.experimental_rerun()  # Reload the app with the updated title
        else:
            st.sidebar.error("Thread title must be unique!")  # Show error if the new title is not unique

    # Input and button to add a new thread
    new_thread_title = st.sidebar.text_input("New thread title")
    if st.sidebar.button("Add new thread"):
        if new_thread_title:
            if new_thread_title not in st.session_state.threads:
                st.session_state.threads[new_thread_title] = {"title": new_thread_title, "messages": []}
                st.session_state.current_thread = new_thread_title
                st.experimental_rerun()  # Reload the app with the new thread
            else:
                st.sidebar.error("Thread title must be unique!")  # Show error if thread title is not unique

    # Update the current thread if a new thread is selected
    if selected_thread:
        st.session_state.current_thread = selected_thread

    # Function to count tokens in messages
    def count_tokens(messages):
        return sum(len(m["content"].split()) for m in messages)

    # Function to prune messages if token limit is exceeded
    def prune_messages(messages, max_tokens):
        while count_tokens(messages) > max_tokens:
            messages.pop(0)
        return messages

    # Display and update the current thread
    if st.session_state.current_thread:
        thread = st.session_state.threads[st.session_state.current_thread]

        # Display messages
        for message in thread["messages"]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Add new message
        if prompt := st.chat_input("What is up?"):
            thread["messages"].append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Create a pruned version of messages for API call
            max_tokens = 4096  # Adjust based on the specific model's token limit
            pruned_messages = prune_messages(thread["messages"][:], max_tokens)  # Use a copy of the messages list

            with st.chat_message("assistant"):
                stream = st.session_state['client'].chat.completions.create(
                    model=st.session_state["openai_model"],
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in pruned_messages
                    ],
                    stream=True,
                )
                response = st.write_stream(stream)
            thread["messages"].append({"role": "assistant", "content": response})

        # Convert threads to JSON for download
        st.sidebar.title("Save Conversation")
        threads_json = json.dumps(st.session_state.threads, indent=4)
        st.sidebar.download_button(
            label="Save",
            data=threads_json,
            file_name='gpt_conversations.json',
            mime='application/json'
        )

    # Sidebar for uploading JSON file
    st.sidebar.title("Load Conversation")
    uploaded_file = st.sidebar.file_uploader("Upload JSON file", type="json")
    if uploaded_file and not st.session_state.file_loaded:
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
        st.experimental_rerun()  # Reload the app with the newly loaded threads

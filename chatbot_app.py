import streamlit as st
from openai import OpenAI





st.title("ChatGPT-like clone")

if 'key' not in st.session_state or not st.session_state['key']:
    with st.form("key_form"):
        key_input = st.text_input("Please enter the key:")
        submitted = st.form_submit_button("Submit")
        if submitted and key_input:
            st.session_state['key'] = key_input
            st.experimental_rerun()
else:
    if 'client' not in st.session_state or not st.session_state['client']:
        st.session_state['client'] = OpenAI(api_key=st.session_state['key'])

    if "openai_models" not in st.session_state:
        try:
            models = st.session_state['client'].models.list()
            st.session_state["openai_models"] = [model.id for model in models.data]
        except Exception as e:
            st.session_state['client'] = None
            st.session_state['key'] = None
            st.session_state["openai_models"] = None
            st.experimental_rerun()


    st.session_state["openai_model"] = st.selectbox("Select a model", st.session_state["openai_models"])

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What is up?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            stream = st.session_state['client'].chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})

import streamlit as st

from ingestion import Ingestion

from search_api import Inference

# Set up our front end page
st.set_page_config(page_title="Knowledgebase OpenAI Assistant", page_icon=":books:")


st.session_state.assistant_id = "asst_RbtKgT73vPz2xlzlTdrHOvHK"
st.session_state.thread_id = "thread_ItZgAl34aOKteAv8SZnIfS0I"
st.session_state.vector_store_id = "vs_67ae0ded5bf8819193a760c3598bb398"

# === Sidebar - where users can upload files
file_uploaded = st.sidebar.file_uploader(
    "Upload a pdf file along with meta to be transformed into embeddings", key="file_upload", type=["pdf"]
)

# Upload file button - store the file ID
if st.sidebar.button("Upload File"):
    if file_uploaded:

        ingestion = Ingestion("ingested_data", assistant_id= st.session_state.assistant_id, vector_store_id=st.session_state.vector_store_id)
        ingestion.run()

        st.write("Ingested succesfull")


# the main interface ...
st.title("Knowledgebase OpenAI Assistant")
st.write("Learn fast by chatting with your documents")

# # Check sessions
# if st.session_state.start_chat:
    
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show existing messages if any...
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# chat input for the user
if prompt := st.chat_input("What's new?"):
    # Add user message to the state and display on the screen
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # add the user's message to the existing thread

    inference = Inference(st.session_state.assistant_id, thread_id=st.session_state.thread_id)
    
    # Show a spinner while the assistant is thinking...
    with st.spinner("Wait... Generating response..."):

        response = inference.run_thread(prompt)

        st.session_state.messages.append(
            {"role": "assistant", "content": response}
            )
        with st.chat_message("assistant"):
            st.markdown(response, unsafe_allow_html=True)




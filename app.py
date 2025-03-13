import os
import streamlit as st
from openai import OpenAI
import time
from dotenv import load_dotenv

# Load environment variables for local development
load_dotenv()

# Set up API key from Streamlit secrets.toml
try:
    api_key = st.secrets["OPENAI_API_KEY"]
except KeyError:
    st.error("OpenAI API key is missing. Please add it to your secrets.toml file.")
    st.stop()

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

# Create sidebar
st.sidebar.title("Navigation Menu")
menu_selection = st.sidebar.radio(
    "Go to",
    ["Chat"]
)

st.sidebar.divider()
st.sidebar.info("© 2025 SoundStylist")

# Display chat interface when Chat is selected
if menu_selection == "Chat":
    st.title("Chat with Assistant")
    
    # Display chat messages from history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Get user input
    prompt = st.chat_input("What would you like to know?")
    
    # Process user input
    if prompt:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Create a thread if it doesn't exist
        if st.session_state.thread_id is None:
            thread = client.beta.threads.create()
            st.session_state.thread_id = thread.id
        
        # Add the user's message to the thread
        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=prompt
        )
        
        # Run the assistant on the thread
        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id="asst_NTpWCKDyZ85yjKUOwBnxmiY9"
        )
        
        # Display a spinner while waiting for the response
        with st.spinner("Thinking..."):
            # Poll for the run to complete
            while True:
                run_status = client.beta.threads.runs.retrieve(
                    thread_id=st.session_state.thread_id,
                    run_id=run.id
                )
                if run_status.status == "completed":
                    break
                time.sleep(0.5)
            
            # Get the assistant's response
            messages = client.beta.threads.messages.list(
                thread_id=st.session_state.thread_id
            )
            
            # Get the latest message from the assistant
            assistant_messages = [msg for msg in messages if msg.role == "assistant"]
            if assistant_messages:
                latest_message = assistant_messages[0]
                response = latest_message.content[0].text.value
                
                # Display assistant response in chat message container
                with st.chat_message("assistant"):
                    st.markdown(response)
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})

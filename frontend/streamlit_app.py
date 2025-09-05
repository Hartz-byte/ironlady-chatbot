import streamlit as st
import requests
import os
from datetime import datetime

# Configuration
API_URL = os.environ.get("CHAT_API_URL", "http://127.0.0.1:8000/chat")

# Set page config
st.set_page_config(
    page_title="Iron Lady Chatbot",
    page_icon="🤖",
    layout="centered"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .stTextInput>div>div>input {
        border-radius: 20px;
        padding: 10px 15px;
    }
    .stButton>button {
        border-radius: 20px;
        padding: 0.5rem 1.5rem;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 1rem;
        margin-bottom: 1rem;
        max-width: 80%;
    }
    .user-message {
        background-color: #e3f2fd;
        margin-left: 20%;
    }
    .bot-message {
        background-color: #f5f5f5;
        margin-right: 20%;
    }
    """, unsafe_allow_html=True)

# Initialize session state
if "history" not in st.session_state:
    st.session_state.history = []

# Header
st.title("Iron Lady Chatbot 🤖")
st.caption("Ask me about our programs, mentors, certificates, and more!")

# Chat input
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input(
        "Type your question here...",
        key="user_input",
        label_visibility="collapsed",
        placeholder="Ask about Iron Lady programs, mentors, certificates..."
    )
    submit_button = st.form_submit_button("Send", use_container_width=True)

# Handle form submission
if submit_button and user_input.strip():
    # Add user message to history
    st.session_state.history.append({
        "role": "user",
        "content": user_input,
        "time": datetime.now().strftime("%H:%M")
    })
    
    # Prepare the request
    payload = {
        "question": user_input,
        "use_model": True  # Set to False to disable LLM and only use FAQs
    }
    
    # Make API request
    with st.spinner("Thinking..."):
        try:
            # Make API request
            response = requests.post(API_URL, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            
            # Format the response based on source
            if data.get('is_faq', False):
                source = "🔍 FAQ"
            elif data.get('source') == 'llm':
                source = "🤖 AI"
            else:
                source = ""
            
            # Add bot response to history
            st.session_state.history.append({
                "role": "bot",
                "content": data.get("answer", "Sorry, I couldn't process your request."),
                "source": source,
                "time": datetime.now().strftime("%H:%M")
            })
            
        except requests.exceptions.RequestException as e:
            st.session_state.history.append({
                "role": "error",
                "content": f"Error connecting to the server: {str(e)}",
                "time": datetime.now().strftime("%H:%M")
            })
        except Exception as e:
            st.session_state.history.append({
                "role": "error",
                "content": f"An unexpected error occurred: {str(e)}",
                "time": datetime.now().strftime("%H:%M")
            })
    
    # Rerun to update the UI
    st.rerun()

# Display chat history
st.write("---")
st.subheader("Chat History")

for message in st.session_state.history:
    if message["role"] == "user":
        with st.container():
            st.markdown(
                f"""
                <div style='display: flex; justify-content: flex-end; margin-bottom: 10px;'>
                    <div class='chat-message user-message'>
                        <div><strong>You</strong> <small>{message['time']}</small></div>
                        <div>{message['content']}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        with st.container():
            source = message.get('source', '').upper()
            source_badge = f"<span style='font-size: 0.8em; color: #666;'>{source}</span>" if source else ""
            st.markdown(
                f"""
                <div style='display: flex; justify-content: flex-start; margin-bottom: 10px;'>
                    <div class='chat-message bot-message'>
                        <div><strong>🤖 Bot</strong> <small>{message['time']} {source_badge}</small></div>
                        <div>{message['content']}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

# Add a clear chat button
if st.button("Clear Chat", type="secondary"):
    st.session_state.history = []
    st.rerun()

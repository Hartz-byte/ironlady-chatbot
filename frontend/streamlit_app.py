import streamlit as st
import requests
import os
from datetime import datetime

# ===== CONFIG =====
BASE_URL = os.environ.get("API_BASE_URL", "http://127.0.0.1:8000")
CHAT_ENDPOINT = f"{BASE_URL}/chat"
HEALTH_ENDPOINT = f"{BASE_URL}/health"

st.set_page_config(
    page_title="Iron Lady Chatbot",
    page_icon="🤖",
    layout="wide"
)

# ===== CSS (modern chatbot UI) =====
st.markdown("""
    <style>
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .chat-box {
        display: flex;
        flex-direction: column;
    }
    .message {
        display: flex;
        align-items: flex-end;
        margin: 0.5rem 0;
        max-width: 80%;
        animation: fadeIn 0.3s ease-in-out;
    }
    .user {
        margin-left: auto;
        flex-direction: row-reverse;
    }
    .bot {
        margin-right: auto;
    }
    .bubble {
        padding: 0.75rem 1rem;
        border-radius: 18px;
        line-height: 1.4;
        position: relative;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    }
    .user .bubble {
        background: linear-gradient(135deg, #0078ff, #005fcc);
        color: white;
        border-bottom-right-radius: 4px;
    }
    .bot .bubble {
        background: #ffffff;
        color: #222;
        border-bottom-left-radius: 4px;
    }
    .avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        margin: 0 0.5rem;
        background-size: cover;
    }
    .user .avatar {
        background-image: url('https://cdn-icons-png.flaticon.com/512/847/847969.png');
    }
    .bot .avatar {
        background-image: url('https://cdn-icons-png.flaticon.com/512/4712/4712035.png');
    }
    .time {
        font-size: 0.7rem;
        margin-top: 4px;
        opacity: 0.7;
    }
    .clear-btn {
        position: fixed;
        bottom: 90px;
        right: 30px;
        background: #ff4b5c;
        color: white;
        border: none;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        font-size: 20px;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        transition: 0.3s;
    }
    .clear-btn:hover {
        background: #d93c4a;
        transform: rotate(90deg);
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    #MainMenu, header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ===== STATE =====
if "history" not in st.session_state:
    st.session_state.history = []
if "model_ready" not in st.session_state:
    st.session_state.model_ready = False

# ===== API HEALTH =====
def check_api_health():
    try:
        r = requests.get(HEALTH_ENDPOINT, timeout=10)
        if r.status_code == 200:
            data = r.json()
            return data.get("model_loaded", False)
    except Exception:
        return False
    return False

if not st.session_state.model_ready:
    with st.spinner("Checking backend API..."):
        st.session_state.model_ready = check_api_health()
    if not st.session_state.model_ready:
        st.error("❌ API is not available or model not ready. Please start backend.")
        st.stop()

# ===== HEADER =====
st.title("Iron Lady Chatbot 🤖")
st.caption("Ask me about leadership programs, mentors, and certificates!")

# ===== CHAT HISTORY UI =====
st.markdown("<div class='chat-box'>", unsafe_allow_html=True)
for msg in st.session_state.history:
    role = msg["role"]
    content = msg["content"]
    time = msg["time"]
    st.markdown(f"""
        <div class="message {role}">
            <div class="avatar"></div>
            <div>
                <div class="bubble">{content}</div>
                <div class="time">{time}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# ===== INPUT AREA =====
st.markdown("""
    <style>
    .chat-input-container {
        display: flex;
        align-items: center;
        margin-top: 10px;
    }
    .chat-input-container input {
        flex-grow: 1;
        border-radius: 20px;
        padding: 0.75rem 1rem;
        border: 1px solid #ddd;
        font-size: 1rem;
        margin-right: 0.5rem;
    }
    .chat-input-container button {
        border-radius: 20px;
        padding: 0.6rem 1.5rem;
        background: #0078ff;
        color: white;
        font-weight: 500;
        border: none;
        cursor: pointer;
        transition: all 0.2s ease-in-out;
    }
    .chat-input-container button:hover {
        background: #005fcc;
        transform: translateY(-1px);
    }
    </style>
""", unsafe_allow_html=True)

with st.form("chat_form", clear_on_submit=True):
    st.markdown('<div class="chat-input-container">', unsafe_allow_html=True)
    user_input = st.text_input("Type your message...", key="chat_input", label_visibility="collapsed")
    send = st.form_submit_button("Send")
    st.markdown('</div>', unsafe_allow_html=True)

if send and user_input.strip():
    # Add user msg
    st.session_state.history.append({
        "role": "user",
        "content": user_input,
        "time": datetime.now().strftime("%I:%M %p")
    })

    # API request
    try:
        with st.spinner("Thinking..."):
            payload = {"question": user_input, "use_model": True}
            resp = requests.post(CHAT_ENDPOINT, json=payload, timeout=300)
            resp.raise_for_status()
            data = resp.json()
            answer = data.get("answer", "⚠️ Sorry, I couldn't generate a response.")
    except Exception as e:
        answer = f"❌ Error contacting backend: {e}"

    # Add bot msg
    st.session_state.history.append({
        "role": "bot",
        "content": answer,
        "time": datetime.now().strftime("%I:%M %p")
    })

    st.rerun()

# ===== FLOATING CLEAR CHAT BUTTON =====
if st.session_state.history:
    if st.button("🗑️", key="clear", help="Clear chat"):
        st.session_state.history = []
        st.rerun()

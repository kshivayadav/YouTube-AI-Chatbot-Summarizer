# app.py
import streamlit as st
import requests
import os 
from dotenv import load_dotenv
load_dotenv(override=True)

API_KEY = os.getenv("API_KEY")
print(f'API_KEY in frontend:{API_KEY}')
BACKEND_URL = os.getenv("BACKEND_URL")

theme = st.get_option("theme.base")

user_bg = "#1E90FF"
user_text = "white"

bot_bg = "#2A2A2A" if theme == "dark" else "#F1F3F4"
bot_text = "#E8E8E8" if theme == "dark" else "#000000"

st.markdown(
    f"""
    <style>
        .user_msg {{
            background-color: {user_bg};
            color: {user_text};
            padding: 10px 15px;
            border-radius: 12px;
            margin-bottom: 10px;
            width: fit-content;
            max-width: 80%;
        }}
        .bot_msg {{
            background-color: {bot_bg};
            color: {bot_text};
            padding: 10px 15px;
            border-radius: 12px;
            margin-bottom: 15px;
            width: fit-content;
            max-width: 80%;
        }}
    </style>
    """,
    unsafe_allow_html=True
)


st.title("🎥 YouTube AI Chatbot")

url = st.text_input("Paste YouTube URL")
question = st.text_input("Enter your question")
submit = st.button("Submit")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

for role, msg in st.session_state["messages"]:
    tag = "user_msg" if role == "user" else "bot_msg"
    st.markdown(f"<div class='{tag}'>{msg}</div>", unsafe_allow_html=True)

def show_api_error(status_code, detail):
    if status_code == 400:
        st.error("❌ Invalid YouTube URL.")
    elif status_code == 401:
        st.error("🔒 Unauthorized. Invalid API key.")
    elif status_code == 403:
        st.error("🚫 Transcripts are disabled for this video.")
    elif status_code == 404:
        st.error("📄 No transcript found for this video.")
    elif status_code == 429:
        st.error("⏳ Too many requests. Please wait and try again.")
    elif status_code == 500:
        st.error("⚠️ Server error. Please try again later.")
    else:
        st.error(f"Unexpected error ({status_code}): {detail}")


def call_chat_api(url, payload, headers, stream=False):
    print(f'Headers:{headers}')
    try:
        return requests.post(
            url,
            json=payload,
            headers=headers,
            stream=stream,
            timeout=300
        )

    except requests.exceptions.Timeout:
        st.error("⏰ Request timed out. Please try again.")
        st.stop()

    except requests.exceptions.ConnectionError:
        st.error("🌐 Unable to connect to backend. Is FastAPI running?")
        st.stop()

    except Exception as e:
        st.error(f"Unexpected error: {e}")
        st.stop()


if submit:
    
    if not url or not question:
        st.warning("Please enter both YouTube URL and question.")
        st.stop()

    headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
    }


    payload = {
        "video_url": url,
        "question": question
    }


    response = call_chat_api(
        BACKEND_URL + "/chat/stream",
        payload,
        headers,
        stream=True,
    )
    
    if response.status_code != 200:
        try:
            detail = response.json().get("detail", "")
        except Exception:
            detail = ""
        show_api_error(response.status_code, detail)
        st.stop()
    

    bot_placeholder = st.empty()
    answer = ""

    try:
        for chunk in response.iter_content(chunk_size=1):
            if chunk:
                answer += chunk.decode("utf-8", errors="ignore")
                bot_placeholder.markdown(answer)

    except Exception:
        st.error("⚠️ Error while receiving streamed response.")
        st.stop()

    # Save chat history
    st.session_state["messages"].append(("user", question))
    st.session_state["messages"].append(("bot", answer))
    st.rerun()

    


# app.py
import streamlit as st
from chatbot import (
    extract_video_id,
    fetch_video_info,
    fetch_transcript,
    create_vectorstore,
    get_chat_response,
    NoTranscriptFound,
    TranscriptsDisabled,
)

# -------------------------------
# UI Styling
# -------------------------------
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

# Title
st.title("🎥 YouTube AI Chatbot")

# -------------------------------
# Main Inputs
# -------------------------------
url = st.text_input("Paste YouTube URL")
question = st.text_input("Enter your question")
submit = st.button("Submit")

# -------------------------------
# Chat History
# -------------------------------
if "messages" not in st.session_state:
    st.session_state["messages"] = []

for role, msg in st.session_state["messages"]:
    tag = "user_msg" if role == "user" else "bot_msg"
    st.markdown(f"<div class='{tag}'>{msg}</div>", unsafe_allow_html=True)




# -------------------------------
# Handle Submit
# -------------------------------
if submit:
    video_id = extract_video_id(url)
    if not video_id:
        st.error("Invalid YouTube URL")
        st.stop()

    info = fetch_video_info(video_id)

    if info["thumbnail_url"]:
        st.image(info["thumbnail_url"], width=480)
    if info["title"]:
        st.subheader(info["title"])

    try:
        with st.spinner("Fetching transcript…"):
            full_text = fetch_transcript(video_id)

        with st.spinner("Building vectorstore…"):
            retriever = create_vectorstore(full_text)

        with st.spinner("Generating response…"):
            response = get_chat_response(retriever, question)

        st.session_state["messages"].append(("user", question))
        st.session_state["messages"].append(("bot", response))
        st.rerun()

    except NoTranscriptFound:
        st.error("No transcript found for this video.")
    except TranscriptsDisabled:
        st.error("Transcripts are disabled for this video.")
    except Exception as e:
        st.error(f"Error: {e}")

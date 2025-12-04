from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from langchain_huggingface import HuggingFaceEndpoint,ChatHuggingFace, HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnableLambda, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import streamlit as st
import os
import requests
load_dotenv()
os.environ["HUGGINGFACEHUB_API_TOKEN"] = os.getenv("HUGGINGFACEHUB_API_TOKEN")

theme = st.get_option("theme.base")
if theme == "dark":
    user_bg = "#1E90FF"      # blue bubble
    user_text = "white"

    bot_bg = "#2A2A2A"       # dark grey
    bot_text = "#E8E8E8"
else:
    user_bg = "#1E90FF"
    user_text = "white"

    bot_bg = "#F1F3F4"
    bot_text = "#000000"

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
            font-size: 16px;
        }}
        .bot_msg {{
            background-color: {bot_bg};
            color: {bot_text};
            padding: 10px 15px;
            border-radius: 12px;
            margin-bottom: 15px;
            width: fit-content;
            max-width: 80%;
            font-size: 16px;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🎥 YouTube AI Chatbot")
st.markdown(
    """
    <style>
    .stApp h1 {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    </style>
    """,
    unsafe_allow_html=True
)

url = st.text_input("Paste Youtube URL Link here")
question = st.text_input("Enter your Question")
submit = st.button("Submit")
full_text = ""

def fetch_video_info(video_id):
    url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
    resp = requests.get(url)
    if resp.status_code == 200:
        data = resp.json()
        return {
            "title": data.get("title"),
            "thumbnail_url": data.get("thumbnail_url")
        }
    else:
        return {
            "title": None,
            "thumbnail_url": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
        }

def extract_video_id(url):
    if "watch?v=" in url:
        return url.split("watch?v=")[-1]
    if "youtu.be/" in url:
        return url.split("youtu.be/")[-1]
    return None

def format_docs(docs):
    context_text = "\n\n".join([doc.page_content for doc in docs])
    return context_text

if "messages" not in st.session_state:
    st.session_state["messages"] = []


for role, msg in st.session_state["messages"]:
    if role == "user":
        st.markdown(f"<div class='user_msg'>{msg}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='bot_msg'>{msg}</div>", unsafe_allow_html=True)


if submit:
    video_id = extract_video_id(url)
    if not video_id:
        st.error("Invalid YouTube URL")
        st.stop()

    info = fetch_video_info(video_id)
    if info.get("thumbnail_url"):
        st.image(info["thumbnail_url"], width=480)
    if info.get("title"):
        st.subheader(info["title"])

    try:
        with st.spinner("Fetching transcript..."):
            yt = YouTubeTranscriptApi()
            transcript_list = yt.fetch(
                video_id, 
                languages=['en', 'hi', 'te', 'ta', 'ml', 'kn', 'bn', 'mr', 'gu', 'pa']
                )  
            full_text = " ".join([chunk.text for chunk in transcript_list])
            print(full_text)

        with st.spinner("Splitting and Embedding..."):
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, 
                chunk_overlap=200
            )
            chunks = splitter.create_documents([full_text])
            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
            vectorstore = FAISS.from_documents(
                chunks, 
                embeddings
            )
            retriever = vectorstore.as_retriever(
                search_type="similarity", 
                search_kwargs={"k":4}
            )

        with st.spinner("Generating response..."):
            llm = HuggingFaceEndpoint(
                repo_id = 'openai/gpt-oss-120b',
                task = 'text-generation',
                temperature=0.7,
            )
            model = ChatHuggingFace(llm = llm)

            parser = StrOutputParser()
            prompt = PromptTemplate(
                template="""
                You are an expert AI assistant.
                Answer the user using ONLY the transcript context below.
                If the answer is not found, say:
                "The transcript does not contain this information."

                CONTEXT:
                {context}

                QUESTION:
                {question}
                """,
                input_variables=["context", "question"]
            )

            parrallel_chain = RunnableParallel({
                "context": retriever | RunnableLambda(format_docs),
                "question": RunnablePassthrough()
            })

            seq_chain = prompt | model | parser
            final_chain = parrallel_chain | seq_chain
            response = final_chain.invoke(question)
        st.success("Response generated!")
        st.write(response)

        st.session_state["messages"].append(("user", question))
        st.session_state["messages"].append(("bot", response))
        st.rerun()
            
    except NoTranscriptFound:
        st.error("No transcript found for this video.")
    except TranscriptsDisabled:
        st.error("Transcripts are disabled for this video.")
    except Exception as e:
        st.error(f"An error occurred: {e}")
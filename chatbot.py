# chatbot.py
import os
import requests
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace, HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnableLambda, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

load_dotenv()
os.environ["HUGGINGFACEHUB_API_TOKEN"] = os.getenv("HUGGINGFACEHUB_API_TOKEN")


# -------------------------------
# Extract Video ID
# -------------------------------
def extract_video_id(url):
    if "watch?v=" in url:
        return url.split("watch?v=")[-1]
    if "youtu.be/" in url:
        return url.split("youtu.be/")[-1]
    return None


# -------------------------------
# Fetch Title + Thumbnail
# -------------------------------
def fetch_video_info(video_id):
    url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
    resp = requests.get(url)

    if resp.status_code == 200:
        data = resp.json()
        return {
            "title": data.get("title"),
            "thumbnail_url": data.get("thumbnail_url")
        }

    return {
        "title": None,
        "thumbnail_url": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
    }


# -------------------------------
# Fetch Transcript
# -------------------------------
def fetch_transcript(video_id):
    transcript_list = YouTubeTranscriptApi().fetch(
        video_id,
        languages=['en', 'hi', 'te', 'ta', 'ml', 'kn', 'bn', 'mr', 'gu', 'pa']
    )
    full_text = " ".join([chunk.text for chunk in transcript_list])
    return full_text


# -------------------------------
# Create FAISS Vectorstore
# -------------------------------
def create_vectorstore(text):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.create_documents([text])

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    vectorstore = FAISS.from_documents(chunks, embeddings)
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 4})

    return retriever


# -------------------------------
# Answer User Question
# -------------------------------
def get_chat_response(retriever, question):
    def format_docs(docs):
        return "\n\n".join([doc.page_content for doc in docs])

    llm = HuggingFaceEndpoint(
        repo_id='openai/gpt-oss-120b',
        task='text-generation',
        temperature=0.7,
    )
    model = ChatHuggingFace(llm=llm)

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

    parser = StrOutputParser()

    parallel_chain = RunnableParallel({
        "context": retriever | RunnableLambda(format_docs),
        "question": RunnablePassthrough()
    })

    seq_chain = prompt | model | parser

    final_chain = parallel_chain | seq_chain

    return final_chain.invoke(question)

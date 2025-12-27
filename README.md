# 🎥 YouTube AI Chatbot & Summarizer

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.27-green)](https://streamlit.io/)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-🤗-orange)](https://huggingface.co/)

# 🎥 YouTube AI Chatbot

A **production-grade YouTube AI Chatbot** that allows users to paste a YouTube video URL and ask questions about its content.  
The system extracts the video transcript, builds a semantic search index, and generates accurate answers using **Retrieval-Augmented Generation (RAG)**.

Built with **FastAPI**, **Streamlit**, **LangChain**, **FAISS**, and **HuggingFace LLMs**, featuring authentication, rate limiting, caching, and streaming responses.

---

## 🚀 Features

- 🔗 Paste any YouTube video URL
- 🧠 Ask natural language questions about the video
- 📜 Automatic transcript extraction (multi-language support)
- 🔍 Semantic search using FAISS vector database
- 🤖 Context-aware answers using LLMs (RAG architecture)
- ⚡ Streaming responses for better UX
- 🔐 API key–based authentication
- 🚦 Rate limiting using SlowAPI
- 🧩 Caching for transcripts and embeddings
- 🌐 FastAPI backend + Streamlit frontend
- 🐳 Dockerized for easy deployment

---


## 🏗️ Architecture

User (Browser)
     ↓
Streamlit Frontend
     ↓
FastAPI Backend (Auth + Rate Limit)
     ↓
Transcript Extraction (YouTube API)
     ↓
FAISS Vector Store (Embeddings)
     ↓
HuggingFace LLM (LangChain)


## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/kshivayadav/YouTube-AI-Chatbot-Summarizer.git
cd YouTube-AI-Chatbot-Summarizer
```
2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```
3. Set your HuggingFace API token in .env:
```bash
HUGGINGFACEHUB_API_TOKEN=your_token_here
API_KEY = your_auth_key
```
4. Backend Setup:
```bash
cd backend
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
uvicorn main:app --reload
```
Backend will be available at: 
```
http://localhost:8000
(http://localhost:8000/docs)
```

5. Frontend Setup 
```bash
cd frontend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```
Frontend will be available at:
```bash
http://localhost:8501
```


---

## 🧠 Tech Stack

### Frontend
- Streamlit
- Python
- Requests

### Backend
- FastAPI
- LangChain
- FAISS
- HuggingFace Inference API
- YouTube Transcript API
- SlowAPI (Rate Limiting)

### DevOps
- Docker
- Docker Compose
- dotenv

---

## 📂 Project Structure

```
YOUTUBE_CHATBOT/
│
├── backend/
│ ├── main.py
│ ├── chatbot.py
│ ├── schemas.py
│ ├── requirements.txt
│ ├── Dockerfile
│ └── .env
│
├── frontend/
│ ├── app.py
│ ├── requirements.txt
│ ├── Dockerfile
│ └── .env
│
├── docker-compose.yml
└── README.md
```



---

## 🔐 Environment Variables

### Backend `.env`

```env
API_KEY=supersecretkey
HUGGINGFACEHUB_API_TOKEN=your_huggingface_token
```

### Frontend `.env`

```env
API_KEY=supersecretkey
BACKEND_URL=http://localhost:8000
```

### 🐳 Docker Setup
Run everything with Docker Compose
```bash
docker-compose up --build
```
### 🔑 Authentication
All API requests require an Authorization header:

Authorization: Bearer supersecretkey

Authentication is enforced using FastAPI dependencies and integrated with Swagger UI.

### 🚦 Rate Limiting

Rate limiting is implemented using SlowAPI:

Limit: 5 requests per minute per IP

Prevents abuse and API overuse

### 📡 API Endpoints
Health Check

GET /health

Request Body

{
  "video_url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "question": "What is this video about?"
}

Chat (Streaming)

POST /chat/stream

Streams the response token-by-token for real-time UX.

### 🧠 How It Works (RAG Flow)

Extract YouTube transcript

Split transcript into chunks

Generate embeddings using Sentence Transformers

Store embeddings in FAISS

Retrieve relevant chunks

Send context + question to LLM

Generate accurate, grounded answer

⭐ Highlights

Multi-language transcript support

Handles long YouTube videos with vector embeddings

Uses sentence-transformers/all-MiniLM-L6-v2 for Embeddings

Uses GPT-OSS for lightweight LLM responses

Polished professional UI suitable for recruiters

📌 Notes

If transcripts are disabled for a video, the app will display an error.

The AI will only answer from the transcript. If information is missing, it responds with:

"The transcript does not contain this information."

## 📫 Contact

- **GitHub:** [kshivayadav](https://github.com/kshivayadav)  
- **LinkedIn:** [K Shiva Kumar](https://www.linkedin.com/in/shiva-kumar-5586432b0/)  
- **Email:** [kshivayadav7@gmail.com](mailto:kshivayadav7@gmail.com)  





# 🎥 YouTube AI Chatbot & Summarizer

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.27-green)](https://streamlit.io/)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-🤗-orange)](https://huggingface.co/)

A **smart AI-powered YouTube Chatbot** that summarizes YouTube video transcripts and answers your questions **using only the video transcript**. Built with **Streamlit, LangChain, HuggingFace embeddings, and GPT-OSS LLMs**.

---

## ⚡ Features

- Paste a **YouTube URL** and fetch the transcript automatically.
- Ask **questions about the video** and get precise AI responses.
- Shows **video thumbnail, title, and duration**.
- Works in **multiple languages**: English, Hindi, Telugu, Tamil, Malayalam, Kannada, Bengali, Marathi, Gujarati, Punjabi.
- Maintains **chat history** for continuous conversation.
- Handles **long transcripts** using chunking and vector embeddings.
- Fully interactive **Streamlit UI**.

---

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
3. Install dependencies:
```bash
pip install -r requirements.txt
```
4 . Set your HuggingFace API token in .env:
```bash
HUGGINGFACEHUB_API_TOKEN=your_token_here
```
5. Run the Streamlit
```bash
streamlit run chatbot.py
```

🛠️ Tech Stack

Streamlit – Interactive web app

LangChain – Orchestrating embeddings and LLMs

HuggingFace – Embeddings & LLM models

FAISS – Vector database for semantic search

YouTube Transcript API – Fetch video transcripts

💡 Usage

Open the Streamlit app.

Paste the YouTube URL.

Enter a question related to the video.

Click Submit and get an AI-generated answer.

Scroll through the chat history to see previous Q&A.

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





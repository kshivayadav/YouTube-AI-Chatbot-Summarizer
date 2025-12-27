from fastapi import FastAPI, HTTPException, Depends, Header,Request
from fastapi.responses import JSONResponse,StreamingResponse
from fastapi.concurrency import run_in_threadpool
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from typing import Dict
from schemas import ChatRequest,ChatResponse
from chatbot import (
    extract_video_id,
    fetch_video_info,
    fetch_transcript,
    create_vectorstore,
    get_chat_response,
    NoTranscriptFound,
    TranscriptsDisabled
)

import os
from dotenv import load_dotenv
load_dotenv(override=True)

API_KEY = os.getenv("API_KEY")

print(f'API_KEY in backend:{API_KEY}')
api_key_header = APIKeyHeader(name="Authorization", auto_error=False)


transcript_cache: Dict[str, str] = {}
vectorstore_cache: Dict[str, object] = {}


app = FastAPI(
    title="YouTube AI Chatbot API",
    version="2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests"}
    )

    
def verify_api_key(api_key: str = Depends(api_key_header)):
    if not api_key:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    if api_key != f"Bearer {API_KEY}":
        raise HTTPException(status_code=401, detail="Invalid API key")



@app.get("/")
def read_root():
    return {"message": "Welcome to the YouTube AI Chatbot API"}

@app.get("/health")
def health_check():
    return {"status": "healthy",
            "message": "API is up and running",
            "version": "1.0"
            }

@app.post("/chat", response_model=ChatResponse)
@limiter.limit("5/minute")
async def chat(request : Request,
               data: ChatRequest,
               auth:str = Depends(verify_api_key)):

    video_id = extract_video_id(data.video_url)
    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")

    try:
        if video_id not in transcript_cache:
            transcript_cache[video_id] = fetch_transcript(video_id)

        transcript = transcript_cache[video_id]

        if video_id not in vectorstore_cache:
            vectorstore_cache[video_id] = create_vectorstore(transcript)

        retriever = vectorstore_cache[video_id]
        info = fetch_video_info(video_id)

        answer = await run_in_threadpool(get_chat_response, retriever, data.question)

        return ChatResponse(
            answer=answer,
            title=info.get("title"),
            thumbnail_url=info.get("thumbnail_url")
        )

    except NoTranscriptFound:
        raise HTTPException(status_code=404, detail="No transcript found")
    except TranscriptsDisabled:
        raise HTTPException(status_code=403, detail="Transcripts disabled")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/stream")
@limiter.limit("5/minute")
async def chat_stream(request: Request, 
                      data: ChatRequest,
                       auth: str = Depends(verify_api_key)):

    try:
        video_id = extract_video_id(data.video_url)
        if not video_id:
            raise HTTPException(status_code=400, detail="Invalid YouTube URL")

        if video_id not in transcript_cache:
            transcript_cache[video_id] = fetch_transcript(video_id)

        if video_id not in vectorstore_cache:
            vectorstore_cache[video_id] = create_vectorstore(transcript_cache[video_id])

        retriever = vectorstore_cache[video_id]

        def generator():
            try:
                answer = get_chat_response(retriever, data.question)
                for token in answer.split():
                    yield token + " "
            except Exception as e:
                yield f"\n[ERROR]: {str(e)}"

        return StreamingResponse(generator(), media_type="text/plain")
    
    except NoTranscriptFound:
        raise HTTPException(status_code=404, detail="No transcript found")
    except TranscriptsDisabled:
        raise HTTPException(status_code=403, detail="Transcripts disabled")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
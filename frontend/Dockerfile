# ---------- Stage 1: Build ----------
FROM python:3.10-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip wheel --no-cache-dir --no-deps -r requirements.txt -w /wheels


# ---------- Stage 2: Runtime ----------
FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=builder /wheels /wheels

RUN pip install --no-cache-dir /wheels/* \
    && rm -rf /wheels

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py","--server.port=8501","--server.address=0.0.0.0","--server.enableCORS=false","--server.enableXsrfProtection=false"]

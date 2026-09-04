FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps for psycopg/cryptography — keep lean, no build-essential needed for binary wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# Run as non-root
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# .env is not baked in — inject DATABASE_URL / GOOGLE_SERVER_CLIENT_ID / HUME_* at runtime
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

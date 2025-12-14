FROM python:3.11-slim

WORKDIR /app

# Install OS-level dependencies needed by opencv and media handling
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       gcc \
       libgl1 \
       libglib2.0-0 \
       libsm6 \
       libxext6 \
       ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps first (cached when unchanged)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

EXPOSE 8000

# Use shell form to allow $PORT from the platform; default to 8000 for local runs.
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000} --log-level info"]
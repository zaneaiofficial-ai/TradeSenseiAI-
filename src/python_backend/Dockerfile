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

ENV PORT=8000

# Use exec form to allow $PORT expansion
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "$PORT"]
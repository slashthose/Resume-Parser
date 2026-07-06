FROM python:3.11-slim

# Install Ollama
RUN apt-get update && apt-get install -y curl zstd procps && \
    curl -fsSL https://ollama.com/install.sh | sh && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Pull the model during the BUILD, not on every container start.
# This starts ollama temporarily, downloads the model into the image,
# then stops it -- so at runtime the model is already on disk.
RUN ollama serve & \
    sleep 5 && \
    ollama pull llama3 && \
    (pkill ollama || true)

EXPOSE 8000

# Runtime: both processes start immediately since the model is already local.
# Render/Railway set $PORT at runtime -- fall back to 8000 for local `docker run`.
CMD ollama serve & \
    sleep 3 && \
    uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}

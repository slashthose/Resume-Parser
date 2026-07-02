FROM python:3.11-slim

# Install Ollama
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://ollama.com/install.sh | sh && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Pull the model during the BUILD, not on every container start.
RUN ollama serve & \
    sleep 5 && \
    ollama pull llama3 && \
    (pkill ollama || true)

# Hugging Face Spaces expects the app to listen on 7860 (matches app_port in README.md)
EXPOSE 7860

CMD ollama serve & \
    sleep 3 && \
    uvicorn main:app --host 0.0.0.0 --port 7860

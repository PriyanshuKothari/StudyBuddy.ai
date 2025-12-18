# Dockerfile for Hugging Face Spaces
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY studybuddy/requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download sentence-transformers model (CRITICAL for HF!)
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Copy backend application code
COPY studybuddy/ .

# Create directories
RUN mkdir -p uploads

# Expose Hugging Face port
EXPOSE 7860

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
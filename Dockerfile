# Use Python 3.10 slim as base
FROM python:3.10-slim AS base

# Set working directory
WORKDIR /app

# Install system dependencies and Python packages in one layer
# RUN apt update && \
#     apt install -y --no-install-recommends \
#     curl \
#     wget \
#     && rm -rf /var/lib/apt/lists/* && \
#     pip install --no-cache-dir --upgrade pip wheel setuptools

RUN apt update && \
    apt install -y curl wget \
    pip install --no-cache-dir --upgrade pip wheel setuptools

# Copy requirements and install Python packages
COPY requirements-docker.txt requirements.txt
RUN pip install --no-cache-dir \
    --disable-pip-version-check \
    --only-binary=all \
    -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories and set permissions in one layer
RUN mkdir -p /app/data/vector_db /app/data/cache /app/temp /app/logs /app/nltk_data && \
    groupadd -r appuser && useradd -r -g appuser appuser && \
    chown -R appuser:appuser /app

# Set environment variables
ENV PYTHONPATH=/app
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
ENV NLTK_DATA=/app/nltk_data

# Pre-download NLTK data
RUN python -c "import nltk; nltk.download('punkt', download_dir='/app/nltk_data'); nltk.download('stopwords', download_dir='/app/nltk_data'); nltk.download('wordnet', download_dir='/app/nltk_data')"

# Switch to non-root user
USER appuser

# Expose the port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run Streamlit
CMD ["streamlit", "run", "streamlit_app/chatbot.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true", "--browser.gatherUsageStats=false"] 
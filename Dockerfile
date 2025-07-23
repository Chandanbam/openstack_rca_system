# Complete OpenStack RCA System Dockerfile
# Single comprehensive Dockerfile with all imports, volumes, and directories

FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Upgrade pip and install wheel
RUN pip install --no-cache-dir --upgrade pip wheel

# Copy requirements first for better caching
COPY requirements-docker.txt .

# Install Python dependencies with optimizations
RUN pip install --no-cache-dir \
    --disable-pip-version-check \
    --no-compile \
    -r requirements-docker.txt

# Download NLTK data (required for text processing) - after installing packages
RUN python -c "import nltk; nltk.download('stopwords', download_dir='/app/nltk_data'); nltk.download('punkt', download_dir='/app/nltk_data'); nltk.download('wordnet', download_dir='/app/nltk_data'); nltk.download('omw-1.4', download_dir='/app/nltk_data')"

# Copy ALL application code and directories
COPY main.py .
COPY config/ config/
COPY data/ data/
COPY lstm/ lstm/
COPY models/ models/
COPY logs/ logs/
COPY services/ services/
COPY streamlit_app/ streamlit_app/
COPY utils/ utils/
COPY mlflow_integration/ mlflow_integration/

# Ensure vector DB data is properly copied and accessible
RUN ls -la /app/data/vector_db/ || echo "Vector DB directory created"

# Create necessary directories and set permissions
RUN mkdir -p /app/data/vector_db \
    && mkdir -p /app/data/cache \
    && mkdir -p /app/data/cache/transformers \
    && mkdir -p /app/data/cache/huggingface \
    && mkdir -p /app/temp \
    && mkdir -p /app/logs \
    && mkdir -p /app/models \
    && mkdir -p /app/nltk_data \
    && chmod -R 755 /app

# Note: Vector DB data is copied from data/vector_db/ directory
# Ensure vector DB data exists before building the image

# Set environment variables
ENV PYTHONPATH=/app
ENV NLTK_DATA=/app/nltk_data
ENV TRANSFORMERS_CACHE=/app/data/cache/transformers
ENV HF_HOME=/app/data/cache/huggingface
ENV STREAMLIT_SERVER_PORT=7051
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
ENV ANONYMIZED_TELEMETRY=False
ENV CHROMA_TELEMETRY_ENABLED=False

# Note: MLflow, AWS, and AI API environment variables should be provided at runtime
# via docker run -e, --env-file, or docker-compose environment configuration

# Expose port
EXPOSE 7051

# Create startup script with comprehensive setup
RUN echo '#!/bin/bash' > /app/start.sh && \
    echo 'set -e' >> /app/start.sh && \
    echo 'echo "🚀 Starting OpenStack RCA Streamlit App..."' >> /app/start.sh && \
    echo 'echo "📁 Directories:"' >> /app/start.sh && \
    echo 'echo "   📊 Vector DB: /app/data/vector_db"' >> /app/start.sh && \
    echo 'ls -la /app/data/vector_db/ || echo "Vector DB directory empty"' >> /app/start.sh && \
    echo 'echo "   💾 Cache: /app/data/cache"' >> /app/start.sh && \
    echo 'echo "   🤖 Models: /app/models"' >> /app/start.sh && \
    echo 'echo "   📋 Logs: /app/logs"' >> /app/start.sh && \
    echo 'echo "   🌐 Port: 7051"' >> /app/start.sh && \
    echo 'echo ""' >> /app/start.sh && \
    echo 'echo "🔧 Environment:"' >> /app/start.sh && \
    echo 'echo "   📦 PYTHONPATH: $PYTHONPATH"' >> /app/start.sh && \
    echo 'echo "   🔗 MLflow URI: $MLFLOW_TRACKING_URI"' >> /app/start.sh && \
    echo 'echo "   🤖 AI Provider: Claude"' >> /app/start.sh && \
    echo 'echo "   🌍 Environment: $ENVIRONMENT"' >> /app/start.sh && \
    echo 'echo ""' >> /app/start.sh && \
    echo 'echo "🎯 Starting Streamlit app..."' >> /app/start.sh && \
    echo 'exec streamlit run streamlit_app/chatbot.py --server.port=7051 --server.address=0.0.0.0' >> /app/start.sh && \
    chmod +x /app/start.sh

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Health check using Python
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:7051/_stcore/health')" || exit 1

# Define volumes for persistent data
VOLUME ["/app/data/vector_db", "/app/data/cache", "/app/logs", "/app/models", "/app/temp"]

# Run the startup script
CMD ["/app/start.sh"] 
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for volumes
RUN mkdir -p /app/data/vector_db \
    && mkdir -p /app/data/cache \
    && mkdir -p /app/models \
    && mkdir -p /app/logs \
    && mkdir -p /app/temp

# Set environment variables
ENV PYTHONPATH=/app
ENV STREAMLIT_SERVER_PORT=7051
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Expose the port
EXPOSE 7051

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7051/_stcore/health || exit 1

# Create startup script
RUN echo '#!/bin/bash\n\
echo "🚀 Starting OpenStack RCA Streamlit App..."\n\
echo "📊 Vector DB: /app/data/vector_db"\n\
echo "💾 Cache: /app/data/cache"\n\
echo "🤖 Models: /app/models"\n\
echo "📋 Logs: /app/logs"\n\
echo "🌐 Port: 7051"\n\
echo ""\n\
# Download model from S3 if not present locally\n\
if [ ! -f "/app/models/lstm_log_classifier.keras" ] && [ -n "$MLFLOW_ENABLED" ]; then\n\
    echo "📥 Attempting to download model from S3..."\n\
    python -c "from utils.mlflow_model_manager import MLflowModelManager; MLflowModelManager().download_latest_model()" || echo "⚠️ S3 model download failed, will use local fallback"\n\
fi\n\
echo "🎯 Starting Streamlit app on port 7051..."\n\
exec streamlit run streamlit_app/chatbot.py --server.port=7051 --server.address=0.0.0.0\n\
' > /app/start.sh && chmod +x /app/start.sh

# Run the startup script
CMD ["/app/start.sh"] 
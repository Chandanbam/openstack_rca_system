# Use Python 3.10 slim as base
FROM python:3.10-slim AS base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* \
    && rm -rf /var/tmp/*

# Upgrade pip and install wheel for faster builds
RUN pip install --no-cache-dir --upgrade pip wheel setuptools

# Copy requirements and install Python dependencies first (for better caching)
COPY requirements.txt .

# Install Python dependencies with optimizations
RUN pip install --no-cache-dir \
    --disable-pip-version-check \
    --no-compile \
    -r requirements.txt \
    && pip cache purge \
    && find /usr/local/lib/python3.10 -type d -name __pycache__ -exec rm -rf {} + || true \
    && find /usr/local/lib/python3.10 -name "*.pyc" -delete || true

# Copy application code selectively
COPY main.py .
COPY config/ config/
COPY lstm/ lstm/
COPY services/ services/
COPY streamlit_app/ streamlit_app/
COPY utils/ utils/
COPY monitoring/ monitoring/

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

# ============================================
# Production Stage  
# ============================================
FROM base AS production

# Create a non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Create startup script with proper error handling
COPY <<EOF /app/start.sh
#!/bin/bash
set -e

echo "🚀 Starting OpenStack RCA Streamlit App..."
echo "📊 Vector DB: /app/data/vector_db"
echo "💾 Cache: /app/data/cache" 
echo "🤖 Models: /app/models"
echo "📋 Logs: /app/logs"
echo "🌐 Port: 7051"
echo ""

# Download model from MLflow/S3 if not present locally
if [ ! -f "/app/models/lstm_log_classifier.keras" ] && [ -n "\$MLFLOW_ENABLED" ]; then
    echo "📥 Attempting to download model from MLflow/S3..."
    python -c "
try:
    from utils.mlflow_model_manager import MLflowModelManager
    MLflowModelManager().download_latest_model()
    print('✅ Model downloaded successfully')
except Exception as e:
    print(f'⚠️ Model download failed: {e}')
    print('Will use local fallback if available')
" || echo "⚠️ Model download failed, will use local fallback"
fi

echo "🎯 Starting Streamlit app on port 7051..."
exec streamlit run streamlit_app/chatbot.py --server.port=7051 --server.address=0.0.0.0
EOF

RUN chmod +x /app/start.sh

# Change ownership to appuser
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Run the startup script
CMD ["/app/start.sh"] 
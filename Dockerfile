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
COPY data/ data/
COPY lstm/ lstm/
COPY models/ models/
COPY logs/ logs/
COPY services/ services/
COPY streamlit_app/ streamlit_app/
COPY utils/ utils/
COPY monitoring/ monitoring/
COPY mlflow_integration/ mlflow_integration/

# Create directories for volumes (only for additional directories)
RUN mkdir -p /app/data/vector_db \
    && mkdir -p /app/data/cache \
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
RUN groupadd -r appuser && useradd -r -g appuser appuser \
    && mkdir -p /home/appuser \
    && chown -R appuser:appuser /home/appuser

# Set NLTK data directory to avoid permission issues
ENV NLTK_DATA=/app/nltk_data
RUN mkdir -p /app/nltk_data && chown -R appuser:appuser /app/nltk_data

# Pre-download NLTK data as root to avoid runtime permission issues
RUN python -c "import nltk; nltk.download('punkt', download_dir='/app/nltk_data'); nltk.download('stopwords', download_dir='/app/nltk_data'); nltk.download('wordnet', download_dir='/app/nltk_data')"

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
    from mlflow_integration.mlflow_manager import MLflowManager
    from config.config import Config
    
    # Use the environment's experiment name
    import os
    experiment_name = os.getenv('MLFLOW_EXPERIMENT_NAME', Config.MLFLOW_CONFIG.get('experiment_name', 'openstack_rca_system_production'))
    
    mgr = MLflowManager(
        tracking_uri=Config.MLFLOW_TRACKING_URI,
        experiment_name=experiment_name,
        enable_mlflow=True
    )
    
    if mgr.is_enabled:
        model = mgr.load_model_with_versioning(model_name='lstm_model', version='latest')
        if model:
            print(f'✅ Model downloaded successfully from experiment: {experiment_name}')
        else:
            print(f'⚠️ No model found for experiment: {experiment_name}')
    else:
        print('⚠️ MLflow not enabled')
        
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
# Docker Deployment Documentation

Complete guide for containerizing and deploying the OpenStack RCA System using Docker.

## 🐳 Overview

The OpenStack RCA System is containerized using Docker for consistent deployment across different environments. The Docker setup includes:

- **Multi-stage builds** for optimized image size
- **Model integration** from MLflow artifacts
- **Health checks** for container validation
- **Environment variable** configuration
- **Production-ready** Streamlit application

## 📋 Dockerfile Structure

### **Multi-Stage Build**

```dockerfile
# Stage 1: Base Python environment
FROM python:3.10-slim

# Stage 2: Dependencies installation
COPY requirements-docker.txt .
RUN pip install --no-cache-dir -r requirements-docker.txt

# Stage 3: Application code and models
COPY . /app/
WORKDIR /app

# Stage 4: Production configuration
ENV PYTHONPATH=/app
ENV TF_USE_LEGACY_KERAS=1
ENV CUDA_VISIBLE_DEVICES=-1
```

### **Key Features**

- **Python 3.10**: Stable Python version
- **Slim base image**: Reduced image size
- **Keras 3 compatibility**: Legacy Keras mode for compatibility
- **CPU-only**: Disabled CUDA for cloud deployment
- **Non-root user**: Security best practices

## 🚀 Building the Docker Image

### **Local Build**

```bash
# Build with latest tag
docker build -t openstack-rca-system:latest .

# Build with specific tag
docker build -t openstack-rca-system:v1.0.0 .

# Build with no cache (for clean build)
docker build --no-cache -t openstack-rca-system:latest .
```

### **CI/CD Build**

The CI/CD pipeline automatically builds the image:

```yaml
# From .github/workflows/ci-cd-pipeline.yml
- name: Build and test Docker image
  run: |
    echo "🐳 Building Docker image..."
    docker build -t openstack-rca-system:${{ github.sha }} .
```

### **Model Integration**

The Docker build process includes model integration:

```bash
# Models are copied from MLflow artifacts
COPY models/ models/

# Model files are available at runtime
# - lstm_log_classifier.keras (main model)
# - lstm_log_classifier_info.pkl (model metadata)
```

## 🧪 Testing the Container

### **Local Testing**

```bash
# Run container with environment variables
docker run --rm -d --name test-container -p 8501:8501 \
  -e ANTHROPIC_API_KEY=your_key \
  -e MLFLOW_TRACKING_URI=your_uri \
  -e MLFLOW_ARTIFACT_ROOT=your_s3_bucket \
  openstack-rca-system:latest

# Health check
curl -f http://localhost:8501/_stcore/health

# Stop container
docker stop test-container
```

### **CI/CD Testing**

The pipeline includes automated container testing:

```yaml
# Health check in CI/CD
echo "🔍 Checking container health..."
curl -f http://localhost:8501/_stcore/health || echo "Health check failed"
```

## 📦 Container Configuration

### **Environment Variables**

```bash
# Required for operation
ANTHROPIC_API_KEY=sk-ant-api...
MLFLOW_TRACKING_URI=https://your-mlflow-server.com
MLFLOW_ARTIFACT_ROOT=s3://your-bucket/group6-capstone
MLFLOW_S3_ENDPOINT_URL=https://s3.amazonaws.com

# AWS credentials
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=ap-south-1

# Application configuration
CONTAINER_PORT=8501
DEBUG=false
ENVIRONMENT=production
TF_USE_LEGACY_KERAS=1
CUDA_VISIBLE_DEVICES=-1
```

### **Port Configuration**

```dockerfile
# Expose Streamlit port
EXPOSE 8501

# Default Streamlit configuration
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
```

### **Volume Mounts**

```bash
# For data persistence (optional)
docker run -v /host/data:/app/data openstack-rca-system:latest

# For model updates (optional)
docker run -v /host/models:/app/models openstack-rca-system:latest
```

## 🔧 Production Deployment

### **Docker Compose**

```yaml
# docker-compose.yml
version: '3.8'
services:
  openstack-rca:
    image: openstack-rca-system:latest
    ports:
      - "8501:8501"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - MLFLOW_TRACKING_URI=${MLFLOW_TRACKING_URI}
      - MLFLOW_ARTIFACT_ROOT=${MLFLOW_ARTIFACT_ROOT}
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### **Kubernetes Deployment**

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: openstack-rca
spec:
  replicas: 2
  selector:
    matchLabels:
      app: openstack-rca
  template:
    metadata:
      labels:
        app: openstack-rca
    spec:
      containers:
      - name: openstack-rca
        image: openstack-rca-system:latest
        ports:
        - containerPort: 8501
        env:
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: openstack-rca-secrets
              key: anthropic-api-key
        - name: MLFLOW_TRACKING_URI
          valueFrom:
            configMapKeyRef:
              name: openstack-rca-config
              key: mlflow-tracking-uri
        resources:
          requests:
            memory: "512Mi"
            cpu: "256m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /_stcore/health
            port: 8501
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /_stcore/health
            port: 8501
          initialDelaySeconds: 5
          periodSeconds: 5
```

## 🔍 Monitoring and Health Checks

### **Health Endpoint**

```bash
# Streamlit health check
curl -f http://localhost:8501/_stcore/health

# Expected response: 200 OK
```

### **Container Logs**

```bash
# View container logs
docker logs openstack-rca-container

# Follow logs in real-time
docker logs -f openstack-rca-container

# Logs include:
# - Application startup
# - Model loading status
# - Request processing
# - Error messages
```

### **Resource Monitoring**

```bash
# Container resource usage
docker stats openstack-rca-container

# Process information
docker exec openstack-rca-container ps aux

# Memory usage
docker exec openstack-rca-container free -h
```

## 🚨 Troubleshooting

### **Common Issues**

#### **Container Won't Start**
```bash
# Check container logs
docker logs openstack-rca-container

# Common causes:
# - Missing environment variables
# - Port conflicts
# - Insufficient resources
```

#### **Model Loading Issues**
```bash
# Verify model files exist
docker exec openstack-rca-container ls -la /app/models/

# Check model file permissions
docker exec openstack-rca-container ls -la /app/models/*.keras

# Test model loading
docker exec openstack-rca-container python -c "
from lstm.lstm_classifier import LSTMClassifier
model = LSTMClassifier()
model.load_model('/app/models/lstm_log_classifier.keras')
print('Model loaded successfully')
"
```

#### **Memory Issues**
```bash
# Check memory usage
docker stats openstack-rca-container

# Increase memory limit
docker run --memory=2g openstack-rca-system:latest

# Monitor memory in container
docker exec openstack-rca-container python -c "
import psutil
print(f'Memory usage: {psutil.virtual_memory().percent}%')
"
```

### **Debug Commands**

```bash
# Enter container shell
docker exec -it openstack-rca-container /bin/bash

# Check environment variables
docker exec openstack-rca-container env | grep -E "(MLFLOW|AWS|ANTHROPIC)"

# Verify Python packages
docker exec openstack-rca-container pip list

# Test imports
docker exec openstack-rca-container python -c "
import tensorflow as tf
import mlflow
import streamlit
print('All imports successful')
"
```

## 📊 Performance Optimization

### **Image Size Optimization**

```dockerfile
# Use multi-stage builds
# Remove unnecessary files
# Use .dockerignore
# Optimize layer caching
```

### **Runtime Optimization**

```bash
# Resource limits
docker run --cpus=2 --memory=2g openstack-rca-system:latest

# Volume caching
docker run -v model-cache:/app/models openstack-rca-system:latest

# Network optimization
docker run --network=host openstack-rca-system:latest
```

### **Security Best Practices**

```dockerfile
# Use non-root user
USER appuser

# Minimal base image
FROM python:3.10-slim

# No secrets in image
# Use environment variables or secrets management
```

## 🔄 CI/CD Integration

### **Automated Build and Push**

The CI/CD pipeline automatically:

1. **Builds** Docker image with latest code
2. **Tests** container functionality
3. **Pushes** to Docker Hub
4. **Deploys** to ECS with EC2 launch type

### **Version Tagging**

```bash
# Git SHA tagging
docker tag openstack-rca-system:${{ github.sha }} username/openstack-rca-system:${{ github.sha }}

# Latest tag
docker tag openstack-rca-system:${{ github.sha }} username/openstack-rca-system:latest
```

### **Registry Integration**

```bash
# Docker Hub push
docker push username/openstack-rca-system:${{ github.sha }}
docker push username/openstack-rca-system:latest

# ECR push (alternative)
aws ecr get-login-password --region region | docker login --username AWS --password-stdin account.dkr.ecr.region.amazonaws.com
docker tag openstack-rca-system:latest account.dkr.ecr.region.amazonaws.com/openstack-rca-system:latest
docker push account.dkr.ecr.region.amazonaws.com/openstack-rca-system:latest
```

This Docker deployment setup provides a robust, scalable, and production-ready containerization solution for the OpenStack RCA System. 
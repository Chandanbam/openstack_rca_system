# 🚀 OpenStack RCA System - Docker Deployment Summary

## 📦 What's Created

### 1. Docker Infrastructure
- **Dockerfile**: Multi-stage container build with Python 3.10, port 7051 exposed
- **docker-compose.yml**: Orchestration with volume mounts and environment variables
- **.dockerignore**: Optimized build context excluding unnecessary files

### 2. Build & Deploy Scripts
- **docker_build_deploy.py**: Complete Docker build, tag, and push to DockerHub
- **setup_ec2_deployment.sh**: Automated EC2 setup with Docker installation
- **requirements_deploy.txt**: Minimal deployment dependencies

### 3. Main.py Integration
- **--mode deploy**: New deployment mode in main.py
- **deploy_with_docker()**: Automatic container management function

### 4. Documentation
- **DOCKER_DEPLOYMENT.md**: Comprehensive deployment guide
- **DEPLOYMENT_SUMMARY.md**: This summary document

## 🔄 Complete Workflow

### Step 1: Build and Push Docker Image
```bash
# Configure credentials (one-time setup)
cp env.template .env
nano .env  # Set your DOCKER_USERNAME and DOCKER_PASSWORD

# Build and push to DockerHub (uses env/config automatically)
python docker_build_deploy.py

# This automatically:
# ✅ Loads Docker credentials from .envrc/config.py
# ✅ Builds Docker image with all dependencies  
# ✅ Tags with version and 'latest'
# ✅ Pushes to DockerHub
# ✅ Updates config.py with image details
# ✅ Creates config/docker_config.json
```

### Step 2: Deploy Locally
```bash
# Simple deployment
python main.py --mode deploy

# This automatically:
# ✅ Pulls latest image from DockerHub
# ✅ Stops existing container (if any)
# ✅ Creates volume mounts for data persistence
# ✅ Starts container on port 7051
# ✅ Passes environment variables
# ✅ Sets up health checks and restart policies
```

### Step 3: Deploy on EC2
```bash
# Setup EC2 instance (run once)
wget https://raw.githubusercontent.com/your-repo/openstack-rca-system/main/setup_ec2_deployment.sh
chmod +x setup_ec2_deployment.sh
./setup_ec2_deployment.sh

# Deploy application
cd ~/openstack-rca-system
cp .env.template .env
# Edit .env with your API keys
python3 main.py --mode deploy
```

## 📁 Volume Mounts & Data Persistence

The Docker container automatically mounts these directories:

```bash
Host Directory          → Container Directory     Purpose
./data/vector_db       → /app/data/vector_db    ChromaDB database
./data/cache           → /app/data/cache        Cached log processing
./models              → /app/models            LSTM model files
./logs                → /app/logs              Application logs
./temp                → /app/temp              S3 downloads
```

## 🌐 Environment Variables

Required in `.env` file or environment:

```env
# Essential
ANTHROPIC_API_KEY=your_key_here

# MLflow (Optional)
MLFLOW_TRACKING_URI=https://your-mlflow-server.com
MLFLOW_ARTIFACT_ROOT=s3://your-bucket/mlflow
MLFLOW_S3_ENDPOINT_URL=https://s3.region.amazonaws.com
MLFLOW_ENABLED=true

# AWS (Optional)
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_DEFAULT_REGION=your_region
```

## 🔧 Container Features

### Automatic Capabilities
- ✅ **Port 7051**: Streamlit app accessible
- ✅ **Health Checks**: Automatic restart if unhealthy
- ✅ **S3 Model Loading**: Downloads models from S3 if available
- ✅ **Volume Persistence**: Data survives container restarts
- ✅ **Environment Pass-through**: All required env vars passed
- ✅ **Restart Policy**: "unless-stopped" for reliability

### Startup Process
1. Container starts and checks for mounted volumes
2. Downloads model from S3 if configured and not present locally
3. Initializes ChromaDB with existing data
4. Starts Streamlit app on port 7051
5. Health check endpoint available at `/_stcore/health`

## 🎯 Usage Examples

### Local Development
```bash
# Build image
python docker_build_deploy.py -u myusername

# Deploy locally
python main.py --mode deploy

# Access app
open http://localhost:7051
```

### Production Deployment
```bash
# Setup EC2 (t3.large or larger)
./setup_ec2_deployment.sh

# Configure environment
cp .env.template .env
nano .env  # Add your API keys

# Deploy
python3 main.py --mode deploy

# Monitor
docker logs -f openstack-rca-system
```

### CI/CD Integration
```bash
# In your CI/CD pipeline
python docker_build_deploy.py -u $DOCKER_USERNAME -p $DOCKER_PASSWORD -v $BUILD_VERSION

# On deployment server
docker pull username/openstack-rca-system:$BUILD_VERSION
python main.py --mode deploy
```

## 🛠️ Container Management

### Using main.py (Recommended)
```bash
python main.py --mode deploy     # Deploy/update
docker logs -f openstack-rca-system  # View logs
docker stop openstack-rca-system     # Stop
```

### Using Docker Compose
```bash
docker-compose up -d             # Start
docker-compose logs -f           # View logs
docker-compose restart           # Restart
docker-compose down              # Stop
```

### Direct Docker Commands
```bash
docker run -d --name openstack-rca-system \
  -p 7051:7051 \
  -v $(pwd)/data/vector_db:/app/data/vector_db \
  -v $(pwd)/models:/app/models \
  --env-file .env \
  username/openstack-rca-system:latest
```

## 📊 Monitoring & Health

### Health Checks
- **Endpoint**: `http://localhost:7051/_stcore/health`
- **Automatic**: Every 30 seconds
- **Restart**: Automatic if unhealthy

### Log Monitoring
```bash
# Real-time logs
docker logs -f openstack-rca-system

# Container stats
docker stats openstack-rca-system

# Application health
curl http://localhost:7051/_stcore/health
```

## ⚡ Performance & Resource Usage

### Recommended Resources
- **Development**: 2 CPU, 4GB RAM
- **Production**: 4 CPU, 8GB RAM
- **High Load**: 8 CPU, 16GB RAM

### Optimization
- Uses Python 3.10-slim base image
- Multi-stage build for smaller final image
- Cached layers for faster builds
- Volume mounts for data persistence
- Health checks for reliability

## 🔒 Security Features

- Non-root user execution
- Environment variable isolation
- No sensitive data in image
- Resource limits configurable
- Automatic restart policies
- Health check monitoring

## 🚀 Quick Commands Reference

```bash
# Build and push image
python docker_build_deploy.py -u username

# Deploy container
python main.py --mode deploy

# View logs
docker logs -f openstack-rca-system

# Update application
docker-compose pull && docker-compose up -d

# Backup data
tar -czf backup.tar.gz data/ models/

# Access application
curl http://localhost:7051/_stcore/health
open http://localhost:7051
```

## ✅ Verification Checklist

After deployment, verify:
- [ ] Container is running: `docker ps`
- [ ] Health check passing: `curl localhost:7051/_stcore/health`
- [ ] App accessible: `open http://localhost:7051`
- [ ] Logs showing no errors: `docker logs openstack-rca-system`
- [ ] Data directories mounted: `docker exec -it openstack-rca-system ls -la /app/data`
- [ ] Environment variables loaded: `docker exec -it openstack-rca-system env | grep API`

## 🎉 Success!

Your OpenStack RCA System is now fully containerized and ready for deployment anywhere Docker runs!

- **Local Development**: Fast iteration with `python main.py --mode deploy`
- **Production**: Reliable deployment on EC2 with automatic restarts
- **Scalable**: Easy to replicate across multiple instances
- **Maintainable**: Version controlled with automated builds 
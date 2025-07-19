# Docker Deployment Guide for OpenStack RCA System

This guide covers how to deploy the OpenStack RCA System using Docker containers.

## 🚀 Quick Start

### Option 1: Using main.py (Recommended)
```bash
# Deploy the latest container
python main.py --mode deploy
```

### Option 2: Using Docker Compose
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 📋 Prerequisites

### Local Development
- Docker installed and running
- Python 3.10+
- Required Python packages: `pip install -r requirements_deploy.txt`

### EC2 Deployment
- EC2 instance (t3.large or higher recommended)
- Ubuntu 20.04+ / Amazon Linux 2 / CentOS 8+
- At least 4GB RAM and 20GB disk space

## 🔧 EC2 Setup

### Automated Setup
```bash
# Download and run the setup script
wget https://raw.githubusercontent.com/your-repo/openstack-rca-system/main/setup_ec2_deployment.sh
chmod +x setup_ec2_deployment.sh
./setup_ec2_deployment.sh
```

### Manual Setup
```bash
# Install Docker
sudo yum update -y
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Python requirements
pip3 install --user docker python-dotenv boto3 requests
```

## 🏗️ Building and Publishing Docker Image

### Build Locally
```bash
# Build using credentials from .envrc and config.py
python docker_build_deploy.py

# This will:
# 1. Load Docker credentials from environment/config
# 2. Build the Docker image
# 3. Push to DockerHub
# 4. Update config.py with image details
```

### Build Options
```bash
# Override with command line arguments
python docker_build_deploy.py -u username -r custom-repo-name

# Specific version tag
python docker_build_deploy.py -v v1.0.0

# With password (otherwise uses env/config or prompts)
python docker_build_deploy.py -p your_password

# All arguments are now optional - defaults come from:
# 1. Environment variables (.envrc)
# 2. Config.py DOCKER_CONFIG
# 3. Command line arguments (override)
# 4. User prompt (fallback)
```

## 🌐 Environment Configuration

### Required Environment Variables
Create a `.env` file or set environment variables:

```env
# Required for RCA analysis
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Docker Registry (for building/pushing images)
DOCKER_USERNAME=your_dockerhub_username
DOCKER_PASSWORD=your_dockerhub_password
DOCKER_REGISTRY=docker.io
DOCKER_REPOSITORY=openstack-rca-system

# Optional: MLflow integration
MLFLOW_TRACKING_URI=https://your-mlflow-server.com
MLFLOW_ARTIFACT_ROOT=s3://your-bucket/mlflow-artifacts
MLFLOW_S3_ENDPOINT_URL=https://s3.your-region.amazonaws.com
MLFLOW_ENABLED=true

# Optional: AWS for S3 model storage
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_DEFAULT_REGION=your-aws-region
```

### Environment Setup
```bash
# Option 1: Copy from template
cp env.template .env
nano .env  # Edit with your credentials

# Option 2: Use direnv (loads .envrc automatically)
# Your .envrc already includes Docker configuration
```

## 📁 Volume Mounts

The container automatically mounts the following directories:

| Local Path | Container Path | Purpose |
|------------|---------------|---------|
| `./data/vector_db` | `/app/data/vector_db` | ChromaDB vector database |
| `./data/cache` | `/app/data/cache` | Cached log processing |
| `./models` | `/app/models` | LSTM model files |
| `./logs` | `/app/logs` | Application and OpenStack logs |
| `./temp` | `/app/temp` | Temporary files and S3 downloads |

## 🐳 Container Management

### Using main.py
```bash
# Deploy latest container
python main.py --mode deploy

# This automatically:
# - Pulls latest image from DockerHub
# - Stops existing container
# - Creates new container with proper mounts
# - Starts the service on port 7051
```

### Using Docker Commands
```bash
# Pull latest image
docker pull chandanbam/openstack-rca-system:latest

# Run container
docker run -d \
  --name openstack-rca-system \
  -p 7051:7051 \
  -v $(pwd)/data/vector_db:/app/data/vector_db \
  -v $(pwd)/data/cache:/app/data/cache \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/temp:/app/temp \
  --env-file .env \
  --restart unless-stopped \
  chandanbam/openstack-rca-system:latest

# View logs
docker logs -f openstack-rca-system

# Stop container
docker stop openstack-rca-system

# Remove container
docker rm openstack-rca-system
```

### Using Docker Compose
```bash
# Start services in background
docker-compose up -d

# View logs
docker-compose logs -f openstack-rca-system

# Restart services
docker-compose restart

# Stop and remove
docker-compose down

# Update and restart
docker-compose pull && docker-compose up -d
```

## 🔍 Monitoring and Troubleshooting

### Health Checks
The container includes automatic health checks:
- **Endpoint**: `http://localhost:7051/_stcore/health`
- **Interval**: 30 seconds
- **Timeout**: 10 seconds
- **Start period**: 60 seconds

### Log Monitoring
```bash
# Container logs
docker logs -f openstack-rca-system

# Application logs (if mounted)
tail -f logs/app.log

# Real-time container stats
docker stats openstack-rca-system
```

### Common Issues

#### Port Already in Use
```bash
# Find process using port 7051
sudo lsof -i :7051
# or
sudo netstat -tulpn | grep :7051

# Kill the process and restart container
```

#### Container Won't Start
```bash
# Check container status
docker ps -a

# Check logs for errors
docker logs openstack-rca-system

# Remove and recreate container
docker rm -f openstack-rca-system
python main.py --mode deploy
```

#### Model Not Loading
```bash
# Check if model exists locally
ls -la models/

# Check S3 connectivity (if using MLflow)
docker exec -it openstack-rca-system python -c "import boto3; print(boto3.client('s3').list_buckets())"

# Download model manually
docker exec -it openstack-rca-system python -c "from utils.mlflow_model_manager import MLflowModelManager; MLflowModelManager().download_latest_model()"
```

## 🔒 Security Considerations

### Production Deployment
- Use specific version tags instead of `latest` in production
- Set proper resource limits in docker-compose.yml
- Use Docker secrets for sensitive environment variables
- Run containers as non-root user
- Enable Docker daemon security features

### Firewall Configuration
```bash
# Allow port 7051 (Ubuntu/Debian)
sudo ufw allow 7051

# Allow port 7051 (CentOS/RHEL)
sudo firewall-cmd --permanent --add-port=7051/tcp
sudo firewall-cmd --reload
```

## ⚡ Performance Optimization

### Resource Limits
Adjust in `docker-compose.yml`:
```yaml
deploy:
  resources:
    limits:
      memory: 4G
      cpus: '2.0'
    reservations:
      memory: 2G
      cpus: '1.0'
```

### Recommended Instance Sizes
- **Development**: t3.large (2 vCPU, 8GB RAM)
- **Production**: t3.xlarge (4 vCPU, 16GB RAM)
- **High Load**: c5.2xlarge (8 vCPU, 16GB RAM)

## 📊 Accessing the Application

Once deployed, access the application at:
- **Local**: http://localhost:7051
- **EC2**: http://YOUR_EC2_PUBLIC_IP:7051

### Features Available
- ✅ Interactive RCA analysis with Streamlit UI
- ✅ Vector database search for similar issues
- ✅ LSTM-based log classification
- ✅ Model loading from S3 (if configured)
- ✅ Real-time log processing
- ✅ Comprehensive error analysis

## 🆘 Getting Help

### Documentation
- Main README: `README.md`
- MLflow Integration: `docs/MLFLOW_INTEGRATION.md`
- Vector Database: `docs/VECTOR_DB_OPERATIONS.md`
- Cache Management: `docs/CACHE_OPERATIONS.md`

### Support
- Check logs: `docker logs -f openstack-rca-system`
- GitHub Issues: [Create an issue](https://github.com/your-repo/openstack-rca-system/issues)
- Container stats: `docker stats openstack-rca-system`

## 🔄 Updates and Maintenance

### Updating the Application
```bash
# Pull latest image and restart
docker-compose pull && docker-compose up -d

# Or using main.py
python main.py --mode deploy
```

### Backup Important Data
```bash
# Backup vector database
tar -czf vector_db_backup_$(date +%Y%m%d).tar.gz data/vector_db/

# Backup models
tar -czf models_backup_$(date +%Y%m%d).tar.gz models/

# Backup cache
tar -czf cache_backup_$(date +%Y%m%d).tar.gz data/cache/
```

This completes the Docker deployment setup! 🎉 
#!/bin/bash

# EC2 Deployment Setup Script for OpenStack RCA System
# This script installs Docker and required packages on an EC2 instance

set -e  # Exit on any error

echo "🚀 Setting up EC2 instance for OpenStack RCA System deployment..."

# Detect the Linux distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    VERSION=$VERSION_ID
else
    echo "❌ Cannot detect Linux distribution"
    exit 1
fi

echo "✅ Detected OS: $OS $VERSION"

# Update package manager
echo "📦 Updating package manager..."
case $OS in
    ubuntu|debian)
        sudo apt update -y
        INSTALL_CMD="sudo apt install -y"
        DOCKER_COMPOSE_CMD="sudo curl -L \"https://github.com/docker/compose/releases/download/v2.24.1/docker-compose-\$(uname -s)-\$(uname -m)\" -o /usr/local/bin/docker-compose"
        ;;
    amzn|amazon)
        sudo yum update -y
        INSTALL_CMD="sudo yum install -y"
        # Amazon Linux 2 uses docker-compose from extras
        DOCKER_COMPOSE_CMD="sudo yum install -y docker-compose"
        ;;
    centos|rhel|fedora)
        sudo yum update -y
        INSTALL_CMD="sudo yum install -y"
        DOCKER_COMPOSE_CMD="sudo curl -L \"https://github.com/docker/compose/releases/download/v2.24.1/docker-compose-\$(uname -s)-\$(uname -m)\" -o /usr/local/bin/docker-compose"
        ;;
    *)
        echo "❌ Unsupported OS: $OS"
        exit 1
        ;;
esac

# Install essential packages
echo "📦 Installing essential packages..."
$INSTALL_CMD curl wget git python3 python3-pip unzip

# Install Docker
echo "🐳 Installing Docker..."
case $OS in
    ubuntu|debian)
        # Install Docker using official Docker repository
        curl -fsSL https://download.docker.com/linux/$OS/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
        echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/$OS $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
        sudo apt update -y
        $INSTALL_CMD docker-ce docker-ce-cli containerd.io
        ;;
    amzn|amazon)
        $INSTALL_CMD docker
        ;;
    centos|rhel|fedora)
        $INSTALL_CMD docker
        ;;
esac

# Start and enable Docker
echo "🔧 Configuring Docker..."
sudo systemctl start docker
sudo systemctl enable docker

# Add current user to docker group (requires logout/login to take effect)
sudo usermod -aG docker $USER

# Install Docker Compose
echo "📦 Installing Docker Compose..."
eval $DOCKER_COMPOSE_CMD

# Make docker-compose executable
if [ -f /usr/local/bin/docker-compose ]; then
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Test Docker installation
echo "🧪 Testing Docker installation..."
sudo docker --version
sudo docker run --rm hello-world

# Install Python deployment requirements
echo "🐍 Installing Python deployment requirements..."
pip3 install --user --upgrade pip

# Create requirements file if it doesn't exist
if [ ! -f requirements_deploy.txt ]; then
    echo "📝 Creating requirements_deploy.txt..."
    cat > requirements_deploy.txt << EOF
# EC2 Deployment Requirements
docker>=6.1.0
python-dotenv>=1.0.0
boto3>=1.28.0
click>=8.1.0
requests>=2.31.0
awscli>=1.29.0
psutil>=5.9.0
pyyaml>=6.0.0
toml>=0.10.2
netifaces>=0.11.0
supervisor>=4.2.5
EOF
fi

pip3 install --user -r requirements_deploy.txt

# Create project directory
PROJECT_DIR="$HOME/openstack-rca-system"
echo "📁 Creating project directory: $PROJECT_DIR"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# Create data directories
echo "📁 Creating data directories..."
mkdir -p data/vector_db data/cache models logs temp

# Create environment file template
echo "📄 Creating environment file template..."
cat > .env.template << EOF
# OpenStack RCA System Environment Configuration

# Anthropic API Key (required for RCA analysis)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# MLflow Configuration (optional)
MLFLOW_TRACKING_URI=https://your-mlflow-server.com
MLFLOW_ARTIFACT_ROOT=s3://your-bucket/mlflow-artifacts
MLFLOW_S3_ENDPOINT_URL=https://s3.your-region.amazonaws.com
MLFLOW_ENABLED=true

# AWS Configuration (optional, for S3 model storage)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_DEFAULT_REGION=your-aws-region

# Container Configuration
DOCKER_IMAGE=chandanbam/openstack-rca-system:latest
CONTAINER_PORT=7051
EOF

# Create main.py minimal version for deployment
echo "📄 Creating deployment script..."
cat > main.py << 'EOF'
#!/usr/bin/env python3
"""
Minimal deployment script for OpenStack RCA System
Downloads and runs the full system via Docker
"""

import os
import sys
import subprocess
import argparse
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def deploy_with_docker():
    """Deploy using docker-compose"""
    logger.info("🚀 Deploying OpenStack RCA System...")
    
    # Check if docker-compose exists
    compose_file = "docker-compose.yml"
    if not os.path.exists(compose_file):
        logger.info("📄 Creating docker-compose.yml...")
        create_docker_compose()
    
    # Load environment variables
    if os.path.exists('.env'):
        logger.info("✅ Loading environment from .env file")
    else:
        logger.warning("⚠️ No .env file found. Using .env.template as reference")
    
    try:
        # Pull latest image and start services
        subprocess.run(['docker-compose', 'pull'], check=True)
        subprocess.run(['docker-compose', 'up', '-d'], check=True)
        
        logger.info("✅ Deployment successful!")
        logger.info("🌐 Access the app at: http://localhost:7051")
        logger.info("📊 View logs: docker-compose logs -f")
        logger.info("🛑 Stop services: docker-compose down")
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Deployment failed: {e}")
        return False
    
    return True

def create_docker_compose():
    """Create docker-compose.yml file"""
    compose_content = '''version: '3.8'

services:
  openstack-rca-system:
    image: chandanbam/openstack-rca-system:latest
    container_name: openstack-rca-system
    ports:
      - "7051:7051"
    volumes:
      - ./data/vector_db:/app/data/vector_db
      - ./data/cache:/app/data/cache
      - ./models:/app/models
      - ./logs:/app/logs
      - ./temp:/app/temp
    env_file:
      - .env
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:7051/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
'''
    
    with open('docker-compose.yml', 'w') as f:
        f.write(compose_content)

def main():
    parser = argparse.ArgumentParser(description='OpenStack RCA System Deployment')
    parser.add_argument('--mode', choices=['deploy'], default='deploy')
    args = parser.parse_args()
    
    if args.mode == 'deploy':
        deploy_with_docker()

if __name__ == "__main__":
    main()
EOF

chmod +x main.py

echo ""
echo "🎉 EC2 setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Copy your environment variables to .env (use .env.template as reference)"
echo "2. Run: python3 main.py --mode deploy"
echo ""
echo "⚠️ Important notes:"
echo "- You need to logout and login again for Docker group membership to take effect"
echo "- Or run: newgrp docker"
echo "- Make sure to configure your .env file with required API keys"
echo ""
echo "🌐 The app will be available at: http://localhost:7051"
echo "📊 View logs with: docker-compose logs -f"
echo "🛑 Stop with: docker-compose down"
echo "" 
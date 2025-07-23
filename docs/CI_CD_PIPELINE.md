# CI/CD Pipeline Documentation

Complete guide for the OpenStack RCA System continuous integration and deployment pipeline.

## 🚀 Overview

The CI/CD pipeline automates the entire development lifecycle from code commit to production deployment with four comprehensive stages:

```
Code Commit → Train & MLflow → Test RCA & RAG → Docker Build & Push → ECS/EC2 Deploy
```

## 📋 Pipeline Stages

### **Stage 1: Train & MLflow** 🤖
**Trigger**: Every commit to `main` or `deploy` branches

**Actions**:
- ✅ LSTM model training with Keras 3 compatibility
- ✅ MLflow experiment setup and tracking
- ✅ S3 model storage and versioning
- ✅ Model artifact upload for Docker build
- ✅ Environment variable configuration

**Artifacts**:
- Trained LSTM model (`.keras` format)
- MLflow experiment metadata
- Model artifacts for Docker build
- Training logs and metrics

### **Stage 2: Test RCA & RAG** 🧪
**Trigger**: After successful Stage 1

**Actions**:
- ✅ RCA evaluation tests with real scenarios
- ✅ RAG system testing and validation
- ✅ Performance metrics calculation (MRR, accuracy)
- ✅ Continue-on-error for development workflow
- ✅ Test results summary and reporting

**Artifacts**:
- Test results and coverage reports
- Performance metrics (MRR, accuracy scores)
- RCA evaluation reports
- Test artifacts for debugging

### **Stage 3: Docker Build & Push** 🐳
**Trigger**: After successful Stage 2

**Actions**:
- ✅ Multi-stage Docker image build
- ✅ Model integration from MLflow artifacts
- ✅ Container health testing
- ✅ Docker Hub image push with versioning
- ✅ Local container validation

**Artifacts**:
- Docker image with latest model
- Container health status
- Build logs and validation results
- Pushed image to Docker Hub

### **Stage 4: ECS/EC2 Deployment** ☁️
**Trigger**: After successful Stage 3

**Actions**:
- ✅ AWS ECS cluster creation with EC2 launch type
- ✅ Auto Scaling Group with Launch Template
- ✅ ECS service deployment with load balancing
- ✅ Health monitoring and status reporting
- ✅ Production endpoint configuration

**Artifacts**:
- ECS cluster and service status
- EC2 instance details and endpoints
- Deployment summary and metrics
- Production service URLs

## 🔧 Configuration

### **GitHub Secrets Required**

Set these secrets in your GitHub repository settings:

```bash
# API Keys
ANTHROPIC_API_KEY=sk-ant-api...

# MLflow Configuration
MLFLOW_TRACKING_URI=https://your-mlflow-server.com
MLFLOW_ARTIFACT_ROOT=s3://your-bucket/group6-capstone
MLFLOW_S3_ENDPOINT_URL=https://s3.amazonaws.com

# AWS Credentials
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=ap-south-1

# Docker Hub
DOCKER_USERNAME=your_username
DOCKER_PASSWORD=your_password

# ECS/EC2 Deployment
EC2_KEY_NAME=your-ec2-key-pair
ECS_SECURITY_GROUP_IDS=sg-xxxxxxxxx
ECS_SUBNET_IDS=subnet-xxxxxxxxx
```

### **Environment Variables**

The pipeline uses these configurable environment variables:

```yaml
# Core Configuration
PYTHON_VERSION: '3.10'
MLFLOW_EXPERIMENT_NAME: 'openstack_rca_system_prod'
DOCKER_IMAGE: 'openstack-rca-system'

# ECS Configuration
ECS_CLUSTER: 'openstack-rca-cluster'
ECS_SERVICE: 'openstack-rca-service'
ECS_CPU: '256'
ECS_MEMORY: '512'
ECS_CONTAINER_PORT: '7051'
ECS_DESIRED_COUNT: '1'

# EC2 Configuration (Configurable)
EC2_INSTANCE_TYPE: 't2.micro'        # Instance type (t2.micro, t3.small, etc.)
EC2_AMI_ID: 'ami-0c02fb55956c7d316'  # Amazon Machine Image ID
EC2_VOLUME_SIZE: '30'                # EBS volume size in GB
EC2_VOLUME_TYPE: 'gp3'               # EBS volume type (gp3, gp2, io1)

# MLflow Configuration
MLFLOW_TRACKING_URI: ${{ secrets.MLFLOW_TRACKING_URI }}
MLFLOW_ARTIFACT_ROOT: ${{ secrets.MLFLOW_ARTIFACT_ROOT }}
MLFLOW_S3_ENDPOINT_URL: ${{ secrets.MLFLOW_S3_ENDPOINT_URL }}

# AWS Configuration
AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
AWS_DEFAULT_REGION: ${{ secrets.AWS_DEFAULT_REGION }}

# AI Configuration
ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}

# Docker Configuration
DOCKER_USERNAME: ${{ secrets.DOCKER_USERNAME }}
DOCKER_PASSWORD: ${{ secrets.DOCKER_PASSWORD }}
```

### **EC2 Instance Configuration**

The pipeline supports configurable EC2 instances for different environments:

#### **Development (Cost-Effective)**
```yaml
EC2_INSTANCE_TYPE: 't2.micro'    # $8.47/month
EC2_VOLUME_SIZE: '20'            # 20 GB
EC2_VOLUME_TYPE: 'gp3'           # General Purpose
```

#### **Staging (Balanced)**
```yaml
EC2_INSTANCE_TYPE: 't3.small'    # $14.63/month
EC2_VOLUME_SIZE: '30'            # 30 GB
EC2_VOLUME_TYPE: 'gp3'           # General Purpose
```

#### **Production (Performance)**
```yaml
EC2_INSTANCE_TYPE: 't3.medium'   # $29.25/month
EC2_VOLUME_SIZE: '50'            # 50 GB
EC2_VOLUME_TYPE: 'gp3'           # General Purpose
```

#### **Available Instance Types**
```yaml
# T2/T3 Series (Burstable Performance)
EC2_INSTANCE_TYPE: 't2.micro'    # 1 vCPU, 1 GB RAM
EC2_INSTANCE_TYPE: 't2.small'    # 1 vCPU, 2 GB RAM
EC2_INSTANCE_TYPE: 't3.small'    # 2 vCPU, 2 GB RAM
EC2_INSTANCE_TYPE: 't3.medium'   # 2 vCPU, 4 GB RAM
EC2_INSTANCE_TYPE: 't3.large'    # 2 vCPU, 8 GB RAM

# M5/M6 Series (General Purpose)
EC2_INSTANCE_TYPE: 'm5.large'    # 2 vCPU, 8 GB RAM
EC2_INSTANCE_TYPE: 'm6g.medium'  # 1 vCPU, 4 GB RAM (ARM)
```

#### **Available Volume Types**
```yaml
EC2_VOLUME_TYPE: 'gp3'    # General Purpose SSD (recommended)
EC2_VOLUME_TYPE: 'gp2'    # General Purpose SSD (legacy)
EC2_VOLUME_TYPE: 'io1'    # Provisioned IOPS SSD (high performance)
EC2_VOLUME_TYPE: 'st1'    # Throughput Optimized HDD
EC2_VOLUME_TYPE: 'sc1'    # Cold HDD (lowest cost)
``` 
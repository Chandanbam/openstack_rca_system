# CI/CD Pipeline Documentation

Complete guide for the OpenStack RCA System continuous integration and deployment pipeline.

## 🚀 Overview

The CI/CD pipeline automates the entire development lifecycle from code commit to production deployment:

```
Code Commit → Test & Train → MLflow Deploy → Docker Build → ECS Deploy
```

## 📋 Pipeline Stages

### 1. Test & Train Stage
**Trigger**: Every commit to `main` or `develop` branches

**Actions**:
- ✅ Unit tests with pytest
- ✅ Model training with MLflow integration
- ✅ Performance validation
- ✅ Coverage reporting
- ✅ Integration tests

**Artifacts**:
- Test coverage reports
- Trained model files
- Performance metrics

### 2. MLflow Deploy Stage
**Trigger**: Only on `main` branch after successful test stage

**Actions**:
- ✅ Model versioning and registration
- ✅ S3 artifact upload
- ✅ MLflow experiment tracking
- ✅ Model deployment verification

**Artifacts**:
- Versioned model in S3
- MLflow experiment metadata
- Model registry entries

### 3. Docker Build Stage
**Trigger**: Only on `main` branch after successful MLflow deploy

**Actions**:
- ✅ Docker image build
- ✅ Container health testing
- ✅ Image validation
- ✅ Docker Hub push (placeholder)

**Artifacts**:
- Docker image with latest model
- Container health status
- Build logs

### 4. ECS Deploy Stage
**Trigger**: Only on `main` branch after successful Docker build

**Actions**:
- ⏳ AWS ECS deployment (placeholder)
- ⏳ Load balancer configuration
- ⏳ Auto-scaling setup
- ⏳ Health monitoring

**Artifacts**:
- Deployment status
- Service endpoints
- Monitoring metrics

## 🔧 Configuration

### GitHub Secrets Required

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

# Docker Hub (for future implementation)
DOCKER_USERNAME=your_username
DOCKER_PASSWORD=your_password
```

### Environment Variables

The pipeline uses these environment variables:

```yaml
env:
  PYTHON_VERSION: '3.10'
  MLFLOW_EXPERIMENT_NAME: 'openstack_rca_system_staging'
  DOCKER_IMAGE: 'openstack-rca-system'
  ECS_CLUSTER: 'openstack-rca-cluster'
  ECS_SERVICE: 'openstack-rca-service'
```

## 🧪 Testing Strategy

### Unit Tests
```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ -v --cov=. --cov-report=html

# Run specific test file
python -m pytest tests/test_inference.py -v
```

### Test Categories

1. **Model Inference Tests** (`tests/test_inference.py`)
   - Model loading validation
   - Prediction shape verification
   - Performance metrics
   - Input validation

2. **MLflow Integration Tests**
   - Manager initialization
   - Model versioning
   - S3 connectivity

3. **Configuration Tests**
   - Parameter validation
   - Environment loading
   - Default values

### Test Coverage Requirements

- **Minimum Coverage**: 80%
- **Critical Paths**: 95%
- **Model Components**: 90%

## 📦 Model Deployment

### MLflow Integration

The pipeline automatically:

1. **Trains** the LSTM model with latest data
2. **Versions** the model with incremental numbering
3. **Uploads** to S3 with meaningful folder names
4. **Registers** in MLflow model registry
5. **Verifies** deployment success

### S3 Organization

```
s3://your-bucket/group6-capstone/
├── openstack-rca-system-prod_0001/
│   └── models/lstm_model_v1.keras
├── openstack-rca-system-prod_0002/
│   └── models/lstm_model_v2.keras
└── openstack-rca-system-prod_vXXX/
    └── models/lstm_model_vXXX.keras
```

### Model Verification

```python
# Verify model deployment
from mlflow_integration.mlflow_manager import MLflowManager

mgr = MLflowManager(
    tracking_uri=Config.MLFLOW_TRACKING_URI,
    experiment_name='openstack_rca_system_staging'
)

if mgr.is_enabled:
    model = mgr.load_model_with_versioning(
        model_name='lstm_model', 
        version='latest'
    )
    if model:
        print('✅ Model successfully deployed')
```

## 🐳 Docker Integration

### Build Process

1. **Multi-stage build** for optimized image size
2. **Dependency caching** for faster builds
3. **Health checks** for container validation
4. **Environment variable** injection

### Image Testing

```bash
# Build image
python utils/docker_build_deploy.py

# Test container
docker run --rm -d --name test-container -p 7051:7051 \
  -e ANTHROPIC_API_KEY=your_key \
  your-username/openstack-rca-system:latest

# Health check
curl -f http://localhost:7051/_stcore/health

# Stop container
docker stop test-container
```

### Container Features

- **Port 7051**: Streamlit application
- **Volume mounts**: Data persistence
- **Health endpoint**: `/_stcore/health`
- **Auto-restart**: Unless-stopped policy
- **Resource limits**: Configurable CPU/memory

## ☁️ AWS ECS Deployment (Future)

### Planned Implementation

1. **ECS Cluster Creation**
   ```bash
   aws ecs create-cluster --cluster-name openstack-rca-cluster
   ```

2. **Task Definition**
   ```json
   {
     "family": "openstack-rca-task",
     "networkMode": "awsvpc",
     "requiresCompatibilities": ["FARGATE"],
     "cpu": "1024",
     "memory": "2048",
     "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole"
   }
   ```

3. **Service Creation**
   ```bash
   aws ecs create-service \
     --cluster openstack-rca-cluster \
     --service-name openstack-rca-service \
     --task-definition openstack-rca-task
   ```

### Deployment Strategy

- **Blue-Green Deployment**: Zero-downtime updates
- **Auto-scaling**: Based on CPU/memory usage
- **Load balancing**: Application Load Balancer
- **Health monitoring**: CloudWatch integration

## 🔍 Monitoring & Observability

### Pipeline Metrics

- **Build time**: Target < 15 minutes
- **Test coverage**: Minimum 80%
- **Model accuracy**: Minimum 85%
- **Deployment success rate**: Target 99%

### Logging

- **GitHub Actions**: Step-by-step execution logs
- **MLflow**: Training metrics and artifacts
- **Docker**: Container build and runtime logs
- **AWS CloudWatch**: ECS service logs (future)

### Alerts

- **Pipeline failures**: Immediate notification
- **Test coverage drops**: Warning threshold
- **Model performance degradation**: Alert on accuracy < 80%
- **Deployment issues**: Service health monitoring

## 🛠️ Local Development

### Running Pipeline Locally

```bash
# 1. Run tests
python -m pytest tests/ -v --cov=. --cov-report=html

# 2. Train model
python main.py --mode train --enable-mlflow

# 3. Build Docker image
python utils/docker_build_deploy.py

# 4. Test container
docker run --rm -p 7051:7051 your-username/openstack-rca-system:latest
```

### Development Workflow

1. **Feature Branch**: Create feature branch from `develop`
2. **Local Testing**: Run tests and model training locally
3. **Push Changes**: Push to feature branch
4. **Pull Request**: Create PR to `develop` branch
5. **CI Validation**: Automated testing and validation
6. **Merge**: Merge to `develop` after approval
7. **Release**: Merge `develop` to `main` for deployment

## 🚨 Troubleshooting

### Common Issues

#### Pipeline Failures
```bash
# Check GitHub Actions logs
# Visit: https://github.com/your-repo/actions

# Run failing step locally
python -m pytest tests/test_inference.py -v
```

#### Model Deployment Issues
```bash
# Verify MLflow connection
python -c "import mlflow; print(mlflow.get_tracking_uri())"

# Check S3 access
aws s3 ls s3://your-bucket/group6-capstone/

# Test model loading
python -c "
from mlflow_integration.mlflow_manager import MLflowManager
mgr = MLflowManager()
model = mgr.load_model_with_versioning('lstm_model', 'latest')
print('Model loaded:', model is not None)
"
```

#### Docker Build Issues
```bash
# Check Docker daemon
docker info

# Build with verbose output
python utils/docker_build_deploy.py --verbose

# Test Docker image locally
docker build -t test-image .
docker run --rm test-image python -c "print('Image works')"
```

### Debug Commands

```bash
# Check environment variables
env | grep -E "(MLFLOW|AWS|DOCKER)"

# Verify dependencies
python -c "import tensorflow, mlflow, streamlit; print('All OK')"

# Test MLflow connectivity
python -c "
import mlflow
mlflow.set_tracking_uri('your-mlflow-uri')
print('Connected to:', mlflow.get_tracking_uri())
"
```

## 📈 Performance Optimization

### Build Optimization

- **Docker layer caching**: Reuse cached layers
- **Multi-stage builds**: Reduce final image size
- **Dependency caching**: Cache pip packages
- **Parallel execution**: Run independent jobs in parallel

### Test Optimization

- **Test parallelization**: Run tests in parallel
- **Selective testing**: Only run affected tests
- **Caching**: Cache test artifacts
- **Incremental builds**: Skip unchanged components

### Deployment Optimization

- **Blue-green deployment**: Zero-downtime updates
- **Rolling updates**: Gradual service replacement
- **Health checks**: Fast failure detection
- **Auto-scaling**: Dynamic resource allocation

## 🔄 Future Enhancements

### Planned Features

1. **Docker Hub Integration**
   - Automated image pushing
   - Version tagging
   - Security scanning

2. **ECS Deployment**
   - Complete AWS ECS integration
   - Load balancer configuration
   - Auto-scaling policies

3. **Advanced Monitoring**
   - Prometheus metrics
   - Grafana dashboards
   - Custom alerts

4. **Security Scanning**
   - Container vulnerability scanning
   - Dependency security checks
   - Secrets management

5. **Multi-environment Support**
   - Staging environment
   - Production environment
   - Environment-specific configurations

This CI/CD pipeline provides a robust foundation for automated development, testing, and deployment of the OpenStack RCA System. 
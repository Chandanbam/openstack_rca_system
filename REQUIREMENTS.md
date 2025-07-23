# Requirements Files Structure

This project uses separate requirements files for different phases of the CI/CD pipeline to optimize build times and ensure proper dependency management.

## Requirements Files

### 1. `requirements-base.txt`
**Purpose**: Core dependencies needed across all phases
**Used in**: All phases
**Dependencies**:
- numpy, pandas, scikit-learn
- python-dotenv, pyyaml, requests
- logging

### 2. `requirements-test.txt`
**Purpose**: Testing dependencies
**Used in**: Test & Train phase
**Dependencies**:
- Includes: `requirements-base.txt`
- pytest, pytest-cov, pytest-mock
- pytest-xdist, coverage

### 3. `requirements-mlflow.txt`
**Purpose**: MLflow and AWS dependencies
**Used in**: MLflow deployment phase
**Dependencies**:
- Includes: `requirements-base.txt`
- mlflow, boto3, botocore
- joblib, pickle5, s3fs

### 4. `requirements-docker.txt`
**Purpose**: Production dependencies for Docker
**Used in**: Docker build phase
**Dependencies**:
- Includes: `requirements-base.txt`, `requirements-mlflow.txt`
- streamlit, streamlit-option-menu
- tensorflow, tf-keras, anthropic
- chromadb, sentence-transformers
- psutil, python-multipart

### 5. `requirements-dev.txt`
**Purpose**: Development tools
**Used in**: Local development
**Dependencies**:
- Includes: `requirements-docker.txt`
- ipython, jupyter
- black, flake8, mypy
- pre-commit, sphinx

## CI/CD Pipeline Phases

### 1. Setup and Cache Dependencies
- **Job**: `setup-and-cache`
- **Purpose**: Install base dependencies and create shared artifacts
- **Requirements**: `requirements-base.txt`
- **Artifacts**: Shared dependencies cache

### 2. Test & Train Model
- **Job**: `test-and-train`
- **Purpose**: Run tests and train models
- **Requirements**: `requirements-test.txt`
- **Artifacts**: Test results, models, logs

### 3. Deploy to MLflow & S3
- **Job**: `mlflow-deploy`
- **Purpose**: Deploy models to MLflow and S3
- **Requirements**: `requirements-mlflow.txt`
- **Artifacts**: MLflow artifacts, model files

### 4. Build Docker Image
- **Job**: `docker-build`
- **Purpose**: Build and test Docker image
- **Requirements**: `requirements-docker.txt`
- **Artifacts**: Docker artifacts, build files

### 5. Deploy to AWS ECS
- **Job**: `ecs-deploy`
- **Purpose**: Deploy to AWS ECS (placeholder)
- **Requirements**: All artifacts from previous phases
- **Artifacts**: Deployment summary

## Shared Artifacts

The CI/CD pipeline creates and shares artifacts across phases:

1. **shared-dependencies**: Cached pip dependencies and shared directories
2. **test-results**: Test coverage reports and results
3. **mlflow-artifacts**: Models, logs, and MLflow integration files
4. **docker-artifacts**: Dockerfile, docker-compose.yml, and build utilities

## Usage

### Local Development
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install only production dependencies
pip install -r requirements-docker.txt

# Install only testing dependencies
pip install -r requirements-test.txt
```

### CI/CD Pipeline
The pipeline automatically uses the appropriate requirements file for each phase, ensuring:
- Faster builds through dependency caching
- Proper separation of concerns
- Shared artifacts across phases
- Optimized Docker image size

## Benefits

1. **Faster Builds**: Dependencies are cached and shared across phases
2. **Smaller Images**: Only necessary dependencies are included in each phase
3. **Better Organization**: Clear separation of dependencies by purpose
4. **Artifact Sharing**: Models and configurations are shared across phases
5. **Reduced Redundancy**: Base dependencies are installed once and reused 
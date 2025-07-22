#!/usr/bin/env python3
"""
Generate Docker image information for CI/CD pipeline
"""

import os
import json
from datetime import datetime

def generate_docker_info():
    """Generate Docker image information file"""
    
    # Get environment variables
    docker_username = os.getenv('DOCKER_USERNAME', 'chandantech')
    docker_image = os.getenv('DOCKER_IMAGE', 'openstack-rca-system')
    github_sha = os.getenv('GITHUB_SHA', 'latest')
    
    # Create image info
    image_info = {
        'image_name': f"{docker_username}/{docker_image}",
        'tag': github_sha,
        'full_image': f"{docker_username}/{docker_image}:{github_sha}",
        'build_time': datetime.now().isoformat(),
        'mlflow_experiment': os.getenv('MLFLOW_EXPERIMENT_NAME', 'openstack_rca_system_staging'),
        'mlflow_tracking_uri': os.getenv('MLFLOW_TRACKING_URI', ''),
        'mlflow_artifact_root': os.getenv('MLFLOW_ARTIFACT_ROOT', ''),
        'aws_region': os.getenv('AWS_DEFAULT_REGION', 'ap-south-1'),
        'environment': 'production'
    }
    
    # Write to file
    with open('docker-image-info.txt', 'w') as f:
        f.write(f"Docker Image Information\n")
        f.write(f"======================\n\n")
        f.write(f"Image Name: {image_info['image_name']}\n")
        f.write(f"Tag: {image_info['tag']}\n")
        f.write(f"Full Image: {image_info['full_image']}\n")
        f.write(f"Build Time: {image_info['build_time']}\n")
        f.write(f"MLflow Experiment: {image_info['mlflow_experiment']}\n")
        f.write(f"MLflow Tracking URI: {image_info['mlflow_tracking_uri']}\n")
        f.write(f"MLflow Artifact Root: {image_info['mlflow_artifact_root']}\n")
        f.write(f"AWS Region: {image_info['aws_region']}\n")
        f.write(f"Environment: {image_info['environment']}\n")
    
    # Also write JSON for programmatic access
    with open('docker-image-info.json', 'w') as f:
        json.dump(image_info, f, indent=2)
    
    print(f"✅ Docker image info generated:")
    print(f"   Image: {image_info['full_image']}")
    print(f"   Build Time: {image_info['build_time']}")
    print(f"   MLflow Experiment: {image_info['mlflow_experiment']}")

if __name__ == "__main__":
    generate_docker_info() 
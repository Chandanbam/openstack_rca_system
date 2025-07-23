#!/bin/bash

echo "🔧 OpenStack RCA System Environment Setup"
echo "=========================================="

# Check if .env file already exists
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists!"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Setup cancelled. Existing .env file preserved."
        exit 1
    fi
fi

# Copy template to .env
if [ -f "env.template" ]; then
    cp env.template .env
    echo "✅ Created .env file from template"
else
    echo "❌ env.template not found!"
    exit 1
fi

echo ""
echo "📝 Please edit the .env file with your actual values:"
echo "   nano .env"
echo ""
echo "🔑 Required variables to set:"
echo "   - ANTHROPIC_API_KEY (Required for RCA analysis)"
echo ""
echo "🔧 Optional variables:"
echo "   - MLFLOW_TRACKING_URI (For MLflow integration)"
echo "   - AWS_ACCESS_KEY_ID (For S3 storage)"
echo "   - AWS_SECRET_ACCESS_KEY (For S3 storage)"
echo ""
echo "🚀 After editing .env, you can run:"
echo "   docker-compose up"
echo "   or"
echo "   docker run --env-file .env -p 7051:7051 openstack-rca-system:latest"
echo ""
echo "📚 For more information, see:"
echo "   - ENVIRONMENT_VARIABLES.md"
echo "   - DOCKER_DEPLOYMENT_GUIDE.md" 
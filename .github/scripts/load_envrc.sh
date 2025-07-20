#!/bin/bash
# Helper script to load .envrc variables in GitHub Actions

set -e

echo "🔧 Loading environment variables..."

# Check if .envrc file exists
if [ -f ".envrc" ]; then
    echo "📁 Found .envrc file, loading variables..."
    
    # Extract export statements from .envrc and set them as environment variables
    while IFS= read -r line; do
        # Skip comments and empty lines
        if [[ $line =~ ^[[:space:]]*# ]] || [[ -z "${line// }" ]]; then
            continue
        fi
        
        # Check if line starts with 'export '
        if [[ $line =~ ^export[[:space:]]+ ]]; then
            # Remove 'export ' prefix and add to GITHUB_ENV
            env_var=$(echo "$line" | sed 's/^export[[:space:]]*//')
            if [[ $env_var == *"="* ]]; then
                echo "$env_var" >> $GITHUB_ENV
                echo "  ✅ Loaded: ${env_var%%=*}"
            fi
        fi
    done < .envrc
    
    echo "✅ .envrc variables loaded successfully"
else
    echo "⚠️ .envrc file not found, skipping..."
fi

# Load additional environment variables from secrets
echo "🔐 Loading secrets as environment variables..."

# Function to safely set environment variable
set_env_var() {
    local var_name=$1
    local secret_value=$2
    
    if [ -n "$secret_value" ]; then
        echo "$var_name=$secret_value" >> $GITHUB_ENV
        echo "  ✅ Set: $var_name"
    else
        echo "  ⚠️ Warning: $var_name secret not found"
    fi
}

# Set secrets (these will override .envrc values if conflicts)
set_env_var "ANTHROPIC_API_KEY" "$ANTHROPIC_API_KEY"
set_env_var "MLFLOW_TRACKING_URI" "$MLFLOW_TRACKING_URI"
set_env_var "MLFLOW_ARTIFACT_ROOT" "$MLFLOW_ARTIFACT_ROOT"
set_env_var "MLFLOW_S3_ENDPOINT_URL" "$MLFLOW_S3_ENDPOINT_URL"
set_env_var "AWS_ACCESS_KEY_ID" "$AWS_ACCESS_KEY_ID"
set_env_var "AWS_SECRET_ACCESS_KEY" "$AWS_SECRET_ACCESS_KEY"
set_env_var "AWS_DEFAULT_REGION" "$AWS_DEFAULT_REGION"
set_env_var "DOCKER_USERNAME" "$DOCKER_USERNAME"
set_env_var "DOCKER_PASSWORD" "$DOCKER_PASSWORD"

echo "✅ Environment setup complete" 
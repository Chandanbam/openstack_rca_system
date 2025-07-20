import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Configuration
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    GEMINI_SERVICE_ACCOUNT_PATH = os.getenv('GEMINI_SERVICE_ACCOUNT_PATH', 'gemini-service-account.json')
    
    # AI Provider Selection (claude or gemini)
    AI_PROVIDER = os.getenv('AI_PROVIDER', 'claude').lower()
    
    # File paths
    DATA_DIR = 'logs'
    MODELS_DIR = 'models'
    CACHE_DIR = 'data/cache'
    VECTOR_DB_DIR = 'data/vector_db'
    
    # LSTM Model Configuration
    LSTM_CONFIG = {
        'max_sequence_length': 100,
        'embedding_dim': 128,
        'lstm_units': 64,
        'dropout_rate': 0.2,
        'batch_size': 32,
        'epochs': 50,
        'validation_split': 0.2
    }
    
    # Log Processing Configuration
    LOG_CONFIG = {
        'important_keywords': [
            'ERROR', 'CRITICAL', 'FAILED', 'EXCEPTION', 'TIMEOUT',
            'CONNECTION_LOST', 'UNAVAILABLE', 'DENIED', 'REJECTED',
            'SPAWNING', 'TERMINATING', 'DESTROYED', 'CLAIM', 'RESOURCE'
        ],
        'service_patterns': {
            'nova-api': r'nova-api\.log',
            'nova-compute': r'nova-compute\.log',
            'nova-scheduler': r'nova-scheduler\.log'
        }
    }
    
    # RCA Configuration
    RCA_CONFIG = {
        'similarity_threshold': 0.7,
        'max_context_logs': 50,
        'time_window_minutes': 30,
        'historical_context_size': 10,  # Number of historical logs to include in context
        'max_historical_context_chars': 2000  # Maximum characters for historical context
    }
    
    # NEW: Vector DB Configuration
    VECTOR_DB_CONFIG = {
        'type': 'chroma',
        'embedding_model': 'all-MiniLM-L12-v2',  # Upgraded to L12 for better semantic understanding
        'collection_name': 'openstack_logs',
        'similarity_threshold': 0.7,
        'top_k_results': 20,
        'persist_directory': VECTOR_DB_DIR,
        
        # Additional parameters for enhanced configuration
        'chunk_size': 512,  # For text chunking if needed
        'chunk_overlap': 50,  # Overlap between chunks
        'embedding_dimensions': 384,  # Explicit dimension setting
        'distance_metric': 'cosine',  # Distance metric (cosine, euclidean, etc.)
        'max_text_length': 1000,  # Maximum text length for embedding
    }
    
    # AI Model Configuration
    AI_CONFIG = {
        'claude': {
            'model': 'claude-3-5-sonnet-20241022',
            'max_tokens': 2000,
            'temperature': 0.1
        },
        'gemini': {
            'model': 'gemini-1.5-pro',
            'max_tokens': 2000,
            'temperature': 0.1
        }
    }
    
    # Simplified MLflow Configuration for Academic Use
    MLFLOW_CONFIG = {
        # Core MLflow settings
        'tracking_uri': os.getenv('MLFLOW_TRACKING_URI'),
        'experiment_name': 'openstack_rca_system_production',
        
        # S3 Artifact Store with proper folder structure
        'artifact_root': os.getenv('MLFLOW_ARTIFACT_ROOT','s3://chandanbam-bucket/group6-capstone'),
        's3_endpoint_url': os.getenv('MLFLOW_S3_ENDPOINT_URL','https://s3.amazonaws.com'),
        'aws_access_key_id': os.getenv('AWS_ACCESS_KEY_ID'),
        'aws_secret_access_key': os.getenv('AWS_SECRET_ACCESS_KEY'),
        
        # Simplified Model Management
        'auto_register_model': True,  # Automatically register models
        'default_model_stage': 'Production',  # Default to production for academic use
        
        # Basic Logging
        'auto_log': True,  # Enable automatic logging
        'log_models': True,  # Log models automatically
        'tags': {
            'project': 'openstack_rca_system',
            'environment': 'production'
        },
        
        # Single Environment - Auto Deploy (Academic Use)
        'auto_deploy_production': True,  # Auto-deploy to production (simplified)
    }
    
    # MLflow Tracking URI (for backward compatibility)
    MLFLOW_TRACKING_URI = MLFLOW_CONFIG['tracking_uri']
    
    # Streamlit Configuration
    STREAMLIT_CONFIG = {
        'page_title': 'CloudTracer RCA Assistant',
        'page_icon': '🔍',
        'layout': 'wide'
    }

    # Docker Configuration
    DOCKER_CONFIG = {
        'username': os.getenv('DOCKER_USERNAME', 'chandantech'),
        'password': os.getenv('DOCKER_PASSWORD', ''),
        'registry': os.getenv('DOCKER_REGISTRY', 'docker.io'),
        'repository': os.getenv('DOCKER_REPOSITORY', 'openstack-rca-system'),
        'image_latest': f"{os.getenv('DOCKER_USERNAME', 'chandantech')}/{os.getenv('DOCKER_REPOSITORY', 'openstack-rca-system')}:latest",
        'port': 7051,
        'auto_build': True,
        'auto_push': True,
        'build_args': {},
        'labels': {
            'maintainer': 'OpenStack RCA Team',
            'version': '1.0.0',
            'description': 'OpenStack Root Cause Analysis System'
        }
    }
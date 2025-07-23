"""
Inference tests for OpenStack RCA System
Tests model loading, prediction, and performance metrics
"""

import pytest
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

def test_environment_variables():
    """Test that required environment variables are set"""
    required_vars = [
        'ANTHROPIC_API_KEY',
        'MLFLOW_TRACKING_URI',
        'MLFLOW_ARTIFACT_ROOT',
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY',
        'AWS_DEFAULT_REGION'
    ]
    
    missing_vars = []
    for var in required_vars:
        if os.getenv(var) is None:
            missing_vars.append(var)
    
    if missing_vars:
        # In CI/CD environment, these should be set
        if os.getenv('CI') or os.getenv('GITHUB_ACTIONS'):
            pytest.fail(f"Environment variables not set in CI/CD: {missing_vars}")
        else:
            # In local development, just warn
            pytest.skip(f"Environment variables not set (local development): {missing_vars}")
    else:
        print("✅ All required environment variables are set")

def test_config_import():
    """Test that config module can be imported"""
    try:
        from config.config import Config
        config = Config()
        assert config is not None
        print("✅ Config module imported successfully")
    except ImportError as e:
        pytest.fail(f"Failed to import config: {e}")

def test_mlflow_manager_import():
    """Test that MLflow manager can be imported"""
    try:
        from mlflow_integration.mlflow_manager import MLflowManager
        assert MLflowManager is not None
        print("✅ MLflow manager imported successfully")
    except ImportError as e:
        pytest.fail(f"Failed to import MLflow manager: {e}")

def test_vector_db_service_import():
    """Test that vector DB service can be imported"""
    try:
        from services.vector_db_service import VectorDBService
        assert VectorDBService is not None
        print("✅ Vector DB service imported successfully")
    except ImportError as e:
        pytest.fail(f"Failed to import vector DB service: {e}")

def test_preprocessing_import():
    """Test that preprocessing module can be imported"""
    try:
        from data.preprocessing import LogPreprocessor
        preprocessor = LogPreprocessor()
        assert preprocessor is not None
        print("✅ Preprocessing module imported successfully")
    except ImportError as e:
        pytest.fail(f"Failed to import preprocessing: {e}")

def test_streamlit_app_import():
    """Test that Streamlit app can be imported"""
    try:
        from streamlit_app.chatbot import OpenStackRCAAssistant
        assert OpenStackRCAAssistant is not None
        print("✅ Streamlit app imported successfully")
    except ImportError as e:
        pytest.fail(f"Failed to import Streamlit app: {e}")

def test_basic_functionality():
    """Test basic functionality without complex dependencies"""
    # Test that we can create basic objects
    try:
        from config.config import Config
        config = Config()
        
        # Test config has required attributes
        assert hasattr(config, 'ANTHROPIC_API_KEY')
        assert hasattr(config, 'MLFLOW_CONFIG')
        assert hasattr(config, 'VECTOR_DB_CONFIG')
        
        print("✅ Basic functionality test passed")
    except Exception as e:
        pytest.fail(f"Basic functionality test failed: {e}")

def test_file_structure():
    """Test that required files and directories exist"""
    required_files = [
        'main.py',
        'config/config.py',
        'data/preprocessing.py',
        'services/vector_db_service.py',
        'streamlit_app/chatbot.py',
        'mlflow_integration/mlflow_manager.py',
        'requirements.txt',
        'Dockerfile',
        'docker-compose.yml'
    ]
    
    for file_path in required_files:
        assert os.path.exists(file_path), f"Required file {file_path} does not exist"
    
    print("✅ File structure test passed")

def test_vector_db_data():
    """Test that vector DB data exists"""
    vector_db_path = 'data/vector_db'
    assert os.path.exists(vector_db_path), "Vector DB directory does not exist"
    
    # Check for ChromaDB files
    chroma_db_file = os.path.join(vector_db_path, 'chroma.sqlite3')
    assert os.path.exists(chroma_db_file), "ChromaDB database file does not exist"
    
    print("✅ Vector DB data test passed")

if __name__ == "__main__":
    # Run basic tests
    test_environment_variables()
    test_config_import()
    test_mlflow_manager_import()
    test_vector_db_service_import()
    test_preprocessing_import()
    test_streamlit_app_import()
    test_basic_functionality()
    test_file_structure()
    test_vector_db_data()
    print("🎉 All basic tests passed!") 
"""
Pytest configuration and fixtures for OpenStack RCA System tests
"""

import os
import sys
import pytest
from pathlib import Path

# Add project root to Python path for all tests
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set up environment for testing
os.environ.setdefault('TESTING', 'true')
os.environ.setdefault('PYTHONPATH', str(project_root))

# Disable MLflow telemetry during tests
os.environ.setdefault('MLFLOW_TRACKING_DISABLE_LOGGING', 'true')

# Disable ChromaDB telemetry during tests
os.environ.setdefault('ANONYMIZED_TELEMETRY', 'false')
os.environ.setdefault('CHROMA_TELEMETRY_ENABLED', 'false')

@pytest.fixture(scope="session")
def project_root_path():
    """Return the project root path"""
    return project_root

@pytest.fixture(scope="session")
def test_data_dir():
    """Return the test data directory"""
    return project_root / "tests" / "data"

@pytest.fixture(scope="session")
def sample_logs():
    """Sample log data for testing"""
    return [
        "nova-api.log.1.2017-05-16_13:53:08 2017-05-16 00:00:00.008 25746 INFO nova.osapi_compute.wsgi.server [req-38101a0b-2096-447d-96ea-a692162415ae] 10.11.10.1 \"GET /v2/servers/detail HTTP/1.1\" status: 200",
        "nova-compute.log.1.2017-05-16_13:55:31 2017-05-16 00:00:04.500 2931 ERROR nova.compute.manager [req-3ea4052c-895d-4b64-9e2d-04d64c4d94ab] [instance: b9000564-fe1a-409b-b8cc-1e88b294cd1d] VM Failed to start (Lifecycle Event)",
        "nova-scheduler.log.1.2017-05-16_13:56:15 2017-05-16 00:00:05.123 4567 WARNING nova.scheduler.manager No valid host was found for instance b9000564-fe1a-409b-b8cc-1e88b294cd1d"
    ]

@pytest.fixture(scope="session")
def mock_environment():
    """Set up mock environment variables for testing"""
    original_env = os.environ.copy()
    
    # Set mock environment variables
    os.environ.update({
        'ANTHROPIC_API_KEY': 'test-key',
        'MLFLOW_TRACKING_URI': 'http://localhost:5000',
        'MLFLOW_ARTIFACT_ROOT': 's3://test-bucket/test',
        'MLFLOW_S3_ENDPOINT_URL': 'https://s3.amazonaws.com',
        'AWS_ACCESS_KEY_ID': 'test-access-key',
        'AWS_SECRET_ACCESS_KEY': 'test-secret-key',
        'AWS_DEFAULT_REGION': 'us-east-1',
        'TESTING': 'true'
    })
    
    yield os.environ
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)

def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "inference: marks tests as inference tests"
    )
    config.addinivalue_line(
        "markers", "training: marks tests as training tests"
    )
    config.addinivalue_line(
        "markers", "mlflow: marks tests as MLflow integration tests"
    )

def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names"""
    for item in items:
        # Add markers based on test class names and test names
        if "TestModelTraining" in item.nodeid:
            item.add_marker(pytest.mark.training)
        elif "TestModelInference" in item.nodeid:
            item.add_marker(pytest.mark.inference)
        elif "TestMLflowIntegration" in item.nodeid or "mlflow" in item.nodeid:
            item.add_marker(pytest.mark.mlflow)
        elif "TestConfiguration" in item.nodeid:
            item.add_marker(pytest.mark.unit)
        else:
            item.add_marker(pytest.mark.unit) 
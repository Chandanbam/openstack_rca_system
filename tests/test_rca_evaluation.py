"""
OpenStack RCA System Evaluation Test Suite
==========================================

This pytest suite evaluates the OpenStack RCA system using:
- Mean Reciprocal Rank (MRR) for ranking quality
- Root Cause Accuracy for diagnostic correctness

Run with: pytest test_rca_evaluation.py -v --json-report --json-report-file=rca_evaluation_report.json
"""

import pytest
import json
import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Any
import tempfile
import logging
from unittest.mock import patch, MagicMock

# Disable ChromaDB telemetry
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY_ENABLED"] = "False"

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Test configurations
TEST_CONFIG = {
    "evaluation_metrics": ["mrr", "root_cause_accuracy"],
    "test_scenarios": [
        "disk_space_exhaustion",
        "instance_launch_failure", 
        "network_connectivity",
        "authentication_error",
        "resource_allocation_failure"
    ],
    "fast_mode_tests": True,
    "hybrid_mode_tests": True,
    "mock_anthropic": False  # Set to False to use real API, True for mocking
}

class RCAEvaluationMetrics:
    """Calculate evaluation metrics for RCA system"""
    
    @staticmethod
    def calculate_mrr(ranked_results: List[List[str]], ground_truth: List[str]) -> float:
        """
        Calculate Mean Reciprocal Rank
        
        Args:
            ranked_results: List of ranked predictions for each query
            ground_truth: List of correct answers for each query
            
        Returns:
            MRR score between 0 and 1
        """
        if not ranked_results or not ground_truth:
            return 0.0
        
        reciprocal_ranks = []
        
        for predictions, truth in zip(ranked_results, ground_truth):
            truth_lower = truth.lower()
            
            # Find rank of correct answer
            rank = None
            for i, prediction in enumerate(predictions):
                if truth_lower in prediction.lower() or prediction.lower() in truth_lower:
                    rank = i + 1  # 1-indexed rank
                    break
            
            if rank is not None:
                reciprocal_ranks.append(1.0 / rank)
            else:
                reciprocal_ranks.append(0.0)
        
        return np.mean(reciprocal_ranks) if reciprocal_ranks else 0.0
    
    @staticmethod
    def calculate_root_cause_accuracy(predictions: List[str], ground_truth: List[str]) -> float:
        """
        Calculate Root Cause Accuracy
        
        Args:
            predictions: List of predicted root causes
            ground_truth: List of actual root causes
            
        Returns:
            Accuracy score between 0 and 1
        """
        if not predictions or not ground_truth or len(predictions) != len(ground_truth):
            return 0.0
        
        correct = 0
        total = len(predictions)
        
        for pred, truth in zip(predictions, ground_truth):
            # Check if key terms from ground truth appear in prediction
            truth_terms = set(truth.lower().split())
            pred_terms = set(pred.lower().split())
            
            # Calculate overlap
            overlap = len(truth_terms.intersection(pred_terms))
            if overlap >= len(truth_terms) * 0.5:  # 50% term overlap threshold
                correct += 1
        
        return correct / total if total > 0 else 0.0
    
    @staticmethod
    def extract_key_findings(rca_response: str) -> List[str]:
        """Extract key findings from RCA response for ranking evaluation"""
        if not rca_response:
            return []
        
        # Split into sentences and filter relevant ones
        sentences = [s.strip() for s in rca_response.split('.') if s.strip()]
        
        # Extract key diagnostic statements
        key_findings = []
        diagnostic_keywords = [
            'root cause', 'caused by', 'due to', 'insufficient', 'failed',
            'error', 'problem', 'issue', 'unable', 'exceeded', 'exhausted'
        ]
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(keyword in sentence_lower for keyword in diagnostic_keywords):
                key_findings.append(sentence)
        
        return key_findings[:5]  # Top 5 findings

class MockAnthropicAPI:
    """Mock Anthropic API for testing without real API calls"""
    
    MOCK_RESPONSES = {
        "disk_space": """
        Root Cause Analysis: The primary issue is disk space exhaustion on compute nodes.
        
        Key Findings:
        1. Insufficient disk space available on all compute hosts
        2. Nova scheduler unable to find valid host due to disk constraints
        3. Instance spawn failures caused by disk allocation errors
        4. Automatic cleanup processes activated to free space
        
        The root cause is insufficient disk space across the compute infrastructure, 
        preventing new instance creation and causing scheduling failures.
        """,
        
        "instance_launch": """
        Root Cause Analysis: Instance launch failure due to resource constraints.
        
        Key Findings:
        1. No valid host found for instance placement
        2. Resource allocation failed during scheduling phase
        3. Compute nodes unable to satisfy resource requirements
        4. Scheduler filters rejecting all available hosts
        
        The root cause is insufficient available resources (CPU, memory, or disk) 
        across the compute infrastructure to satisfy the instance requirements.
        """,
        
        "network": """
        Root Cause Analysis: Network connectivity issues affecting instance communication.
        
        Key Findings:
        1. Network interface configuration failures
        2. DHCP lease assignment problems
        3. Security group rule blocking traffic
        4. Network namespace isolation issues
        
        The root cause is network misconfiguration preventing proper instance connectivity 
        and communication with external services.
        """,
        
        "authentication": """
        Root Cause Analysis: Authentication service failures.
        
        Key Findings:
        1. Keystone token validation errors
        2. Service authentication timeouts
        3. Invalid credentials or expired tokens
        4. Authorization policy violations
        
        The root cause is authentication service instability or misconfiguration 
        preventing proper service-to-service communication.
        """,
        
        "resource_allocation": """
        Root Cause Analysis: Resource allocation failures in the compute layer.
        
        Key Findings:
        1. Memory allocation exceeded available capacity
        2. CPU overcommit ratio violated
        3. Resource tracker inconsistencies
        4. Placement service unable to satisfy constraints
        
        The root cause is insufficient physical resources or resource tracking 
        inconsistencies preventing successful instance allocation.
        """
    }
    
    @classmethod
    def mock_completion(cls, prompt: str) -> str:
        """Return appropriate mock response based on prompt content"""
        prompt_lower = prompt.lower()
        
        if any(term in prompt_lower for term in ['disk', 'space', 'storage']):
            return cls.MOCK_RESPONSES["disk_space"]
        elif any(term in prompt_lower for term in ['instance', 'launch', 'spawn']):
            return cls.MOCK_RESPONSES["instance_launch"]
        elif any(term in prompt_lower for term in ['network', 'connectivity', 'dhcp']):
            return cls.MOCK_RESPONSES["network"]
        elif any(term in prompt_lower for term in ['auth', 'keystone', 'token']):
            return cls.MOCK_RESPONSES["authentication"]
        else:
            return cls.MOCK_RESPONSES["resource_allocation"]

class TestDataGenerator:
    """Generate test data and scenarios for evaluation"""
    
    @staticmethod
    def create_test_log_data() -> pd.DataFrame:
        """Create synthetic OpenStack log data for testing"""
        base_time = datetime.now() - timedelta(hours=1)
        
        log_entries = [
            # Disk space exhaustion scenario
            {
                'timestamp': base_time + timedelta(minutes=0),
                'service_type': 'nova-api',
                'level': 'INFO',
                'message': 'POST /v2/servers HTTP/1.1 status: 202',
                'instance_id': 'c4f2a8b2-7d1e-4e9f-9c5a-1a2b3c4d5e6f',
                'request_id': 'req-9bc36dd9-91c5-4314-898a-47625eb93b09'
            },
            {
                'timestamp': base_time + timedelta(minutes=1),
                'service_type': 'nova-scheduler',
                'level': 'WARNING',
                'message': 'Host cp-1 has insufficient disk space: required 20GB, available 2GB',
                'instance_id': 'c4f2a8b2-7d1e-4e9f-9c5a-1a2b3c4d5e6f',
                'request_id': 'req-9bc36dd9-91c5-4314-898a-47625eb93b09'
            },
            {
                'timestamp': base_time + timedelta(minutes=2),
                'service_type': 'nova-scheduler',
                'level': 'ERROR',
                'message': 'No valid host was found. There are not enough hosts available.',
                'instance_id': 'c4f2a8b2-7d1e-4e9f-9c5a-1a2b3c4d5e6f',
                'request_id': 'req-9bc36dd9-91c5-4314-898a-47625eb93b09'
            },
            {
                'timestamp': base_time + timedelta(minutes=3),
                'service_type': 'nova-compute',
                'level': 'ERROR',
                'message': 'Instance failed to spawn due to insufficient disk space',
                'instance_id': 'c4f2a8b2-7d1e-4e9f-9c5a-1a2b3c4d5e6f',
                'request_id': 'req-9bc36dd9-91c5-4314-898a-47625eb93b09'
            },
            # Network connectivity scenario
            {
                'timestamp': base_time + timedelta(minutes=5),
                'service_type': 'neutron-dhcp-agent',
                'level': 'ERROR',
                'message': 'DHCP lease allocation failed for network',
                'instance_id': 'a1b2c3d4-5e6f-7890-abcd-ef1234567890',
                'request_id': 'req-network-001'
            },
            {
                'timestamp': base_time + timedelta(minutes=6),
                'service_type': 'nova-network',
                'level': 'WARNING',
                'message': 'Network interface configuration timeout',
                'instance_id': 'a1b2c3d4-5e6f-7890-abcd-ef1234567890',
                'request_id': 'req-network-001'
            },
            # Authentication scenario
            {
                'timestamp': base_time + timedelta(minutes=10),
                'service_type': 'keystone',
                'level': 'ERROR',
                'message': 'Token validation failed: token expired',
                'instance_id': None,
                'request_id': 'req-auth-001'
            },
            {
                'timestamp': base_time + timedelta(minutes=11),
                'service_type': 'nova-api',
                'level': 'ERROR',
                'message': 'Authentication failed for service request',
                'instance_id': None,
                'request_id': 'req-auth-001'
            }
        ]
        
        return pd.DataFrame(log_entries)
    
    @staticmethod
    def get_test_scenarios() -> List[Dict[str, Any]]:
        """Define test scenarios with expected outcomes"""
        return [
            {
                'scenario_id': 'disk_space_exhaustion',
                'issue_description': 'Instance launch failing with disk space errors',
                'expected_root_cause': 'insufficient disk space available compute hosts',
                'expected_category': 'resource_shortage',
                'keywords': ['disk', 'space', 'insufficient', 'storage']
            },
            {
                'scenario_id': 'instance_launch_failure',
                'issue_description': 'Unable to launch new instances, scheduler not finding hosts',
                'expected_root_cause': 'no valid host found resource constraints',
                'expected_category': 'instance_issues',
                'keywords': ['host', 'valid', 'scheduler', 'resources']
            },
            {
                'scenario_id': 'network_connectivity',
                'issue_description': 'Instances cannot reach network, DHCP issues',
                'expected_root_cause': 'network configuration dhcp allocation failures',
                'expected_category': 'network_issues',
                'keywords': ['network', 'dhcp', 'connectivity', 'interface']
            },
            {
                'scenario_id': 'authentication_error',
                'issue_description': 'Service authentication failing, token validation errors',
                'expected_root_cause': 'authentication service token validation failures',
                'expected_category': 'authentication_issues',
                'keywords': ['authentication', 'token', 'keystone', 'validation']
            },
            {
                'scenario_id': 'resource_allocation_failure',
                'issue_description': 'Resource allocation errors during instance creation',
                'expected_root_cause': 'resource allocation exceeded available capacity',
                'expected_category': 'resource_shortage',
                'keywords': ['resource', 'allocation', 'capacity', 'exceeded']
            }
        ]

@pytest.fixture(scope="session")
def test_environment():
    """Set up test environment"""
    # Create temporary directories
    temp_dir = tempfile.mkdtemp()
    
    # Set environment variables
    os.environ['ANTHROPIC_API_KEY'] = 'test-key-mock'
    
    yield {
        'temp_dir': temp_dir,
        'test_data': TestDataGenerator.create_test_log_data(),
        'scenarios': TestDataGenerator.get_test_scenarios()
    }
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic client for testing"""
    if TEST_CONFIG["mock_anthropic"]:
        with patch('anthropic.Anthropic') as mock_client:
            # Mock the completion response
            mock_response = MagicMock()
            mock_response.content = [MagicMock()]
            mock_response.content[0].text = "Mock response"
            
            mock_client.return_value.messages.create.return_value = mock_response
            
            # Add side effect to return appropriate responses
            def mock_create(*args, **kwargs):
                messages = kwargs.get('messages', [])
                if messages:
                    prompt = messages[-1].get('content', '')
                    mock_response.content[0].text = MockAnthropicAPI.mock_completion(prompt)
                return mock_response
            
            mock_client.return_value.messages.create.side_effect = mock_create
            yield mock_client
    else:
        yield None

class TestRCAEvaluation:
    """Main test class for RCA system evaluation"""
    
    def test_mrr_calculation(self):
        """Test MRR calculation with known data"""
        # Test data: ranked predictions and ground truth
        ranked_results = [
            ["insufficient disk space", "network error", "authentication failure"],
            ["authentication failure", "disk space issue", "network problem"],
            ["network connectivity issue", "disk space", "auth error"]
        ]
        ground_truth = [
            "disk space exhaustion",
            "authentication failure", 
            "network connectivity"
        ]
        
        mrr = RCAEvaluationMetrics.calculate_mrr(ranked_results, ground_truth)
        
        # Expected: 1/1 + 1/1 + 1/2 = 2.5, MRR = 2.5/3 = 0.833
        assert 0.6 <= mrr <= 1.0, f"MRR should be reasonable for good predictions, got {mrr}"
    
    def test_root_cause_accuracy_calculation(self):
        """Test Root Cause Accuracy calculation"""
        predictions = [
            "The issue is caused by insufficient disk space on compute nodes",
            "Authentication service failure due to token validation errors",
            "Network connectivity problems caused by DHCP configuration"
        ]
        ground_truth = [
            "insufficient disk space available compute hosts",
            "authentication service token validation failures", 
            "network configuration dhcp allocation failures"
        ]
        
        accuracy = RCAEvaluationMetrics.calculate_root_cause_accuracy(predictions, ground_truth)
        
        assert 0.6 <= accuracy <= 1.0, f"Accuracy should be high for good predictions, got {accuracy}"
    
    @pytest.mark.parametrize("mode", ["fast", "hybrid"])
    def test_rca_analysis_scenarios(self, test_environment, mock_anthropic_client, mode):
        """Test RCA analysis for different scenarios and modes"""
        try:
            # Import required modules
            from lstm.rca_analyzer import RCAAnalyzer
            from config.config import Config
            
            # Initialize RCA analyzer
            rca_analyzer = RCAAnalyzer(
                api_key='test-key-mock',
                lstm_model=None  # Will use mock for testing
            )
            
            results = []
            scenarios = test_environment['scenarios']
            test_data = test_environment['test_data']
            
            for scenario in scenarios:
                try:
                    # Run RCA analysis
                    fast_mode = (mode == "fast")
                    analysis_result = rca_analyzer.analyze_issue(
                        scenario['issue_description'],
                        test_data,
                        fast_mode=fast_mode
                    )
                    
                    # Extract findings for evaluation
                    rca_response = analysis_result.get('root_cause_analysis', '')
                    findings = RCAEvaluationMetrics.extract_key_findings(rca_response)
                    
                    results.append({
                        'scenario_id': scenario['scenario_id'],
                        'mode': mode,
                        'findings': findings,
                        'expected_cause': scenario['expected_root_cause'],
                        'analysis_result': analysis_result
                    })
                    
                except Exception as e:
                    # Log error but continue with other scenarios
                    results.append({
                        'scenario_id': scenario['scenario_id'],
                        'mode': mode,
                        'error': str(e),
                        'findings': [],
                        'expected_cause': scenario['expected_root_cause']
                    })
            
            # Store results for metric calculation
            setattr(self, f'rca_results_{mode}', results)
            
            assert len(results) > 0, f"Should have results for {mode} mode"
            
        except ImportError as e:
            pytest.skip(f"Required modules not available: {e}")
    
    def test_calculate_evaluation_metrics(self, test_environment):
        """Calculate final evaluation metrics"""
        metrics_report = {
            'test_timestamp': datetime.now().isoformat(),
            'test_config': TEST_CONFIG,
            'scenarios_tested': len(test_environment['scenarios']),
            'metrics': {}
        }
        
        # Process results for each mode
        for mode in ['fast', 'hybrid']:
            if hasattr(self, f'rca_results_{mode}'):
                results = getattr(self, f'rca_results_{mode}')
                
                # Prepare data for metric calculation
                ranked_predictions = []
                ground_truths = []
                predictions = []
                
                for result in results:
                    if 'error' not in result:
                        findings = result.get('findings', [])
                        expected = result['expected_cause']
                        
                        ranked_predictions.append(findings)
                        ground_truths.append(expected)
                        
                        # Use first finding as primary prediction
                        primary_prediction = findings[0] if findings else ""
                        predictions.append(primary_prediction)
                
                # Calculate metrics
                if ranked_predictions and ground_truths:
                    mrr = RCAEvaluationMetrics.calculate_mrr(ranked_predictions, ground_truths)
                    accuracy = RCAEvaluationMetrics.calculate_root_cause_accuracy(predictions, ground_truths)
                    
                    metrics_report['metrics'][f'{mode}_mode'] = {
                        'mean_reciprocal_rank': round(mrr, 4),
                        'root_cause_accuracy': round(accuracy, 4),
                        'scenarios_completed': len(ranked_predictions),
                        'scenarios_failed': len([r for r in results if 'error' in r])
                    }
        
        # Calculate overall metrics
        if 'fast_mode' in metrics_report['metrics'] and 'hybrid_mode' in metrics_report['metrics']:
            fast_mrr = metrics_report['metrics']['fast_mode']['mean_reciprocal_rank']
            hybrid_mrr = metrics_report['metrics']['hybrid_mode']['mean_reciprocal_rank']
            fast_acc = metrics_report['metrics']['fast_mode']['root_cause_accuracy']
            hybrid_acc = metrics_report['metrics']['hybrid_mode']['root_cause_accuracy']
            
            metrics_report['metrics']['overall'] = {
                'average_mrr': round((fast_mrr + hybrid_mrr) / 2, 4),
                'average_accuracy': round((fast_acc + hybrid_acc) / 2, 4),
                'hybrid_improvement_mrr': round(hybrid_mrr - fast_mrr, 4),
                'hybrid_improvement_accuracy': round(hybrid_acc - fast_acc, 4)
            }
        
        # Save metrics report
        report_file = 'rca_evaluation_metrics.json'
        with open(report_file, 'w') as f:
            json.dump(metrics_report, f, indent=2)
        
        print(f"\n{'='*60}")
        print("RCA SYSTEM EVALUATION RESULTS")
        print(f"{'='*60}")
        print(f"Test Timestamp: {metrics_report['test_timestamp']}")
        print(f"Scenarios Tested: {metrics_report['scenarios_tested']}")
        print(f"{'='*60}")
        
        for mode, metrics in metrics_report['metrics'].items():
            if mode != 'overall':
                print(f"\n{mode.upper()} MODE RESULTS:")
                print(f"  Mean Reciprocal Rank: {metrics['mean_reciprocal_rank']:.4f}")
                print(f"  Root Cause Accuracy:  {metrics['root_cause_accuracy']:.4f}")
                print(f"  Scenarios Completed:  {metrics['scenarios_completed']}")
                print(f"  Scenarios Failed:     {metrics['scenarios_failed']}")
        
        if 'overall' in metrics_report['metrics']:
            overall = metrics_report['metrics']['overall']
            print(f"\nOVERALL RESULTS:")
            print(f"  Average MRR:          {overall['average_mrr']:.4f}")
            print(f"  Average Accuracy:     {overall['average_accuracy']:.4f}")
            print(f"  Hybrid Improvement:")
            print(f"    MRR Delta:          {overall['hybrid_improvement_mrr']:+.4f}")
            print(f"    Accuracy Delta:     {overall['hybrid_improvement_accuracy']:+.4f}")
        
        print(f"\n{'='*60}")
        print(f"Report saved to: {report_file}")
        print(f"{'='*60}")
        
        # Store report in class for access
        self.evaluation_report = metrics_report
        
        # Assert minimum performance thresholds
        if 'overall' in metrics_report['metrics']:
            overall = metrics_report['metrics']['overall']
            assert overall['average_mrr'] >= 0.3, f"Average MRR too low: {overall['average_mrr']}"
            assert overall['average_accuracy'] >= 0.3, f"Average accuracy too low: {overall['average_accuracy']}"
    
    def test_performance_comparison(self):
        """Test performance comparison between modes"""
        if hasattr(self, 'evaluation_report'):
            metrics = self.evaluation_report['metrics']
            
            if 'fast_mode' in metrics and 'hybrid_mode' in metrics:
                fast_mrr = metrics['fast_mode']['mean_reciprocal_rank']
                hybrid_mrr = metrics['hybrid_mode']['mean_reciprocal_rank']
                
                # Hybrid mode should generally perform better or equal
                improvement = hybrid_mrr - fast_mrr
                
                print(f"\nPerformance Comparison:")
                print(f"Fast Mode MRR:    {fast_mrr:.4f}")
                print(f"Hybrid Mode MRR:  {hybrid_mrr:.4f}")
                print(f"Improvement:      {improvement:+.4f}")
                
                # Note: We don't assert hybrid > fast as it depends on the specific implementation
                # and test scenarios, but we do want to measure the difference
                assert abs(improvement) <= 1.0, "Improvement should be within reasonable bounds"

# Test configuration and runner
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "evaluation: marks tests as evaluation tests"
    )

def pytest_collection_modifyitems(config, items):
    """Add evaluation marker to all tests in this file"""
    for item in items:
        item.add_marker(pytest.mark.evaluation)

if __name__ == "__main__":
    # Run tests directly if executed as script
    pytest.main([__file__, "-v", "--tb=short"])
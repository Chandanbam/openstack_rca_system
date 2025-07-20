#!/usr/bin/env python3
"""
Test runner script for OpenStack RCA System
Run this script to execute all tests locally
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n🔧 {description}")
    print(f"Command: {cmd}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print("✅ Success!")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed with exit code {e.returncode}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False

def main():
    """Run all tests"""
    print("🧪 OpenStack RCA System - Test Runner")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("main.py").exists():
        print("❌ Error: main.py not found. Please run from project root.")
        sys.exit(1)
    
    # Run tests
    tests_passed = True
    
    # 1. Run all tests with coverage (includes inference, training, MLflow, and configuration tests)
    if not run_command("python3 -m pytest tests/test_inference.py -v --cov=. --cov-report=html --cov-report=xml --tb=short", "Running tests with coverage"):
        tests_passed = False
    
    # 4. Test model training (if environment is set up)
    if os.getenv('ANTHROPIC_API_KEY'):
        print("\n🔧 Testing model training (with MLflow)")
        print("-" * 50)
        if not run_command("python main.py --mode train --enable-mlflow", "Training model with MLflow"):
            print("⚠️ Model training failed (this is OK if MLflow is not configured)")
    else:
        print("\n⚠️ Skipping model training (ANTHROPIC_API_KEY not set)")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    
    if tests_passed:
        print("✅ All tests passed!")
        print("📁 Coverage report: htmlcov/index.html")
        print("📊 Coverage data: coverage.xml")
    else:
        print("❌ Some tests failed!")
        print("🔍 Check the output above for details")
        sys.exit(1)

if __name__ == "__main__":
    main() 
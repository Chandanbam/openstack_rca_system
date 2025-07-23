#!/usr/bin/env python3
"""
Simple RAG Evaluation Runner
===========================

Script to run RAG evaluation tests using API key from .env file.

Usage:
    python run_rag_evaluation.py
    python run_rag_evaluation.py --verbose
    python run_rag_evaluation.py --output-dir my_results
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

def load_env_file():
    """Load ANTHROPIC_API_KEY from .env file"""
    env_file = Path('.env')
    
    if not env_file.exists():
        print("❌ Error: .env file not found")
        print("Create a .env file with: ANTHROPIC_API_KEY=your_key_here")
        sys.exit(1)
    
    try:
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('ANTHROPIC_API_KEY='):
                    api_key = line.split('=', 1)[1].strip()
                    # Remove quotes if present
                    if api_key.startswith('"') and api_key.endswith('"'):
                        api_key = api_key[1:-1]
                    elif api_key.startswith("'") and api_key.endswith("'"):
                        api_key = api_key[1:-1]
                    
                    if not api_key:
                        print("❌ Error: ANTHROPIC_API_KEY is empty in .env file")
                        sys.exit(1)
                    
                    return api_key
        
        print("❌ Error: ANTHROPIC_API_KEY not found in .env file")
        print("Add this line to your .env file: ANTHROPIC_API_KEY=your_key_here")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Error reading .env file: {e}")
        sys.exit(1)

def run_tests(output_dir, verbose=False):
    """Run the RAG evaluation tests"""
    # Load API key from .env
    api_key = load_env_file()
    print("✅ Loaded API key from .env file")
    
    # Set up environment
    env = os.environ.copy()
    env['ANTHROPIC_API_KEY'] = api_key
    
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Check if test file exists
    test_file = Path('tests/test_rag_evaluation.py')
    if not test_file.exists():
        print(f"❌ Error: {test_file} not found")
        sys.exit(1)
    
    print(f"\n{'='*50}")
    print("RUNNING RAG EVALUATION TESTS")
    print(f"{'='*50}")
    print(f"Test file: {test_file}")
    print(f"Output directory: {output_dir}")
    print(f"Verbose: {verbose}")
    print(f"{'='*50}\n")
    
    # Build pytest command
    cmd = [
        sys.executable, '-m', 'pytest',
        str(test_file),
        '-v' if verbose else '-q',
        '--tb=short'
    ]
    
    print("Running command:")
    print(' '.join(cmd))
    print()
    
    # Run tests
    try:
        result = subprocess.run(cmd, env=env, text=True)
        
        if result.returncode == 0:
            print(f"\n✅ Tests completed successfully!")
            print(f"📁 Check results in: {output_dir}")
        else:
            print(f"\n❌ Tests failed with exit code: {result.returncode}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        sys.exit(1)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Run RAG evaluation tests')
    parser.add_argument('--output-dir', default='rag_evaluation_results',
                       help='Output directory (default: rag_evaluation_results)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    run_tests(args.output_dir, args.verbose)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3

import subprocess
import sys
import argparse
from datetime import datetime

def run_build(tag_name, no_cache=False, build_args=None):
    """Run Docker build with progress display"""
    
    print("🏗️ Docker Quick Build")
    print(f"📦 Building: {tag_name}")
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Build command
    cmd = ["docker", "build", "--progress=plain"]
    
    if no_cache:
        cmd.append("--no-cache")
        print("🔄 No-cache build enabled")
    
    # Add build args
    if build_args:
        for key, value in build_args.items():
            cmd.extend(["--build-arg", f"{key}={value}"])
    
    cmd.extend(["-t", tag_name, "."])
    
    print(f"🚀 Command: {' '.join(cmd)}")
    print("=" * 60)
    
    try:
        # Run build with real-time output
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Print output in real-time
        for line in process.stdout:
            print(line.rstrip())
        
        process.wait()
        
        if process.returncode == 0:
            print("=" * 60)
            print("✅ Build completed successfully!")
            print(f"📦 Image: {tag_name}")
            print(f"🎯 Test with: docker run -p 7051:7051 {tag_name}")
            return True
        else:
            print("=" * 60)
            print("❌ Build failed!")
            return False
            
    except KeyboardInterrupt:
        print("\n❌ Build interrupted by user")
        return False
    except Exception as e:
        print(f"❌ Build error: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Quick Docker build for OpenStack RCA System")
    parser.add_argument("--tag", "-t", default="openstack-rca:latest", help="Docker image tag")
    parser.add_argument("--no-cache", action="store_true", help="Build without cache")
    parser.add_argument("--target", help="Build target stage (e.g., 'base', 'production')")
    
    args = parser.parse_args()
    
    # Build args
    build_args = {}
    if args.target:
        build_args["TARGET_STAGE"] = args.target
    
    success = run_build(args.tag, args.no_cache, build_args)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main() 
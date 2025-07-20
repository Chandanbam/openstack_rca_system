#!/usr/bin/env python3
"""
Docker Build and Deploy Script for OpenStack RCA System
Builds Docker container and pushes to DockerHub
"""

import subprocess
import sys
import os
import json
from datetime import datetime
import argparse

class DockerBuilder:
    def __init__(self, docker_username=None, docker_repo=None, version_tag=None):
        # Load from config.py or environment variables
        self.docker_username = docker_username or self.get_docker_username()
        self.docker_repo = docker_repo or self.get_docker_repo()
        self.version_tag = version_tag or self.generate_version_tag()
        self.image_name = f"{self.docker_username}/{self.docker_repo}"
        self.full_image_name = f"{self.image_name}:{self.version_tag}"
        
    def generate_version_tag(self):
        """Generate version tag based on timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        return f"v{timestamp}"
    
    def get_docker_username(self):
        """Get Docker username from config.py or environment variables"""
        try:
            # Try to load from config.py
            import sys
            import os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))
            from config.config import Config
            if hasattr(Config, 'DOCKER_CONFIG'):
                return Config.DOCKER_CONFIG.get('username')
        except ImportError:
            pass
        
        # Fall back to environment variables
        return os.getenv('DOCKER_USERNAME', 'chandantech')
    
    def get_docker_repo(self):
        """Get Docker repository name from config.py or environment variables"""
        try:
            # Try to load from config.py
            import sys
            import os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))
            from config.config import Config
            if hasattr(Config, 'DOCKER_CONFIG'):
                return Config.DOCKER_CONFIG.get('repository')
        except ImportError:
            pass
        
        # Fall back to environment variables
        return os.getenv('DOCKER_REPOSITORY', 'openstack-rca-system')
    
    def get_docker_password(self):
        """Get Docker password from config.py or environment variables"""
        try:
            # Try to load from config.py
            import sys
            import os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))
            from config.config import Config
            if hasattr(Config, 'DOCKER_CONFIG'):
                password = Config.DOCKER_CONFIG.get('password')
                if password:
                    return password
        except ImportError:
            pass
        
        # Fall back to environment variables
        return os.getenv('DOCKER_PASSWORD', '')
    
    def run_command(self, command, description, hide_command=False):
        """Run shell command with logging"""
        print(f"\n🔄 {description}...")
        
        # Only print command if it doesn't contain sensitive information
        if not hide_command:
            print(f"Command: {command}")
        else:
            print("Command: [HIDDEN - contains sensitive information]")
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                check=True,
                capture_output=True,
                text=True
            )
            print(f"✅ {description} completed successfully")
            if result.stdout and not hide_command:
                print(f"Output: {result.stdout.strip()}")
            elif result.stdout and hide_command:
                print("Output: [HIDDEN - may contain sensitive information]")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ {description} failed")
            if not hide_command:
                print(f"Error: {e.stderr}")
            else:
                # For login commands, show error but not the full command
                error_msg = e.stderr.strip()
                if "unauthorized" in error_msg.lower():
                    print("Error: Docker login failed - check your username and password/token")
                else:
                    print(f"Error: {error_msg}")
            return False
    
    def check_docker_installed(self):
        """Check if Docker is installed and running"""
        print("🔍 Checking Docker installation...")
        
        if not self.run_command("docker --version", "Docker version check"):
            print("❌ Docker is not installed or not in PATH")
            return False
            
        if not self.run_command("docker info", "Docker daemon check"):
            print("❌ Docker daemon is not running")
            return False
            
        print("✅ Docker is installed and running")
        return True
    
    def check_docker_login(self):
        """Check if user is already logged into DockerHub"""
        try:
            result = subprocess.run(
                "docker system info --format '{{.RegistryConfig.IndexConfigs}}'",
                shell=True,
                capture_output=True,
                text=True
            )
            
            # If logged in, should show registry information
            if result.returncode == 0 and "docker.io" in result.stdout:
                # Try to get current username
                whoami_result = subprocess.run(
                    "docker system info --format '{{.Username}}'",
                    shell=True,
                    capture_output=True,
                    text=True
                )
                if whoami_result.returncode == 0 and whoami_result.stdout.strip():
                    current_user = whoami_result.stdout.strip()
                    print(f"ℹ️ Already logged into DockerHub as: {current_user}")
                    return True
                    
        except Exception as e:
            # If check fails, assume not logged in
            pass
            
        return False
    
    def docker_login(self, username, password=None):
        """Login to DockerHub"""
        print(f"\n🔐 Logging into DockerHub as {username}...")
        
        if password:
            login_cmd = f"echo '{password}' | docker login -u {username} --password-stdin"
            # Hide the command to prevent password exposure in logs
            result = self.run_command(login_cmd, "DockerHub login", hide_command=True)
            
            if not result:
                print("💡 Login failed. This could be due to:")
                print("   1. Incorrect username or password")
                print("   2. DockerHub requires a Personal Access Token instead of password")
                print("   3. Two-Factor Authentication is enabled (use token)")
                print("   4. Account locked or suspended")
                print("\n🔧 To create a Personal Access Token:")
                print("   1. Go to https://hub.docker.com/settings/security")
                print("   2. Click 'New Access Token'")
                print("   3. Use the token as your password")
                
            return result
        else:
            login_cmd = f"docker login -u {username}"
            return self.run_command(login_cmd, "DockerHub login")
    
    def build_image(self):
        """Build Docker image with optimizations"""
        print(f"\n🏗️ Building Docker image: {self.full_image_name}")
        print(f"🏷️ Also tagging as: {self.docker_username}/{self.docker_repo}:latest")
        print("🎯 Target: production stage")
        print("⚠️ This may take several minutes for ML dependencies...")
        print("📊 Progress will be shown in real-time...")
        
        # Create image with both versioned tag and latest tag
        latest_tag = f"{self.docker_username}/{self.docker_repo}:latest"
        build_cmd = f"docker build --progress=plain --target=production -t {self.full_image_name} -t {latest_tag} ."
        return self.run_command(build_cmd, "Docker image build")
    
    def push_image(self):
        """Push Docker image to DockerHub"""
        print(f"\n📤 Pushing Docker images to DockerHub...")
        
        # Push versioned tag
        print(f"📤 Pushing versioned tag: {self.full_image_name}")
        if not self.run_command(f"docker push {self.full_image_name}", "Push versioned image"):
            return False
        
        # Push latest tag
        latest_tag = f"{self.docker_username}/{self.docker_repo}:latest"
        print(f"📤 Pushing latest tag: {latest_tag}")
        if not self.run_command(f"docker push {latest_tag}", "Push latest image"):
            return False
            
        return True
    
    def test_image(self):
        """Test the built image"""
        print(f"\n🧪 Testing Docker image...")
        
        # Test that the image can be inspected
        inspect_cmd = f"docker inspect {self.full_image_name}"
        if not self.run_command(inspect_cmd, "Image inspection"):
            return False
            
        print("✅ Image built successfully and is ready for deployment")
        return True
    
    def save_build_info(self):
        """Save build information to config"""
        build_info = {
            "docker_image": self.full_image_name,
            "docker_username": self.docker_username,
            "docker_repo": self.docker_repo,
            "version_tag": self.version_tag,
            "build_timestamp": datetime.now().isoformat(),
            "port": 7051
        }
        
        # Save to config file
        config_file = "config/docker_config.json"
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        
        with open(config_file, "w") as f:
            json.dump(build_info, f, indent=2)
            
        print(f"📝 Build info saved to {config_file}")
        
        # Also update main config.py
        self.update_main_config(build_info)
        
    def update_main_config(self, build_info):
        """Update main config.py with Docker deployment info"""
        config_addition = f'''

# Docker Deployment Configuration
DOCKER_CONFIG = {{
    'image': '{build_info["docker_image"]}',
    'image_latest': '{build_info["docker_image_latest"]}',
    'username': '{build_info["docker_username"]}',
    'repo': '{build_info["docker_repo"]}',
    'port': {build_info["port"]},
    'version_tag': '{build_info["version_tag"]}',
    'build_timestamp': '{build_info["build_timestamp"]}'
}}
'''
        
        # Read existing config
        config_file = "config/config.py"
        try:
            with open(config_file, 'r') as f:
                content = f.read()
                
            # Remove existing DOCKER_CONFIG if present
            if "# Docker Deployment Configuration" in content:
                lines = content.split('\n')
                new_lines = []
                skip = False
                for line in lines:
                    if line.strip() == "# Docker Deployment Configuration":
                        skip = True
                        continue
                    if skip and line.strip() == "" and not line.startswith(" ") and not line.startswith("\t"):
                        skip = False
                    if not skip:
                        new_lines.append(line)
                content = '\n'.join(new_lines).rstrip()
            
            # Add new config
            with open(config_file, 'w') as f:
                f.write(content + config_addition)
                
            print(f"✅ Updated {config_file} with Docker configuration")
            
        except Exception as e:
            print(f"⚠️ Failed to update config.py: {e}")
    
    def build_and_deploy(self, docker_username=None, docker_password=None, build_only=False, skip_login=False):
        """Complete build and deploy process"""
        # Use provided credentials or get from config/env
        username = docker_username or self.docker_username
        password = docker_password or self.get_docker_password()
        
        print("🚀 Starting Docker Build and Deploy Process")
        print(f"📦 Image: {self.full_image_name}")
        print(f"🏷️ Version: {self.version_tag}")
        print(f"👤 DockerHub User: {username}")
        print(f"🏗️ Repository: {self.docker_repo}")
        
        if build_only:
            print("🔧 Build-only mode: Will not login or push to registry")
        elif skip_login:
            print("🔧 Skip-login mode: Assuming already logged into DockerHub")
        
        # Check prerequisites
        if not self.check_docker_installed():
            return False
        
        # Login to DockerHub (unless skipped)
        if not build_only and not skip_login:
            # Check if already logged in
            if self.check_docker_login():
                print("✅ Using existing DockerHub login")
            else:
                if not self.docker_login(username, password):
                    return False
        
        # Build image
        if not self.build_image():
            return False
        
        # Test image
        if not self.test_image():
            return False
        
        # Push to DockerHub (unless build-only)
        if not build_only:
            if not self.push_image():
                return False
            
            # Save build info
            self.save_build_info()
            
            print(f"\n🎉 Build and Deploy completed successfully!")
            print(f"📦 Docker Image: {self.full_image_name}")
            print(f"🌐 DockerHub: https://hub.docker.com/r/{self.image_name}")
            print(f"🚀 To deploy: python main.py --mode deploy")
        else:
            print(f"\n🎉 Build completed successfully!")
            print(f"📦 Local Docker Image: {self.full_image_name}")
            print(f"🔧 To push later: docker push {self.full_image_name}")
        
        return True

def main():
    parser = argparse.ArgumentParser(description="Build and deploy Docker container for OpenStack RCA System")
    parser.add_argument("--username", "-u", help="DockerHub username (defaults to config.py or DOCKER_USERNAME env var)")
    parser.add_argument("--repo", "-r", help="DockerHub repository name (defaults to config.py or DOCKER_REPOSITORY env var)")
    parser.add_argument("--password", "-p", help="DockerHub password (defaults to config.py or DOCKER_PASSWORD env var)")
    parser.add_argument("--version", "-v", help="Version tag (auto-generated if not provided)")
    parser.add_argument("--build-only", action="store_true", help="Only build the image, skip login and push to registry")
    parser.add_argument("--skip-login", action="store_true", help="Skip DockerHub login (assumes already logged in)")
    
    args = parser.parse_args()
    
    # Create builder (will auto-load from config/env if not provided)
    builder = DockerBuilder(
        docker_username=args.username,
        docker_repo=args.repo,
        version_tag=args.version
    )
    
    # Get password - use provided, or from config/env, or prompt
    docker_password = args.password or builder.get_docker_password()
    if not docker_password:
        import getpass
        docker_password = getpass.getpass(f"Enter DockerHub password for {builder.docker_username}: ")
    
    success = builder.build_and_deploy(
        builder.docker_username, 
        docker_password, 
        build_only=args.build_only,
        skip_login=args.skip_login
    )
    
    if not success:
        if args.build_only:
            print("❌ Build failed!")
        else:
            print("❌ Build and deploy failed!")
        sys.exit(1)
    
    if args.build_only:
        print("✅ Build completed successfully!")
    else:
        print("✅ Build and deploy completed successfully!")

if __name__ == "__main__":
    main() 
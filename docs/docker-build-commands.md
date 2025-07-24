# Docker Build Commands for Network Issues

## 🐳 Standard Build (Try First)
```bash
docker build -t openstack-rca-system:latest .
```

## 🌐 Network Issue Solutions

### Option 1: Use Google DNS
```bash
docker build --dns 8.8.8.8 --dns 8.8.4.4 -t openstack-rca-system:latest .
```

### Option 2: Use Cloudflare DNS
```bash
docker build --dns 1.1.1.1 --dns 1.0.0.1 -t openstack-rca-system:latest .
```

### Option 3: Build with Network Host
```bash
docker build --network host -t openstack-rca-system:latest .
```

### Option 4: Use BuildKit with DNS
```bash
DOCKER_BUILDKIT=1 docker build --dns 8.8.8.8 -t openstack-rca-system:latest .
```

### Option 5: Build with Proxy (if behind corporate firewall)
```bash
docker build \
  --build-arg HTTP_PROXY=http://proxy.company.com:8080 \
  --build-arg HTTPS_PROXY=http://proxy.company.com:8080 \
  -t openstack-rca-system:latest .
```

## 🔧 Troubleshooting Commands

### Check DNS Resolution
```bash
# Test DNS from host
nslookup deb.debian.org

# Test DNS from container
docker run --rm python:3.10-slim nslookup deb.debian.org
```

### Build with Verbose Output
```bash
docker build --progress=plain --no-cache -t openstack-rca-system:latest .
```

### Build Step by Step
```bash
# Build up to a specific step
docker build --target <step-name> -t openstack-rca-system:latest .
```

## 🚀 Quick Fix Commands

```bash
# Most common solution
docker build --dns 8.8.8.8 -t openstack-rca-system:latest .

# If still failing, try with no cache
docker build --dns 8.8.8.8 --no-cache -t openstack-rca-system:latest .

# Last resort: use host network
docker build --network host -t openstack-rca-system:latest .
``` 
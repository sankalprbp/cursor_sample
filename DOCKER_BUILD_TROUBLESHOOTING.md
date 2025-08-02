# Docker Build Troubleshooting Guide

## Problem: Docker Image Pull Timeout

You encountered this error:
```
failed to solve: DeadlineExceeded: DeadlineExceeded: DeadlineExceeded: python:3.11-slim: failed to resolve source metadata for docker.io/library/python:3.11-slim: failed to do request: Head "https://registry-1.docker.io/v2/library/python/manifests/3.11-slim": context deadline exceeded
```

## Solutions Applied

### 1. Docker Daemon Configuration
Created `docker-daemon.json` with:
- Registry mirrors for faster pulls
- Increased timeout settings
- Better retry mechanisms

### 2. Updated Dockerfile
Modified `backend/Dockerfile` with:
- Build cache mounts for faster builds
- Retry mechanisms for pip install
- Better error handling

### 3. Alternative Dockerfile
Created `backend/Dockerfile.alternative` using:
- Alpine Linux base (smaller, faster to pull)
- More reliable package management

### 4. Automated Fix Script
Created `fix-docker-build.sh` that:
- Pre-pulls all required images
- Configures Docker daemon
- Implements retry mechanisms
- Cleans Docker cache

## Quick Fix Steps

### Option 1: Use the Automated Script (Recommended)
```bash
# Make script executable (if not already)
chmod +x fix-docker-build.sh

# Run the fix script
./fix-docker-build.sh
```

### Option 2: Manual Steps

1. **Pre-pull the problematic image:**
```bash
docker pull python:3.11-slim
```

2. **Configure Docker daemon:**
```bash
sudo mkdir -p /etc/docker
sudo cp docker-daemon.json /etc/docker/daemon.json
sudo systemctl restart docker
```

3. **Clean Docker cache:**
```bash
docker system prune -f
```

4. **Build with retry:**
```bash
docker-compose build --no-cache
```

### Option 3: Use Alternative Dockerfile
If the main Dockerfile still fails, use the Alpine-based alternative:

```bash
# Temporarily rename Dockerfiles
mv backend/Dockerfile backend/Dockerfile.original
mv backend/Dockerfile.alternative backend/Dockerfile

# Build with alternative
docker-compose build --no-cache
```

## Additional Troubleshooting

### Network Issues
If you're behind a corporate firewall or have poor internet:

1. **Use a VPN** if available
2. **Try different registry mirrors** in `docker-daemon.json`
3. **Increase timeout values** in Docker daemon config

### Alternative Registry Mirrors
Add these to your `docker-daemon.json`:
```json
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com",
    "https://registry.docker-cn.com"
  ]
}
```

### Manual Image Pull with Retry
```bash
for i in {1..5}; do
    echo "Attempt $i to pull python:3.11-slim"
    if docker pull python:3.11-slim; then
        echo "Success!"
        break
    else
        echo "Failed, waiting 10 seconds..."
        sleep 10
    fi
done
```

### Check Docker Logs
```bash
# Check Docker daemon logs
sudo journalctl -u docker.service -f

# Check Docker build logs
docker-compose build --no-cache --progress=plain
```

## Prevention

### 1. Regular Maintenance
```bash
# Clean up regularly
docker system prune -f
docker image prune -f
```

### 2. Use Build Cache
```bash
# Build with cache
docker-compose build

# Only rebuild when needed
docker-compose build --no-cache
```

### 3. Monitor Network
- Check your internet connection
- Use stable network connections
- Consider using a wired connection for large builds

## Success Indicators

After applying fixes, you should see:
- ✅ Images pull successfully
- ✅ Build completes without timeout errors
- ✅ All services start properly
- ✅ Health checks pass

## If Problems Persist

1. **Check system resources:**
```bash
free -h
df -h
```

2. **Check Docker daemon status:**
```bash
sudo systemctl status docker
```

3. **Try different base images:**
- `python:3.11-alpine` (smaller)
- `python:3.11-bullseye` (more stable)
- `python:3.10-slim` (older but stable)

4. **Contact your network administrator** if behind corporate firewall

## Support

If you continue to have issues:
1. Check the Docker logs for specific error messages
2. Try the alternative Dockerfile
3. Consider using a different network connection
4. Report the issue with full error logs
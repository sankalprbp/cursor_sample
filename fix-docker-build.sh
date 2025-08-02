#!/bin/bash

# Fix Docker Build Issues Script
# This script helps resolve Docker image pull timeout issues

set -e

echo "🔧 Fixing Docker build issues..."

# Function to check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        echo "❌ Docker is not running. Please start Docker first."
        exit 1
    fi
    echo "✅ Docker is running"
}

# Function to pre-pull required images
pre_pull_images() {
    echo "📥 Pre-pulling required Docker images..."
    
    # Pull Python base image with retry
    echo "Pulling python:3.11-slim..."
    for i in {1..3}; do
        if docker pull python:3.11-slim; then
            echo "✅ Successfully pulled python:3.11-slim"
            break
        else
            echo "⚠️  Attempt $i failed, retrying..."
            sleep 5
        fi
    done
    
    # Pull other required images
    echo "Pulling postgres:15..."
    docker pull postgres:15
    
    echo "Pulling redis:7-alpine..."
    docker pull redis:7-alpine
    
    echo "Pulling nginx:alpine..."
    docker pull nginx:alpine
    
    echo "Pulling minio/minio..."
    docker pull minio/minio
    
    echo "Pulling node:18-alpine..."
    docker pull node:18-alpine
    
    echo "✅ All images pre-pulled successfully"
}

# Function to configure Docker daemon
configure_docker() {
    echo "⚙️  Configuring Docker daemon..."
    
    # Create docker daemon config directory if it doesn't exist
    sudo mkdir -p /etc/docker
    
    # Copy the daemon configuration
    if [ -f "docker-daemon.json" ]; then
        sudo cp docker-daemon.json /etc/docker/daemon.json
        echo "✅ Docker daemon configuration updated"
    else
        echo "⚠️  docker-daemon.json not found, skipping daemon configuration"
    fi
}

# Function to restart Docker daemon
restart_docker() {
    echo "🔄 Restarting Docker daemon..."
    sudo systemctl restart docker
    sleep 5
    echo "✅ Docker daemon restarted"
}

# Function to clean up Docker cache
clean_docker_cache() {
    echo "🧹 Cleaning Docker cache..."
    docker system prune -f
    echo "✅ Docker cache cleaned"
}

# Function to build with retry mechanism
build_with_retry() {
    echo "🔨 Building with retry mechanism..."
    
    for attempt in {1..3}; do
        echo "Build attempt $attempt of 3..."
        
        if docker-compose build --no-cache; then
            echo "✅ Build completed successfully!"
            return 0
        else
            echo "❌ Build attempt $attempt failed"
            if [ $attempt -lt 3 ]; then
                echo "Waiting 10 seconds before retry..."
                sleep 10
            fi
        fi
    done
    
    echo "❌ All build attempts failed"
    return 1
}

# Main execution
main() {
    echo "🚀 Starting Docker build fix process..."
    
    check_docker
    configure_docker
    restart_docker
    clean_docker_cache
    pre_pull_images
    
    echo ""
    echo "🎯 Ready to build! Running docker-compose build..."
    echo ""
    
    if build_with_retry; then
        echo ""
        echo "🎉 Success! Your Docker build should now work properly."
        echo "You can now run: docker-compose up"
    else
        echo ""
        echo "💡 If you're still having issues, try these additional steps:"
        echo "1. Check your internet connection"
        echo "2. Try using a VPN if you're behind a corporate firewall"
        echo "3. Increase Docker daemon timeout settings"
        echo "4. Use alternative registry mirrors"
    fi
}

# Run main function
main "$@"
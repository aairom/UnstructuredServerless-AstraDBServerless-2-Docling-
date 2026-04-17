#!/bin/bash

# Local build and test script for Docker image
# This script builds the image locally for testing before deployment

set -e

echo "=========================================="
echo "Local Docker Build & Test"
echo "PDF to AstraDB GUI Application"
echo "=========================================="
echo ""

# Configuration
IMAGE_NAME="pdf-astradb-gui"
IMAGE_TAG="${IMAGE_TAG:-latest}"
CONTAINER_NAME="pdf-astradb-gui-test"
PORT="${PORT:-8080}"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "🏗️  Building Docker image..."
cd "$(dirname "$0")/.."

docker build -f k8s-cloud/Dockerfile -t "${IMAGE_NAME}:${IMAGE_TAG}" .

if [ $? -eq 0 ]; then
    echo "✅ Image built successfully: ${IMAGE_NAME}:${IMAGE_TAG}"
else
    echo "❌ Build failed"
    exit 1
fi

echo ""
echo "📊 Image details:"
docker images "${IMAGE_NAME}:${IMAGE_TAG}"

echo ""
read -p "🚀 Do you want to run the container locally? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Stop and remove existing container if running
    if docker ps -a | grep -q "$CONTAINER_NAME"; then
        echo "🛑 Stopping existing container..."
        docker stop "$CONTAINER_NAME" 2>/dev/null || true
        docker rm "$CONTAINER_NAME" 2>/dev/null || true
    fi
    
    # Check if .env file exists
    if [ ! -f ".env" ]; then
        echo "⚠️  Warning: .env file not found"
        echo "   Creating from template..."
        cp k8s-cloud/.env.example .env
        echo "   Please edit .env with your credentials before running"
        exit 0
    fi
    
    echo "🚀 Starting container..."
    docker run -d \
        --name "$CONTAINER_NAME" \
        -p "${PORT}:8080" \
        --env-file .env \
        -v "$(pwd)/input:/app/input" \
        -v "$(pwd)/output:/app/output" \
        "${IMAGE_NAME}:${IMAGE_TAG}"
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Container started successfully!"
        echo ""
        echo "📊 Container Details:"
        echo "   - Name: $CONTAINER_NAME"
        echo "   - Port: $PORT"
        echo ""
        echo "🌐 Access the application at:"
        echo "   http://localhost:${PORT}"
        echo ""
        echo "📋 Useful commands:"
        echo "   - View logs: docker logs -f $CONTAINER_NAME"
        echo "   - Stop container: docker stop $CONTAINER_NAME"
        echo "   - Remove container: docker rm $CONTAINER_NAME"
        echo ""
        echo "⏳ Waiting for application to start..."
        sleep 5
        
        # Check if application is responding
        if curl -s http://localhost:${PORT}/_stcore/health > /dev/null; then
            echo "✅ Application is healthy!"
        else
            echo "⚠️  Application may still be starting..."
            echo "   Check logs with: docker logs -f $CONTAINER_NAME"
        fi
    else
        echo "❌ Failed to start container"
        exit 1
    fi
fi

echo ""
echo "✅ Build process complete!"

# Made with Bob

#!/bin/bash
# Build script for database Docker image
# Run this from the project root directory

echo "Building AI Automobile Database Docker image..."
docker build -t ai-automobile-db:latest -f docker/Dockerfile .

if [ $? -eq 0 ]; then
    echo "✅ Database image built successfully!"
    echo "Image name: ai-automobile-db:latest"
    echo ""
    echo "To run the container:"
    echo "  cd docker"
    echo "  docker-compose up -d"
else
    echo "❌ Build failed!"
    exit 1
fi


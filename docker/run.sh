#!/bin/bash
# Run script for database Docker container
# This script builds and runs the database container

echo "Building database image..."
docker build -t ai-automobile-db:latest -f docker/Dockerfile .

if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi

echo "Starting database container..."
cd docker
docker-compose up -d

if [ $? -eq 0 ]; then
    echo "✅ Database container is running!"
    echo ""
    echo "Container name: ai-automobile-db"
    echo "Volume name: docker_db-storage"
    echo ""
    echo "To view logs: docker logs ai-automobile-db"
    echo "To stop: cd docker && docker-compose down"
else
    echo "❌ Failed to start container!"
    exit 1
fi


#!/bin/bash

echo "🚀 Deploying Password Roast AI..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Build Docker image
echo "📦 Building Docker image..."
docker build -t password-roast-ai .

# Stop existing container if running
echo "🛑 Stopping existing container..."
docker stop password-roast-ai || true
docker rm password-roast-ai || true

# Run new container
echo "🎯 Starting new container..."
docker run -d \
    --name password-roast-ai \
    -p 5000:5000 \
    --env-file .env \
    --restart unless-stopped \
    password-roast-ai

echo "✅ Deployment complete! App is running on http://localhost:5000"
echo "📊 Check logs with: docker logs -f password-roast-ai"
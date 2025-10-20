#!/bin/bash

# Obsidian Chat - Docker Quick Start Script

set -e

echo "🚀 Obsidian Chat Docker Setup"
echo "=============================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Error: Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p vector_store data

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found."
    echo "📝 Please create a .env file with your configuration."
    echo "   You can copy .env.example if it exists, or create one manually."
    echo ""
    read -p "Do you want to continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Ask for Obsidian vault path
echo ""
echo "📚 Obsidian Vault Configuration"
echo "================================"
read -p "Enter the path to your Obsidian vault (or press Enter to skip): " VAULT_PATH

# Build and start
echo ""
echo "🔨 Building Docker image..."
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
else
    COMPOSE_CMD="docker compose"
fi

$COMPOSE_CMD build

echo ""
echo "🎬 Starting application..."
$COMPOSE_CMD up -d

echo ""
echo "✅ Done! Obsidian Chat is starting..."
echo ""
echo "📊 Check status:"
echo "   $COMPOSE_CMD ps"
echo ""
echo "📋 View logs:"
echo "   $COMPOSE_CMD logs -f"
echo ""
echo "🌐 Access the application:"
echo "   http://localhost:8000"
echo ""
echo "🛑 To stop the application:"
echo "   $COMPOSE_CMD down"
echo ""

if [ -n "$VAULT_PATH" ]; then
    echo "💡 Note: You specified a vault path: $VAULT_PATH"
    echo "   Make sure to add this to your docker-compose.yml volumes section:"
    echo "   - $VAULT_PATH:/vault:ro"
    echo ""
fi

# Wait a bit and check if container is running
sleep 3
if $COMPOSE_CMD ps | grep -q "Up"; then
    echo "✨ Application is running!"
else
    echo "⚠️  There might be an issue. Check logs with: $COMPOSE_CMD logs"
fi

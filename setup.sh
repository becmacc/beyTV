#!/bin/bash

# BeyTV Setup Script
# This script helps you install Docker and set up BeyTV

echo "🎬 BeyTV Setup Script"
echo "===================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed."
    echo ""
    echo "To install Docker Desktop on macOS:"
    echo "1. Visit: https://www.docker.com/products/docker-desktop/"
    echo "2. Download Docker Desktop for Mac"
    echo "3. Install and start Docker Desktop"
    echo "4. Run this script again"
    echo ""
    echo "Alternative - Install via Homebrew:"
    echo "   brew install --cask docker"
    echo ""
    exit 1
fi

echo "✅ Docker found!"

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

echo "✅ Docker is running!"
echo ""

# Navigate to the project directory
cd "$(dirname "$0")"

echo "🚀 Starting BeyTV services..."
echo ""

# Run docker compose
docker compose up -d

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ BeyTV services started successfully!"
    echo ""
    echo "📋 Service URLs:"
    echo "   • qBittorrent: http://localhost:8080"
    echo "   • Plex:        http://localhost:32400/web"
    echo "   • BeyFlow:     file://$(pwd)/beyflow.html"
    echo "   • Ratings:     http://localhost:8088 (after running ratings server)"
    echo "   • Indexer:     http://localhost:8089 (after running indexer)"
    echo ""
    echo "🎯 Quick Setup Steps:"
    echo "1. Open beyflow.html in your browser"
    echo "2. Configure qBittorrent (default login: admin/adminadmin)"
    echo "3. Set up Plex libraries pointing to ./media folder"
    echo "4. Configure .env file with OMDb API key and Plex token"
    echo "5. Run: ./start_ratings.sh (for ratings dashboard)"
    echo "6. Run: ./start_indexer.sh (for torrent indexer)"
    echo "7. Run: ./start_notifier.sh (for Telegram notifications)"
    echo "8. Run: ./setup_scheduler.sh (for automated scheduling)"
    echo "9. Start downloading and streaming!"
    echo ""
    echo "📂 Directory Structure:"
    echo "   • Downloads: ./downloads"
    echo "   • Media:     ./media"
    echo "   • Config:    ./config"
    echo "   • Ratings:   ./public"
    echo "   • Notifier:  ./notifier"
    echo "   • Indexer:   ./indexer"
    echo "   • Scheduler: ./scheduler"
    echo ""
    
    # Check if directories exist, create if not
    mkdir -p downloads media config/qb config/plex public
    echo "✅ Directory structure created!"
    
    # Setup Python environment for ratings (if Python is available)
    if command -v python3 &> /dev/null; then
        echo ""
        echo "🐍 Setting up Python environment for ratings..."
        
        if [ ! -d ".venv" ]; then
            python3 -m venv .venv
            echo "✅ Python virtual environment created"
        fi
        
        if [ -f ".venv/bin/activate" ]; then
            source .venv/bin/activate
            pip install -r requirements.txt > /dev/null 2>&1
            echo "✅ Python dependencies installed"
            
            if [ ! -f ".env" ]; then
                cp .env.sample .env
                echo "📝 Environment file created (.env) - Please configure with your API keys"
            fi
        fi
    else
        echo "⚠️  Python3 not found - ratings functionality will be unavailable"
    fi
    
    # Open BeyFlow in default browser
    if command -v open &> /dev/null; then
        echo ""
        echo "🌐 Opening BeyFlow dashboard..."
        open "$(pwd)/beyflow.html"
    fi
    
else
    echo ""
    echo "❌ Failed to start services. Check Docker and try again."
    echo ""
    echo "Debug commands:"
    echo "   docker compose logs"
    echo "   docker compose ps"
fi
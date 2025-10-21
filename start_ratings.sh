#!/bin/bash

# BeyTV Ratings Quick Start
echo "🎬 BeyTV Ratings System"
echo "======================="

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "📝 Creating .env from template..."
    cp .env.sample .env
    echo ""
    echo "⚠️  Please edit .env file with your actual API keys:"
    echo "   1. Get OMDb API key from: http://www.omdbapi.com/apikey.aspx"
    echo "   2. Get Plex token from your Plex server"
    echo "   3. Update PLEX_URL if using remote server"
    echo ""
    echo "Then run this script again."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment and install dependencies
echo "📦 Installing dependencies..."
source .venv/bin/activate
pip install -r requirements.txt > /dev/null 2>&1

# Check if OMDb API key is configured
source .env
if [ "$OMDB_API_KEY" = "your_omdb_api_key_here" ] || [ -z "$OMDB_API_KEY" ]; then
    echo "❌ OMDb API key not configured in .env file"
    echo "Please edit .env and add your actual OMDb API key"
    exit 1
fi

if [ "$PLEX_TOKEN" = "your_plex_token_here" ] || [ -z "$PLEX_TOKEN" ]; then
    echo "❌ Plex token not configured in .env file"
    echo "Please edit .env and add your actual Plex token"
    exit 1
fi

# Generate ratings
echo "⭐ Generating ratings from Plex + OMDb..."
python rss_generator.py

if [ $? -eq 0 ]; then
    echo "✅ Ratings generated successfully!"
    echo ""
    echo "📁 Output files:"
    echo "   • public/index.html - Ratings dashboard"
    echo "   • public/rss.xml - RSS feed"
    echo "   • public/ratings.csv - CSV export"
    echo ""
    
    # Start local server
    echo "🌐 Starting ratings server on http://localhost:8088..."
    echo "Press Ctrl+C to stop the server"
    echo ""
    python -m http.server 8088 -d public
else
    echo "❌ Failed to generate ratings. Check your configuration."
fi
#!/bin/bash

# BeyTV Indexer Quick Start
echo "🔍 BeyTV Torrent Indexer"
echo "========================"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "📝 Creating .env from template..."
    cp .env.sample .env
    echo ""
    echo "⚠️  Please edit .env file with your qBittorrent credentials:"
    echo "   1. Update QB_USER and QB_PASS if changed from defaults"
    echo "   2. Configure FEEDS with your preferred RSS sources"
    echo "   3. Set CATEGORY for auto-categorization"
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

# Check if qBittorrent credentials are configured
source .env
if [ "$QB_USER" = "admin" ] && [ "$QB_PASS" = "adminadmin" ]; then
    echo "⚠️  Using default qBittorrent credentials"
    echo "Consider changing the default password in qBittorrent settings"
fi

# Test indexer
echo "🔍 Running torrent indexer..."
cd indexer
python indexer.py

if [ $? -eq 0 ]; then
    echo "✅ Indexer completed successfully!"
    echo ""
    echo "📁 Output files:"
    echo "   • feeds/latest.json - JSON feed of torrents"
    echo "   • feeds/index.html - Human-readable view"
    echo ""
    
    # Check if feeds were created
    if [ -f "feeds/index.html" ]; then
        echo "🌐 Starting indexer feed server on http://localhost:8089..."
        echo "Press Ctrl+C to stop the server"
        echo ""
        python -m http.server 8089 -d feeds
    else
        echo "❌ No feeds were generated. Check your RSS sources."
    fi
    
    echo ""
    echo "🔄 To set up automatic indexing:"
    echo "   Add this to your crontab (crontab -e):"
    echo "   */30 * * * * cd $(pwd) && source ../.venv/bin/activate && python indexer.py >/tmp/beytv_indexer.log 2>&1"
    
else
    echo "❌ Failed to run indexer. Check your configuration."
fi
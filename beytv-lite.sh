#!/bin/bash

# BeyTV Lite - Conservative setup for limited resources
# This script provides manual control over downloads

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

case "${1:-help}" in
    "setup")
        echo "🚀 Setting up BeyTV Lite (Conservative Mode)"
        
        # Create directories
        mkdir -p downloads media/{movies,tv} config/{qb,plex} public
        
        # Start only essential services
        docker compose up -d
        
        # Create conservative indexer config
        cat > indexer/.env << EOF
QB_URL=http://localhost:8080
QB_USER=admin
QB_PASS=adminadmin
FEEDS=https://yts.mx/rss
CATEGORY=movies
LIMIT=5
AUTO_ADD=false
EOF
        
        echo "✅ BeyTV Lite setup complete!"
        echo "📊 Dashboard: file://$PWD/beyflow.html"
        echo "🔽 qBittorrent: http://localhost:8080"
        echo "🎥 Plex: http://localhost:32400/web"
        echo ""
        echo "💡 Use './beytv-lite.sh manual-add' to browse and manually select downloads"
        ;;
        
    "manual-add")
        echo "🔍 Fetching latest content (no auto-download)..."
        cd indexer
        python indexer.py --no-auto
        echo "📋 Browse feeds/index.html to manually select what to download"
        open feeds/index.html 2>/dev/null || echo "Open feeds/index.html in your browser"
        ;;
        
    "start-download")
        echo "▶️  Starting qBittorrent only"
        docker compose start qbittorrent
        ;;
        
    "stop-download")
        echo "⏹️  Stopping qBittorrent"
        docker compose stop qbittorrent
        ;;
        
    "status")
        echo "📊 BeyTV Lite Status:"
        docker compose ps
        echo ""
        if [ -f "indexer/feeds/latest.json" ]; then
            echo "📋 Latest indexed content:"
            python3 -c "
import json
with open('indexer/feeds/latest.json') as f:
    items = json.load(f)
    for i, item in enumerate(items[:3], 1):
        print(f'{i}. {item[\"title\"]}')
"
        fi
        ;;
        
    "clean")
        echo "🧹 Cleaning up old downloads and cache..."
        docker system prune -f
        rm -rf downloads/.incomplete downloads/.tmp
        ;;
        
    "help"|*)
        echo "🎬 BeyTV Lite - Conservative Media Setup"
        echo ""
        echo "Usage: $0 <command>"
        echo ""
        echo "Commands:"
        echo "  setup          Setup BeyTV in conservative mode"
        echo "  manual-add     Browse available content (no auto-download)"
        echo "  start-download Start qBittorrent for manual downloads"
        echo "  stop-download  Stop qBittorrent to save resources"
        echo "  status         Show current status"
        echo "  clean          Clean up old files"
        echo ""
        echo "💡 This version requires manual selection of downloads"
        echo "   to avoid overwhelming your system with automatic downloads."
        ;;
esac
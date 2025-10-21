#!/bin/bash

echo "🎬 BeyTV - qBittorrent Edition Setup"
echo "======================================"

# Check if qBittorrent is running
if ! pgrep -f "qbittorrent" > /dev/null; then
    echo "⚠️  qBittorrent not detected running"
    echo "📝 Please start qBittorrent with Web UI enabled:"
    echo "   1. Open qBittorrent"
    echo "   2. Go to Tools → Preferences → Web UI"
    echo "   3. Enable 'Web User Interface'"
    echo "   4. Set port to 8080 (default)"
    echo "   5. Set username: admin, password: adminadmin"
    echo ""
fi

# Install Python requirements
echo "📦 Installing Python requirements..."
pip3 install -r requirements.txt

# Start the qBittorrent-integrated server
echo "🚀 Starting BeyTV with qBittorrent integration..."
echo "📍 Server will run on: http://localhost:8000"
echo "🌊 qBittorrent Web UI: http://localhost:8080"
echo ""

python3 main.py
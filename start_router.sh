#!/bin/bash

# BeyTV Storage Router Setup
echo "💾 BeyTV Storage Router"
echo "======================"
echo ""
echo "This will set up unified storage management across:"
echo "• SSD (fast local storage)"
echo "• HDD (bulk local storage)"  
echo "• Cloud (Google Drive, S3, etc.)"
echo ""

# Check platform
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "⚠️  macOS detected - Limited storage router functionality"
    echo "Storage router works best on Linux with mergerfs support"
    echo ""
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "📝 Creating .env from template..."
    cp .env.sample .env
    echo ""
    echo "⚠️  Please edit .env file with your storage paths:"
    echo "   1. Update SSD_PATH, HDD_PATH, CLOUD_PATH"
    echo "   2. Configure rclone remotes (rclone config)"
    echo "   3. Set Plex and qBittorrent credentials"
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

# Load environment
source .env

echo "📋 Current Storage Configuration:"
echo "================================="
cd router
python router.py --list
cd ..

echo ""
echo "🔧 Available Commands:"
echo "   • List storages:     cd router && python router.py --list"
echo "   • Switch to SSD:     cd router && python router.py --set ssd"
echo "   • Switch to HDD:     cd router && python router.py --set hdd"
echo "   • Switch to Cloud:   cd router && python router.py --set cloud"
echo ""

read -p "Would you like to set up storage routing now? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🗂️  Storage Setup Options:"
    echo "1) SSD (Fast local storage)"
    echo "2) HDD (Bulk local storage)"
    echo "3) Cloud (Remote storage via rclone)"
    echo "4) Advanced (mergerfs union - Linux only)"
    echo ""
    
    read -p "Select storage type (1-4): " -n 1 -r
    echo ""
    
    case $REPLY in
        1)
            echo "📀 Setting up SSD storage..."
            cd router && python router.py --set ssd
            ;;
        2)
            echo "💿 Setting up HDD storage..."
            cd router && python router.py --set hdd
            ;;
        3)
            echo "☁️  Setting up Cloud storage..."
            echo "Make sure rclone is configured first: rclone config"
            cd router && python router.py --set cloud
            ;;
        4)
            if [[ "$OSTYPE" == "linux-gnu"* ]]; then
                echo "🔗 Setting up mergerfs union..."
                cd router && sudo bash setup.sh
            else
                echo "❌ mergerfs union only supported on Linux"
            fi
            ;;
        *)
            echo "❌ Invalid selection"
            ;;
    esac
else
    echo "❌ Setup cancelled"
fi

echo ""
echo "💾 Storage router ready!"
echo ""
echo "📚 Documentation:"
echo "   • Linux users: Install mergerfs for drive pooling"
echo "   • Cloud users: Configure rclone first (rclone config)"
echo "   • Advanced: See router/README.txt for automation options"
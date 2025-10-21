#!/bin/bash

# BeyTV Notifier Quick Start
echo "📱 BeyTV Telegram Notifier"
echo "========================="

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "📝 Creating .env from template..."
    cp .env.sample .env
    echo ""
    echo "⚠️  Please edit .env file with your Telegram bot credentials:"
    echo "   1. Create Telegram bot: https://t.me/BotFather"
    echo "   2. Get bot token from BotFather"
    echo "   3. Send message to your bot and get chat ID from:"
    echo "      https://api.telegram.org/bot<TOKEN>/getUpdates"
    echo "   4. Update PLEX_TOKEN if not already configured"
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

# Check if Telegram credentials are configured
source .env
if [ "$TELEGRAM_BOT_TOKEN" = "your_telegram_bot_token_here" ] || [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "❌ Telegram bot token not configured in .env file"
    echo "Please edit .env and add your actual Telegram bot token"
    exit 1
fi

if [ "$TELEGRAM_CHAT_ID" = "your_telegram_chat_id_here" ] || [ -z "$TELEGRAM_CHAT_ID" ]; then
    echo "❌ Telegram chat ID not configured in .env file"
    echo "Please edit .env and add your actual Telegram chat ID"
    exit 1
fi

if [ "$PLEX_TOKEN" = "your_plex_token_here" ] || [ -z "$PLEX_TOKEN" ]; then
    echo "❌ Plex token not configured in .env file"
    echo "Please edit .env and add your actual Plex token"
    exit 1
fi

# Test notification
echo "📱 Testing Telegram notification..."
cd notifier
python notify.py

if [ $? -eq 0 ]; then
    echo "✅ Notification system tested successfully!"
    echo ""
    echo "🔄 To set up automatic notifications:"
    echo "   Add this to your crontab (crontab -e):"
    echo "   */5 * * * * cd $(pwd)/notifier && source ../.venv/bin/activate && python notify.py >/tmp/beytv_notify.log 2>&1"
    echo ""
    echo "📱 You'll now receive Telegram messages when new content is added to Plex!"
else
    echo "❌ Failed to send test notification. Check your configuration."
fi
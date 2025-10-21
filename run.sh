#!/bin/bash
echo "🚀 Starting BeyTV Replit Edition..."
echo "🔧 Installing dependencies..."
pip install --user -r requirements.txt

echo "🌐 Starting web server..."
python3 main.py

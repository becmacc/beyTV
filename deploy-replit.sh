#!/bin/bash

# BeyTV Replit Deployment Script
echo "🎬 Deploying BeyTV to Replit..."

# Create Replit configuration files
echo "📝 Creating Replit configuration..."

# Create .replit file if it doesn't exist
if [ ! -f ".replit" ]; then
    cat > .replit << 'EOF'
[nix]
channel = "stable-22_11"

[deployment]
run = ["python3", "main.py"]

[[ports]]
localPort = 3000
externalPort = 80

[env]
PYTHONPATH = "/home/runner/${REPL_SLUG}"
PORT = "3000"
EOF
fi

# Create replit.nix if it doesn't exist
if [ ! -f "replit.nix" ]; then
    cat > replit.nix << 'EOF'
{ pkgs }: {
  deps = [
    pkgs.python3
    pkgs.python3Packages.pip
    pkgs.python3Packages.requests
    pkgs.python3Packages.feedparser
    pkgs.python3Packages.python-dotenv
  ];
}
EOF
fi

# Create pyproject.toml for modern Python dependency management
cat > pyproject.toml << 'EOF'
[tool.poetry]
name = "beytv-replit"
version = "1.0.0"
description = "BeyTV Replit Edition - Lightweight Media Dashboard"
authors = ["BeyTV Team"]

[tool.poetry.dependencies]
python = "^3.8"
requests = "^2.32.3"
feedparser = "^6.0.11"
python-dotenv = "^1.0.1"

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
EOF

# Create a simple run script
cat > run.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting BeyTV Replit Edition..."
echo "🔧 Installing dependencies..."
pip install --user -r requirements.txt

echo "🌐 Starting web server..."
python3 main.py
EOF

chmod +x run.sh

# Create minimal requirements.txt for Replit
cat > requirements.txt << 'EOF'
requests>=2.32.3
feedparser>=6.0.11
python-dotenv>=1.0.1
EOF

echo "✅ Replit deployment ready!"
echo ""
echo "📋 Next steps:"
echo "1. Create a new Python Repl on replit.com"
echo "2. Copy these files to your Repl:"
echo "   - main.py (main application)"
echo "   - .replit (Replit configuration)"
echo "   - replit.nix (dependencies)"
echo "   - requirements.txt (Python packages)"
echo "   - README_REPLIT.md (documentation)"
echo "3. Click 'Run' in Replit"
echo "4. Open the web preview to access your dashboard"
echo ""
echo "🎯 Your BeyTV will be accessible at: https://your-repl-name.your-username.repl.co"
echo "💡 This version is optimized for minimal resource usage - perfect for your setup!"
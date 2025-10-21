# GitHub Integration Script for Existing Replit AI Setup

This script helps you integrate BeyTV into your existing Replit AI project.

## 🔄 Integration Methods

### Method 1: Add as Submodule (Recommended)
If you want to keep BeyTV as a separate, updateable component:

```bash
# In your existing project directory
git submodule add https://github.com/yourusername/beytv-replit beytv
git commit -m "Add BeyTV dashboard as submodule"
```

### Method 2: Copy Files (Simple)
If you want to integrate directly into your existing structure:

```bash
# Copy BeyTV files to your project
cp -r beytv_setup/ your-project/beytv/
cd your-project
git add beytv/
git commit -m "Add BeyTV media dashboard"
```

### Method 3: Multi-Service Setup (Advanced)
Run multiple services in your existing Replit:

```python
# In your main.py or app.py
import threading
import subprocess

# Start your existing AI service
def start_ai_service():
    # Your existing AI code here
    pass

# Start BeyTV service
def start_beytv_service():
    subprocess.run(["python", "beytv/main.py"])

# Run both services
if __name__ == "__main__":
    ai_thread = threading.Thread(target=start_ai_service)
    beytv_thread = threading.Thread(target=start_beytv_service)
    
    ai_thread.start()
    beytv_thread.start()
    
    ai_thread.join()
    beytv_thread.join()
```

## 📋 Steps for GitHub Integration

1. **Prepare Repository**:
   ```bash
   cd /path/to/beytv_setup
   git add .
   git commit -m "Initial BeyTV Replit setup"
   ```

2. **Create GitHub Repository**:
   - Go to GitHub.com
   - Create new repository: `beytv-replit`
   - Don't initialize with README (we have one)

3. **Push to GitHub**:
   ```bash
   git remote add origin https://github.com/yourusername/beytv-replit.git
   git branch -M main
   git push -u origin main
   ```

4. **Connect to Your Existing Replit**:
   - In your Replit: go to Version Control
   - Import from GitHub: `yourusername/beytv-replit`
   - Or manually add files to existing project

## 🔧 Replit Configuration Updates

Update your existing `.replit` file to include BeyTV:

```toml
[nix]
channel = "stable-22_11"

[deployment]
run = ["python3", "main.py"]  # Your main app
deploymentTarget = "cloudrun"

# Multiple port support
[[ports]]
localPort = 3000   # Your AI service
externalPort = 80

[[ports]]
localPort = 3001   # BeyTV service
externalPort = 3001

[env]
# Your existing env vars
PYTHONPATH = "/home/runner/${REPL_SLUG}"
# Add BeyTV vars
BEYTV_PORT = "3001"
BEYTV_MODE = "lite"
```

## 🎯 Integration Patterns

### Pattern 1: Dashboard Tabs
Add BeyTV as a tab in your existing AI interface:

```html
<!-- In your existing interface -->
<div class="tabs">
  <div class="tab active">AI Chat</div>
  <div class="tab">Media Dashboard</div>
</div>

<div class="tab-content">
  <iframe src="http://localhost:3001" width="100%" height="600px"></iframe>
</div>
```

### Pattern 2: API Integration
Use BeyTV's API in your AI workflows:

```python
import requests

# Get content suggestions from BeyTV
beytv_api = "http://localhost:3001/api"
feeds = requests.get(f"{beytv_api}/feeds").json()

# Process with your AI
ai_recommendations = your_ai_model.process(feeds)
```

### Pattern 3: Embedded Widget
Add as a sidebar widget:

```css
.sidebar {
  width: 300px;
  height: 100vh;
}

.beytv-widget {
  height: 400px;
  border: none;
  border-radius: 8px;
}
```

```html
<div class="sidebar">
  <iframe class="beytv-widget" src="http://localhost:3001?embed=true"></iframe>
</div>
```

## 🚀 Quick Setup Commands

Run these commands to get everything ready for GitHub:

```bash
# Initialize and commit
git add .
git commit -m "BeyTV Replit integration ready"

# Create GitHub repo (replace with your username)
# Then connect:
git remote add origin https://github.com/YOURUSERNAME/beytv-replit.git
git push -u origin main
```

## 🔗 Connect to Existing Replit

Once on GitHub, in your existing Replit:

1. **Import Method**: Use "Import from GitHub" 
2. **Manual Method**: Copy files directly
3. **Submodule Method**: Add as git submodule

## 📱 Mobile Integration

BeyTV is mobile-responsive and will work seamlessly with your existing mobile AI interface.

---

**This integration gives you a lightweight media dashboard alongside your existing AI capabilities!** 🎬🤖
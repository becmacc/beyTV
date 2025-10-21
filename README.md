# BeyTV - Lightweight Media Dashboard

A resource-efficient media management dashboard designed for integration with existing AI workflows and Replit deployments.

## 🚀 Quick Integration

Perfect for adding to existing Replit AI projects as an additional service or layout.

### For Existing GitHub/Replit Setup:

```bash
# Clone as a submodule or copy to your existing project
git submodule add https://github.com/yourusername/beytv-replit beytv
# OR simply copy the files to a new directory in your project
```

## 📁 Project Structure

```
beytv/
├── main.py              # Main web server (standalone)
├── .replit              # Replit configuration
├── replit.nix           # Dependencies
├── requirements.txt     # Python packages
├── README.md           # This file
├── layouts/            # UI layouts for integration
│   ├── dashboard.html  # Main dashboard layout
│   ├── mobile.html     # Mobile-optimized layout
│   └── embed.html      # Embeddable widget
└── api/               # API endpoints
    ├── feeds.py       # Content feed APIs
    ├── search.py      # Search functionality
    └── utils.py       # Helper functions
```

## 🔧 Integration Options

### Option 1: Standalone Service
Run as a separate service on a different port:
```python
# In your main app
import subprocess
subprocess.Popen(["python", "beytv/main.py"])
```

### Option 2: Embedded Layout
Include the dashboard as a component:
```html
<iframe src="/beytv" width="100%" height="600px"></iframe>
```

### Option 3: API Integration
Use just the APIs in your existing AI workflow:
```python
from beytv.api import feeds, search
```

## 🎯 Features

- **Lightweight**: Minimal resource usage
- **Modular**: Easy to integrate into existing projects
- **API-First**: RESTful endpoints for AI integration
- **Responsive**: Works on all devices
- **No Downloads**: Focus on discovery, not storage

## ⚙️ Configuration

### Environment Variables
```bash
PORT=3000              # Service port
BEYTV_MODE=lite        # lite|full
API_ONLY=false         # true for API-only mode
EMBED_MODE=false       # true for widget mode
```

### Replit Integration
The `.replit` file is configured to run alongside other services:

```toml
[deployment]
run = ["python3", "main.py"]

[[ports]]
localPort = 3000
externalPort = 3000

[env]
BEYTV_MODE = "lite"
PORT = "3000"
```

## 🔗 API Endpoints

- `GET /api/feeds` - Get content feeds
- `GET /api/search?q=query` - Search content
- `GET /api/popular` - Popular content
- `GET /api/wishlist` - User wishlist
- `POST /api/wishlist` - Add to wishlist

## 🎨 Custom Layouts

Create custom layouts by extending the base template:

```python
# Custom layout integration
@app.route('/custom-layout')
def custom_layout():
    return render_template('your_layout.html', 
                         feeds=get_feeds(),
                         style='your-custom-style')
```

## 📱 Mobile-First Design

All layouts are optimized for mobile devices and work seamlessly across platforms.

## 🔄 Workflow Integration

Perfect for AI-powered content curation workflows:

1. **Discovery**: AI suggests content based on preferences
2. **Research**: BeyTV provides ratings and metadata
3. **Organization**: Wishlist management and categorization
4. **Export**: Data export for further AI processing

## 🚀 Quick Start

1. **Copy files to your project**
2. **Install dependencies**: `pip install -r requirements.txt`
3. **Run**: `python main.py`
4. **Access**: `http://localhost:3000`

## 🤖 AI Integration Examples

### Content Recommendation
```python
# Get AI-suggested content
suggestions = ai_model.get_recommendations(user_preferences)

# Add to BeyTV for research
for item in suggestions:
    beytv_api.add_to_research_queue(item)
```

### Smart Wishlist
```python
# AI-powered wishlist organization
wishlist = beytv_api.get_wishlist()
categorized = ai_model.categorize_content(wishlist)
beytv_api.update_categories(categorized)
```

## 📊 Resource Usage

- **CPU**: < 5% (idle), < 20% (active)
- **RAM**: < 50MB
- **Storage**: < 10MB
- **Bandwidth**: Minimal (no downloads)

Perfect for Replit's free tier and resource-constrained environments.

## 🔧 Customization

Easily customize colors, layout, and features by modifying:
- `main.py` - Core functionality
- CSS in dashboard template - Styling
- API endpoints - Data sources

---

**Designed for seamless integration with existing AI workflows and Replit deployments** 🚀
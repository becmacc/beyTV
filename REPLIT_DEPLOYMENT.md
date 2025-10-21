# 🚀 BeyTV - Replit Deployment Guide

## ✨ What You're Deploying
**Complete RSS + qBittorrent media management system with automatic torrent discovery**

### 🎯 Features Ready for Cloud:
- **📡 RSS Feeds**: YTS, EZTV, TorrentGalaxy, RARBG auto-discovery
- **🌊 qBittorrent Integration**: Real plugin searches and downloads  
- **📱 Remote Dashboard**: Access from any device, anywhere
- **🎬 Plex Integration**: Organized downloads via local client
- **⚡ Live Monitoring**: Real-time torrent status and speeds

## 🌐 Deploy to Replit (Recommended)

### Step 1: Import from GitHub
1. Go to [Replit.com](https://replit.com)
2. Click "Create Repl" → "Import from GitHub"
3. Enter: `https://github.com/becmacc/beyTV`
4. Click "Import from GitHub"

### Step 2: Configure Replit
1. Replit will detect Python and create `.replit` automatically
2. If not, create `.replit` file with:
```toml
language = "python3"
run = "python3 main.py"

[nix]
channel = "stable-22_11"

[deployment]
run = ["python3", "main.py"]
```

### Step 3: Deploy
1. Click "Run" button in Replit
2. Wait for dependencies to install (feedparser, requests, etc.)
3. Your BeyTV dashboard will be available at your Replit URL
4. Share the URL to access from any device!

## 🎬 How to Use After Deployment

### 📡 RSS Feeds (No Setup Required)
- **Automatic**: Latest movies/TV from YTS, EZTV, TorrentGalaxy
- **Click "RSS Feeds" tab**: Browse new releases instantly
- **Filter feeds**: Movies 1080p, 4K, TV Shows, Popular
- **One-click download**: Add to qBittorrent or Queue for Plex

### 🌊 qBittorrent Integration (Optional)
- **For direct downloads**: Connect your qBittorrent Web UI
- **Manual searches**: Use all your qBittorrent plugins
- **Live monitoring**: See download progress in real-time

### 🖥️ Local Client (For Plex)
- **Download local_client.py** from your repo
- **Run on Plex computer**: `python3 local_client.py`
- **Enter Replit URL**: When prompted
- **Automatic organization**: Files go to Movies/TV Shows folders

## 🌟 Deployment Advantages

### ☁️ Cloud Benefits:
- **Always Online**: 24/7 access from anywhere
- **No Local Resources**: Your computer doesn't need to run anything
- **Mobile Friendly**: Perfect interface for phones/tablets
- **Instant Sharing**: Send URL to family/friends for access
- **Auto-Updates**: Git push updates your deployment

### 🎯 Perfect Workflow:
1. **From Phone**: Browse RSS feeds → Click download
2. **Replit Magic**: Processes torrent automatically  
3. **Home Download**: Local client organizes for Plex
4. **Watch Anywhere**: Content appears in Plex library

## 🔧 Advanced Configuration

### Environment Variables (Optional)
Add to Replit Secrets:
```
QBT_HOST=your-home-ip
QBT_PORT=8080
QBT_USERNAME=admin
QBT_PASSWORD=your-password
```

### Custom RSS Feeds
Edit `main.py` RSSManager feeds dictionary:
```python
self.feeds = {
    'your_custom_feed': 'https://your-rss-url.com/feed.xml',
    # ... existing feeds
}
```

## 🎬 You're Ready!

**Your BeyTV system is now:**
✅ **Cloud-Deployed**: Access from anywhere  
✅ **RSS-Powered**: Automatic content discovery  
✅ **qBittorrent-Ready**: Real torrent integration  
✅ **Plex-Optimized**: Perfect file organization  
✅ **Mobile-Responsive**: Works on any device  

**Deploy now and revolutionize your media management!** 🚀
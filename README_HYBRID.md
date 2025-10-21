# 🎬 BeyTV Hybrid - Remote Dashboard + Local Downloads

**The perfect solution for limited resources: Browse anywhere, download locally!**

## 🚀 How It Works

1. **Dashboard runs on Replit** (accessible from anywhere, uses minimal resources)
2. **Downloads happen on your local machine** (your storage, your bandwidth)
3. **Queue downloads remotely** (from phone, work, anywhere)
4. **Downloads start automatically** when you're home

## ✨ Perfect for Your Situation

- ✅ **Minimal Replit usage** - just the browsing interface
- ✅ **No Replit storage limits** - downloads go to your machine
- ✅ **Access anywhere** - dashboard available 24/7
- ✅ **Old hardware friendly** - local client is lightweight
- ✅ **Queue from anywhere** - add downloads from your phone

## 🔧 Setup

### 1. Deploy Dashboard to Replit
1. Import this repo to Replit
2. Click "Run" 
3. Access your dashboard at the provided URL

### 2. Install Local Client (On Your Machine)
```bash
# Download the local client
curl -O https://raw.githubusercontent.com/becmacc/beyTV/main/local_client.py

# Run it (keeps running in background)
python local_client.py
```

### 3. Connect & Use
1. Dashboard auto-detects when local client is running
2. Browse content on Replit dashboard
3. Click "Queue Download" on items you want
4. Downloads automatically start on your local machine

## 📱 Usage Workflow

### From Anywhere (Phone, Work, etc.)
1. Open your Replit BeyTV dashboard
2. Search/browse for content
3. Add interesting items to download queue
4. Continue with your day

### At Home
1. Local client automatically receives queued downloads
2. Downloads start in qBittorrent (if installed) or as magnet files
3. Files save to `~/Downloads/BeyTV/`

## 🎯 Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Replit        │    │   Your Phone/    │    │  Your Local     │
│   Dashboard     │◄───┤   Work Computer  │    │  Machine        │
│   (Browsing)    │    │   (Queue Items)  │    │  (Downloads)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                                               ▲
         │              Internet                         │
         └───────────────────────────────────────────────┘
              Download requests sent when client online
```

## 🔧 Local Client Features

- **Auto-detection** - Dashboard knows when client is online
- **qBittorrent integration** - Automatically adds torrents if available
- **Fallback handling** - Saves magnet links if qBittorrent not running
- **Download logging** - Keeps track of all download attempts
- **Status page** - View client status at `http://localhost:8888`

## 📊 Resource Usage

### Replit (Remote Dashboard)
- **CPU**: < 5% (just serving web pages)
- **RAM**: < 30MB (minimal web server)
- **Storage**: < 5MB (no media files)
- **Bandwidth**: Minimal (just browsing)

### Local Machine
- **CPU**: < 2% (lightweight client)
- **RAM**: < 20MB (simple HTTP server)
- **Storage**: Your choice (downloads go where you want)
- **Bandwidth**: Only when you actually download

## 🌐 Access Methods

- **Desktop**: Full dashboard with all features
- **Mobile**: Responsive interface for quick browsing
- **Work Computer**: Queue downloads for later
- **API**: Programmatic access for automation

## 🔒 Security & Privacy

- **Local downloads** - Content never touches Replit servers
- **Private communication** - Direct connection between dashboard and your machine
- **No cloud storage** - Everything stays on your hardware
- **Optional qBittorrent** - Use your existing setup

## 📋 File Structure

```
BeyTV/
├── main.py              # Replit dashboard server
├── local_client.py      # Local download client
├── .replit             # Replit configuration
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## 🎬 Example Workflow

**Monday (at work):**
- Browse BeyTV dashboard on phone
- Queue 3 movies for weekend
- Close browser, continue with day

**Friday evening:**
- Get home, local client auto-receives queued items
- Downloads start automatically in qBittorrent
- Watch immediately or over the weekend

## 🔧 Troubleshooting

### Local Client Won't Connect
```bash
# Check if port 8888 is available
netstat -an | grep 8888

# Restart local client
python local_client.py
```

### Downloads Not Starting
1. Make sure qBittorrent is running on port 8080
2. Check `~/Downloads/BeyTV/` for magnet files
3. Verify local client shows "Connected" in dashboard

### Can't Access Dashboard
- Check Replit isn't sleeping
- Refresh the Replit page to wake it up

## 🚀 Advanced Features

### Custom Download Location
Edit `local_client.py` and change:
```python
downloads_dir = Path.home() / "Downloads" / "BeyTV"
# to
downloads_dir = Path("/your/custom/path")
```

### Multiple Machines
Run local client on multiple machines - downloads will go to whichever is online.

### Automation
Use the API endpoints for custom automation:
```bash
# Queue download via API
curl -X POST http://localhost:8888/download \
  -H "Content-Type: application/json" \
  -d '{"title":"Movie Name","url":"magnet:..."}'
```

---

**Perfect for enjoying media discovery without overwhelming your resources!** 🎬✨

### Quick Start Commands
```bash
# On Replit: Just click "Run"
# On your machine:
python local_client.py
```
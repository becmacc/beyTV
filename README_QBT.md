# 🎬 BeyTV - qBittorrent Edition
**Complete Media Management with Real Torrent Downloads**

Transform your media setup into a powerful remote-controlled download station using qBittorrent's search plugins and your Plex library.

## ✨ What This Does

🌊 **Real Torrent Search**: Search across all your qBittorrent plugins from any device  
🎯 **Dual Download Options**: Add to qBittorrent directly OR queue for organized Plex downloads  
📱 **Remote Control**: Manage downloads from anywhere with a beautiful web interface  
🎬 **Plex Integration**: Automatic file organization for Movies and TV Shows  
⚡ **Live Monitoring**: Real-time torrent status, speeds, and progress tracking  

## 🚀 Quick Start

### 1. Setup qBittorrent
```bash
# Install qBittorrent with Web UI
# Enable Web UI in Tools → Preferences → Web UI
# Set: localhost:8080, username: admin, password: adminadmin
```

### 2. Install Search Plugins
In qBittorrent:
- Go to View → Search Engine
- Install plugins for your favorite torrent sites
- Enable all the plugins you want to search

### 3. Run BeyTV
```bash
git clone https://github.com/becmacc/beyTV.git
cd beyTV
./start_beytv_qbt.sh
```

### 4. Access Dashboard
Open http://localhost:8000 in any browser

## 📱 How To Use

### 🔍 Search Torrents
1. Type your search in the box
2. Click "Search All Plugins" 
3. Results from ALL your qBittorrent plugins appear
4. See seeders, file sizes, sources instantly

### 🌊 Download Options
**Option A - Direct qBittorrent:**
- Click "Add to qBittorrent"
- Downloads immediately to qBittorrent's default folder
- Monitor in the "Active Torrents" tab

**Option B - Organized Plex Downloads:**
- Click "Queue for Plex" 
- Runs local_client.py to organize files properly
- Automatic Movies/TV Shows folder sorting
- Perfect for Plex libraries

### 📊 Monitor Everything
- **Search Results Tab**: Browse and download torrents
- **Active Torrents Tab**: Live qBittorrent status
- **Download Queue Tab**: Files queued for Plex

## 🔧 Technical Architecture

```
┌─────────────────┐    ┌───────────────────┐    ┌─────────────────┐
│   Web Browser   │◄──►│  BeyTV Dashboard  │◄──►│   qBittorrent   │
│   (Any Device)  │    │   (Replit/Local)  │    │  + All Plugins  │
└─────────────────┘    └───────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  Local Client   │
                       │ (Plex Computer) │
                       └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  Plex Library   │
                       │ Movies/TV Shows │
                       └─────────────────┘
```

## 🎯 Real-World Workflow

1. **From Phone**: Search "Breaking Bad S01E01" on your BeyTV dashboard
2. **Plugin Magic**: All your qBittorrent plugins search simultaneously  
3. **Choose Quality**: Pick from results (1080p, 720p, different sources)
4. **Smart Download**: 
   - "Add to qBittorrent" = immediate download
   - "Queue for Plex" = organized, library-ready download
5. **Watch**: Files appear perfectly organized in Plex

## 🌟 Advanced Features

### Multi-Plugin Search
- Searches ALL enabled qBittorrent plugins at once
- No need to visit multiple torrent sites
- Unified results with seeders/size comparison

### Hybrid Downloads
- qBittorrent direct downloads for seeding
- Local client downloads for Plex organization
- Both methods work together seamlessly

### Live Status Monitoring
- Real-time download speeds
- Progress percentages
- Seeding ratios
- Connection status for all components

## 🔐 Security Notes

- qBittorrent Web UI should be password protected
- Only enable plugins from trusted sources
- Consider VPN for torrent downloads
- Dashboard can be password protected (see main.py)

## 🛠 Troubleshooting

### qBittorrent Not Connecting
```bash
# Check qBittorrent is running with Web UI
# Default URL: http://localhost:8080
# Default credentials: admin / adminadmin
```

### No Search Results
```bash
# Install search plugins in qBittorrent
# View → Search Engine → Install plugins
# Enable the plugins you want to use
```

### Local Client Issues
```bash
# Make sure local_client.py is running
# Check it can reach your BeyTV dashboard URL
python3 local_client.py
```

## 📂 File Structure

```
beyTV/
├── main_qbt.py           # qBittorrent-integrated server
├── local_client.py       # Plex-optimized downloader
├── start_beytv_qbt.sh   # Quick start script
├── requirements.txt      # Python dependencies
└── README_QBT.md        # This file
```

## 🎬 Perfect for Plex Users

This setup gives you:
- **Remote Control**: Download from anywhere
- **Plugin Power**: Access to all torrent sources  
- **Auto Organization**: Files land in correct Plex folders
- **Quality Control**: Choose your preferred resolution/source
- **No Manual Work**: Set it and forget it

## 🚀 Deployment Options

### Local Network
Run on any computer on your network for family access

### Cloud Hosting  
Deploy to Replit/Heroku for internet-wide access

### Hybrid Setup
Dashboard in cloud + qBittorrent/Plex at home = best of both worlds

---

**Ready to revolutionize your media downloads?**
⭐ Star this repo | 🍴 Fork for customization | 📝 Report issues
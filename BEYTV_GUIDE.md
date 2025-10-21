# 🎬 BeyTV - Complete Setup Guide

BeyTV is your personal download and streaming dashboard that combines qBittorrent, Plex, and IMDb/Rotten Tomatoes ratings into one beautiful interface using BeyFlow.

## ✨ Features

- **📥 qBittorrent Integration** - Download management
- **🎥 Plex Media Server** - Stream your content  
- **⭐ Ratings Dashboard** - IMDb & Rotten Tomatoes ratings via OMDb
- **📊 RSS Feed** - Subscribe to latest ratings
- **📱 Telegram Notifications** - Get notified of new content
- **🔍 Torrent Indexer** - Automated torrent discovery from RSS feeds
- **⏰ Smart Scheduler** - Time-based automation (midnight-6AM downloads)
- **💾 Storage Router** - Unified SSD/HDD/Cloud storage management
- **🎛️ Unified Control** - Single command interface
- **📱 Responsive Design** - Works on all devices
- **🌐 Remote Access** - Access from anywhere

## 📋 Quick Start

### 1. Install Docker (if not already installed)

**Option A: Docker Desktop (Recommended)**
1. Visit: https://www.docker.com/products/docker-desktop/
2. Download Docker Desktop for Mac
3. Install and start Docker Desktop

**Option B: Homebrew**
```bash
brew install --cask docker
```

### 2. Run BeyTV Setup

**Quick Start (Recommended):**
```bash
./beytv.sh setup
```

**Or use individual scripts:**
```bash
./setup.sh
```

This script will:
- Check Docker installation
- Start qBittorrent and Plex services
- Create necessary directories
- Set up Python environment
- Open BeyFlow dashboard

### 3. Manual Setup (Alternative)

```bash
# Start Docker services
docker compose up -d

# Start ratings dashboard
./start_ratings.sh

# Setup notifications
./start_notifier.sh

# Open BeyFlow dashboard
open beyflow.html
```

## 🌐 Service URLs

- **BeyFlow Dashboard**: `file://[path]/beyflow.html`
- **qBittorrent**: http://localhost:8080
- **Plex**: http://localhost:32400/web
- **Ratings Dashboard**: http://localhost:8088
- **Torrent Indexer**: http://localhost:8089

## ⚙️ Initial Configuration

### qBittorrent Setup
1. Open qBittorrent (http://localhost:8080)
2. Default login: `admin` / `adminadmin`
3. Go to Settings → Downloads
4. Set default save path to: `/media`
5. Create categories: `movies`, `tv`

### Plex Setup
1. Open Plex (http://localhost:32400/web)
2. Create account or sign in
3. Add libraries:
   - Movies: `/media/movies`
   - TV Shows: `/media/tv`
4. Let Plex scan your media

### Ratings Setup
1. Get OMDb API key: http://www.omdbapi.com/apikey.aspx
2. Get Plex token from your server settings
3. Configure `.env` file:
   ```bash
   cp .env.sample .env
   # Edit .env with your API keys
   ```
### Notifications Setup
1. Create Telegram bot via BotFather: https://t.me/BotFather
2. Get bot token from BotFather
3. Send message to your bot and get chat ID:
   ```bash
   https://api.telegram.org/bot<TOKEN>/getUpdates
   ```
4. Configure `.env` file with Telegram credentials
5. Run notification system:
   ```bash
   ./start_notifier.sh
   ```
6. Set up cron for automatic notifications:
   ```bash
   # Add to crontab (crontab -e):
   */5 * * * * cd /path/to/beytv_setup/notifier && source ../.venv/bin/activate && python notify.py
   ```

## 📁 Directory Structure

```
beytv_setup/
├── docker-compose.yml      # Docker services configuration
├── beyflow.html           # Main dashboard
├── beyflow-config.js      # Configuration for remote servers
├── beytv.sh              # Main control script
├── setup.sh              # Automated setup script
├── start_ratings.sh      # Ratings system starter
├── start_notifier.sh     # Notification system starter
├── start_indexer.sh      # Indexer system starter
├── start_router.sh       # Storage router starter
├── setup_scheduler.sh    # Scheduler setup
├── rss_generator.py      # Ratings generator
├── requirements.txt      # Python dependencies
├── .env.sample          # Environment configuration template
├── downloads/           # qBittorrent downloads
├── media/              # Plex media library
│   ├── movies/
│   └── tv/
├── config/             # Service configurations
│   ├── qb/             # qBittorrent config
│   └── plex/           # Plex config
├── public/             # Ratings dashboard output
│   ├── index.html      # Ratings viewer
│   ├── rss.xml         # RSS feed
│   └── ratings.csv     # CSV export
├── notifier/           # Telegram notification system
│   ├── notify.py       # Notification script
│   ├── requirements.txt # Notifier dependencies
│   ├── .env.sample     # Notifier config template
│   └── state.json      # Notification state (auto-created)
├── indexer/            # Torrent RSS indexer
│   ├── indexer.py      # Indexer script
│   ├── requirements.txt # Indexer dependencies
│   ├── .env.sample     # Indexer config template
│   └── feeds/          # Generated feeds (auto-created)
│       ├── latest.json
│       └── index.html
├── scheduler/          # Time-based automation
│   ├── start_qb.sh     # Start qBittorrent
│   ├── stop_qb.sh      # Stop qBittorrent
│   ├── day_throttle.sh # Speed throttling
│   ├── crontab.txt     # Cron configuration
│   └── README.txt      # Scheduler documentation
└── router/             # Storage management
    ├── router.py       # Storage router script
    ├── setup.sh        # Storage setup
    ├── requirements.txt # Router dependencies
    ├── .env.sample     # Router config template
    └── README.txt      # Router documentation
```

## 🎯 Usage Workflow

### Using BeyTV Control Script (Recommended)

```bash
# Start everything
./beytv.sh start

# Check status
./beytv.sh status

# Start specific components
./beytv.sh ratings    # Ratings dashboard
./beytv.sh notify     # Telegram notifications
./beytv.sh indexer    # Torrent indexer
./beytv.sh scheduler  # Automated scheduling
./beytv.sh router     # Storage routing

# Stop/restart services  
./beytv.sh stop
./beytv.sh restart

# View logs
./beytv.sh logs
```

### Manual Workflow

1. **Download**: Use qBittorrent to download torrents
2. **Organize**: Files automatically go to `/media` directory
3. **Stream**: Plex automatically detects and organizes media
4. **Rate**: View IMDb/RT ratings in the dashboard
5. **Notify**: Get Telegram alerts for new content
6. **Enjoy**: Access everything through BeyFlow dashboard

## 🔧 Advanced Configuration

### Remote Server Setup

1. Update `beyflow-config.js`:
```javascript
// Change current to 'remote'
current: 'remote'

// Update remote URLs
remote: {
    qbittorrent: 'http://YOUR_SERVER_IP:8080',
    plex: 'http://YOUR_SERVER_IP:32400/web'
}
```

2. Update docker-compose.yml ports if needed:
```yaml
ports:
  - "0.0.0.0:8080:8080"    # qBittorrent
  - "0.0.0.0:32400:32400"  # Plex
```

### Custom Categories
Add these categories in qBittorrent for better organization:
- `movies` → `/media/movies`
- `tv` → `/media/tv`
- `music` → `/media/music`
- `books` → `/media/books`

## 🛠️ Troubleshooting

### Services Won't Start
```bash
# Check Docker status
docker info

# View service logs
docker compose logs

# Restart services
docker compose restart
```

### Can't Access Services
- Check if ports 8080 and 32400 are available
- Verify firewall settings
- For remote access, ensure ports are exposed

### BeyFlow Dashboard Issues
- Check browser console for errors
- Verify service URLs in `beyflow-config.js`
- Try refreshing the page

## 📱 Mobile Access

BeyFlow is responsive and works great on mobile devices. For remote access:

1. Set up port forwarding on your router
2. Use your public IP or domain name
3. Configure HTTPS for secure access (recommended)

## 🔒 Security Notes

- Change default qBittorrent password
- Use VPN for torrenting
- Consider HTTPS reverse proxy for remote access
- Keep services updated

## 🚀 Optional Enhancements

### Automatic Library Refresh
Add this to your download completion script:
```bash
curl -X POST "http://localhost:32400/library/all/refresh"
```

### Sonarr/Radarr Integration
For automated TV show and movie management, consider adding:
- Sonarr (TV shows)
- Radarr (Movies)
- Jackett (Indexer)

### Reverse Proxy
Use nginx or Traefik for:
- Single domain access
- HTTPS/SSL certificates
- Authentication

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section
2. Review Docker and service logs
3. Verify network connectivity
4. Check file permissions

---

**Enjoy your BeyTV setup! 🎬🍿**
#!/usr/bin/env python3
"""
BeyTV Local Client - Downloads files for Plex from Replit dashboard
Connects to your Replit BeyTV dashboard and downloads files locally for Plex
"""

import os
import time
import json
import subprocess
import webbrowser
from pathlib import Path
from urllib.parse import urlparse
import shutil

# Optional imports
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("⚠️  requests not available - install with: pip install requests")

class BeyTVLocalClient:
    def __init__(self):
        self.setup_config()
        
    def setup_config(self):
        """Setup client configuration"""
        print("🎬 BeyTV Local Client for Plex")
        print("=" * 50)
        
        # Get Replit URL
        config_file = Path.home() / ".beytv_config.json"
        if config_file.exists():
            with open(config_file) as f:
                config = json.load(f)
                self.replit_url = config.get('replit_url', '')
        else:
            self.replit_url = ''
            
        if not self.replit_url:
            self.replit_url = input("📱 Enter your Replit BeyTV URL: ").strip()
            # Save for next time
            with open(config_file, 'w') as f:
                json.dump({'replit_url': self.replit_url}, f)
        
        # Setup download paths for Plex
        self.setup_plex_paths()
        
        self.client_id = "plex_client_1"
        print(f"🌐 Connected to: {self.replit_url}")
        print(f"📁 Movies folder: {self.movies_path}")
        print(f"📺 TV Shows folder: {self.tv_path}")
        
    def setup_plex_paths(self):
        """Setup Plex media directories"""
        # Default Plex-friendly structure
        base_path = Path.home() / "Downloads" / "BeyTV"
        
        print(f"\n📁 Setting up Plex media directories...")
        print(f"📍 Base path: {base_path}")
        
        # Create Plex-friendly directory structure
        self.movies_path = base_path / "movies"
        self.tv_path = base_path / "tv"
        self.downloads_path = base_path
        
        # Create directories
        self.movies_path.mkdir(parents=True, exist_ok=True)
        self.tv_path.mkdir(parents=True, exist_ok=True)
        
        print(f"✅ Movies: {self.movies_path}")
        print(f"✅ TV Shows: {self.tv_path}")
        
    def check_in_with_server(self):
        """Register with the Replit server"""
        if not HAS_REQUESTS:
            print("❌ Cannot connect to server - requests module not available")
            return False
            
        try:
            available_space = shutil.disk_usage(self.downloads_path)[2]  # Free space
            data = {
                'client_id': self.client_id,
                'downloads_path': str(self.downloads_path),
                'available_space': available_space,
                'status': 'online'
            }
            
            response = requests.post(
                f"{self.replit_url}/api/client/checkin",
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('queued_downloads', [])
            return []
            
        except Exception as e:
            print(f"❌ Failed to check in with server: {e}")
            return []

    def categorize_content(self, title):
        """Determine if content is movie or TV show"""
        title_lower = title.lower()
        
        # TV show indicators
        tv_indicators = ['s01e', 's02e', 's03e', 'season', 'episode', 'ep', 'x264-', 'hdtv']
        if any(indicator in title_lower for indicator in tv_indicators):
            return 'tv'
        
        # Default to movie
        return 'movie'

    def get_download_path(self, title):
        """Get appropriate download path based on content type"""
        content_type = self.categorize_content(title)
        
        if content_type == 'tv':
            return self.tv_path
        else:
            return self.movies_path

    def download_file(self, download_item):
        """Download a file locally for Plex"""
        print(f"📥 Starting download: {download_item['title']}")
        
        url = download_item['url']
        title = download_item['title']
        download_id = download_item['id']
        
        # Get appropriate path for Plex
        download_path = self.get_download_path(title)
        
        # Sanitize filename
        safe_filename = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
        
        if url.startswith('magnet:'):
            # Handle magnet links
            return self.download_magnet(url, safe_filename, download_id, download_path)
        else:
            # Handle direct downloads
            return self.download_direct(url, safe_filename, download_id, download_path)

    def download_magnet(self, magnet_url, filename, download_id, download_path):
        """Download magnet link using qBittorrent or save magnet file"""
        try:
            self.update_download_status(download_id, 'downloading')
            
            # Try qBittorrent API first
            if self.add_to_qbittorrent(magnet_url, download_path):
                print(f"✅ Added to qBittorrent: {filename}")
                return True
            
            # Fallback: save magnet file
            magnet_file = download_path / f"{filename}.magnet"
            with open(magnet_file, 'w') as f:
                f.write(f"# BeyTV Download for Plex\n")
                f.write(f"# Title: {filename}\n")
                f.write(f"# Path: {download_path}\n\n")
                f.write(magnet_url)
            
            print(f"💾 Saved magnet file: {magnet_file}")
            print(f"💡 Open with your torrent client to download to Plex folder")
            
            # Try to open with default application
            self.open_magnet_file(magnet_file)
            
            self.update_download_status(download_id, 'completed', str(magnet_file))
            return True
            
        except Exception as e:
            print(f"❌ Failed to download {filename}: {e}")
            self.update_download_status(download_id, 'failed')
            return False

    def add_to_qbittorrent(self, magnet_url, download_path):
        """Try to add magnet to qBittorrent"""
        if not HAS_REQUESTS:
            return False
            
        try:
            # Login to qBittorrent
            session = requests.Session()
            login_url = "http://localhost:8080/api/v2/auth/login"
            login_data = {"username": "admin", "password": "adminadmin"}
            
            login_response = session.post(login_url, data=login_data, timeout=5)
            if login_response.status_code != 200:
                return False
            
            # Add torrent
            add_url = "http://localhost:8080/api/v2/torrents/add"
            add_data = {
                "urls": magnet_url, 
                "savepath": str(download_path),
                "category": "plex"
            }
            
            add_response = session.post(add_url, data=add_data, timeout=10)
            return add_response.status_code == 200
            
        except Exception:
            return False

    def open_magnet_file(self, magnet_file):
        """Try to open magnet file with default application"""
        try:
            if os.name == 'nt':  # Windows
                os.startfile(str(magnet_file))
            elif os.name == 'posix':  # macOS/Linux
                subprocess.run(['open', str(magnet_file)], check=False)
        except:
            pass

    def download_direct(self, url, filename, download_id, download_path):
        """Download direct URL"""
        try:
            filepath = download_path / filename
            self.update_download_status(download_id, 'downloading')
            
            # Use wget, curl, or requests
            if shutil.which('wget'):
                cmd = ['wget', '-O', str(filepath), url]
                result = subprocess.run(cmd, capture_output=True)
                success = result.returncode == 0
            elif shutil.which('curl'):
                cmd = ['curl', '-L', '-o', str(filepath), url]
                result = subprocess.run(cmd, capture_output=True)
                success = result.returncode == 0
            elif HAS_REQUESTS:
                success = self.download_with_requests(url, filepath)
            else:
                print(f"❌ No download method available")
                return False
            
            if success:
                print(f"✅ Downloaded for Plex: {filepath}")
                self.update_download_status(download_id, 'completed', str(filepath))
                return True
            else:
                self.update_download_status(download_id, 'failed')
                return False
                
        except Exception as e:
            print(f"❌ Download failed: {e}")
            self.update_download_status(download_id, 'failed')
            return False

    def download_with_requests(self, url, filepath):
        """Download using requests"""
        try:
            with requests.get(url, stream=True, timeout=30) as r:
                r.raise_for_status()
                with open(filepath, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            return True
        except Exception:
            return False

    def update_download_status(self, download_id, status, local_path=None):
        """Update download status on server"""
        if not HAS_REQUESTS:
            return
            
        try:
            data = {
                'download_id': download_id,
                'status': status,
                'local_path': local_path
            }
            requests.post(
                f"{self.replit_url}/api/client/update-status",
                json=data,
                timeout=5
            )
        except Exception as e:
            print(f"❌ Failed to update status: {e}")

    def run(self):
        """Main loop"""
        print(f"\n🚀 BeyTV Local Client for Plex started!")
        print(f"📱 Control downloads from: {self.replit_url}")
        print(f"📁 Files will be organized for Plex in:")
        print(f"   🎬 Movies: {self.movies_path}")
        print(f"   📺 TV Shows: {self.tv_path}")
        print(f"⏹️  Press Ctrl+C to stop")
        print("=" * 60)
        
        while True:
            try:
                # Check in and get downloads
                queued_downloads = self.check_in_with_server()
                
                if queued_downloads:
                    print(f"📥 Found {len(queued_downloads)} queued downloads")
                    for download in queued_downloads:
                        self.download_file(download)
                elif queued_downloads is not None:
                    print("🟢 Connected - No downloads queued")
                else:
                    print("🔴 Cannot connect to Replit dashboard")
                
                # Wait before next check
                time.sleep(15)
                
            except KeyboardInterrupt:
                print("\n🛑 Stopping BeyTV Local Client...")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                time.sleep(30)

if __name__ == "__main__":
    if not HAS_REQUESTS:
        print("❌ Missing required dependency!")
        print("Run: pip install requests")
        exit(1)
        
    client = BeyTVLocalClient()
    client.run()
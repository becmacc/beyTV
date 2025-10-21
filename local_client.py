#!/usr/bin/env python3
"""
BeyTV Local Client - Receives downloads from Replit dashboard
Run this on your local machine to enable downloads
"""

import json
import os
import subprocess
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from pathlib import Path

class LocalDownloadHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/download':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                download_item = json.loads(post_data.decode('utf-8'))
                self.handle_download(download_item)
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(b'{"status": "success"}')
            except Exception as e:
                self.send_response(500)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                print(f"Error: {e}")
    
    def do_GET(self):
        if self.path == '/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(b'{"status": "online", "client": "BeyTV Local"}')
        elif self.path == '/':
            self.serve_status_page()
    
    def serve_status_page(self):
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>BeyTV Local Client</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }}
        .status {{ padding: 20px; background: #e8f5e8; border-radius: 8px; text-align: center; }}
        .info {{ margin: 20px 0; padding: 15px; background: #f0f0f0; border-radius: 5px; }}
        .downloads {{ margin: 20px 0; }}
        .download-item {{ padding: 10px; border-bottom: 1px solid #ddd; }}
    </style>
</head>
<body>
    <div class="status">
        <h1>🎬 BeyTV Local Client</h1>
        <p>✅ Online and ready to receive downloads!</p>
        <p>Listening on: <strong>http://localhost:8888</strong></p>
    </div>
    
    <div class="info">
        <h3>📥 How it works:</h3>
        <ol>
            <li>Browse content on your Replit BeyTV dashboard</li>
            <li>Click "Queue Download" on items you want</li>
            <li>Downloads automatically start on this machine</li>
            <li>Files save to your local Downloads/BeyTV folder</li>
        </ol>
    </div>
    
    <div class="downloads">
        <h3>📁 Download Location:</h3>
        <p><code>{Path.home() / 'Downloads' / 'BeyTV'}</code></p>
        
        <h3>🔧 Setup qBittorrent (Optional):</h3>
        <p>For automatic torrent handling, make sure qBittorrent is running on port 8080</p>
    </div>
    
    <script>
        setInterval(() => {{
            document.querySelector('.status p').innerHTML = '✅ Online - ' + new Date().toLocaleTimeString();
        }}, 1000);
    </script>
</body>
</html>"""
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def handle_download(self, item):
        print(f"📥 Download requested: {item['title']}")
        magnet = item.get('url', '')
        title = item['title']
        
        # Create downloads directory
        downloads_dir = Path.home() / "Downloads" / "BeyTV"
        downloads_dir.mkdir(parents=True, exist_ok=True)
        
        success = False
        
        # Method 1: Try to add to qBittorrent if available
        try:
            import requests
            qb_url = "http://localhost:8080/api/v2/auth/login"
            login_data = {"username": "admin", "password": "adminadmin"}
            session = requests.Session()
            
            # Login to qBittorrent
            login_response = session.post(qb_url, data=login_data, timeout=5)
            if login_response.status_code == 200:
                # Add torrent
                add_url = "http://localhost:8080/api/v2/torrents/add"
                add_data = {"urls": magnet, "category": "beytv"}
                add_response = session.post(add_url, data=add_data, timeout=10)
                
                if add_response.status_code == 200:
                    print(f"✅ Added to qBittorrent: {title}")
                    success = True
                else:
                    print(f"❌ Failed to add to qBittorrent: {add_response.status_code}")
            
        except Exception as e:
            print(f"⚠️ qBittorrent not available: {e}")
        
        # Method 2: Save magnet link as fallback
        if not success:
            try:
                # Clean filename
                safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                magnet_file = downloads_dir / f"{safe_title}.magnet"
                
                with open(magnet_file, 'w') as f:
                    f.write(f"# BeyTV Download\n")
                    f.write(f"# Title: {title}\n")
                    f.write(f"# Added: {item.get('added', 'Unknown')}\n")
                    f.write(f"# Source: {item.get('source', 'Unknown')}\n\n")
                    f.write(magnet)
                
                print(f"💾 Saved magnet link: {magnet_file}")
                
                # Try to open with default torrent application
                try:
                    if os.name == 'nt':  # Windows
                        os.startfile(str(magnet_file))
                    elif os.name == 'posix':  # macOS/Linux
                        subprocess.run(['open', str(magnet_file)], check=False)
                    print(f"🚀 Opened with default application")
                except:
                    print(f"💡 Double-click {magnet_file} to open with your torrent client")
                
                success = True
                
            except Exception as e:
                print(f"❌ Failed to save magnet link: {e}")
        
        # Log the download attempt
        log_file = downloads_dir / "beytv_downloads.log"
        with open(log_file, 'a') as f:
            status = "SUCCESS" if success else "FAILED"
            f.write(f"{item.get('added', 'Unknown')} | {status} | {title} | {magnet[:50]}...\n")

def main():
    print("🎬 BeyTV Local Client Starting...")
    print("📥 Ready to receive downloads from Replit dashboard")
    print("🌐 Local status page: http://localhost:8888")
    print("📁 Downloads will be saved to:", Path.home() / "Downloads" / "BeyTV")
    print("=" * 60)
    
    # Open status page in browser
    try:
        webbrowser.open('http://localhost:8888')
    except:
        pass
    
    try:
        server = HTTPServer(('localhost', 8888), LocalDownloadHandler)
        print("✅ Local client online - waiting for downloads...")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 BeyTV Local Client stopped")
    except Exception as e:
        print(f"❌ Error starting local client: {e}")
        print("💡 Make sure port 8888 is available")

if __name__ == "__main__":
    main()
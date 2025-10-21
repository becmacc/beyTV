#!/usr/bin/env python3
"""
BeyTV Remote Control - Dashboard on Replit, downloads locally for Plex
Interface runs on Replit, files download to your local machine for Plex
"""

import os
import json
import time
import threading
import sqlite3
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from pathlib import Path

# Optional imports for enhanced features
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    import feedparser
    HAS_FEEDPARSER = True
except ImportError:
    HAS_FEEDPARSER = False

class BeyTVHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.init_database()
        super().__init__(*args, **kwargs)
    
    def init_database(self):
        """Initialize SQLite database for download queue"""
        conn = sqlite3.connect('download_queue.db')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS downloads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                url TEXT,
                status TEXT DEFAULT 'queued',
                queued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                local_path TEXT,
                file_size INTEGER
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS local_clients (
                id TEXT PRIMARY KEY,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'offline',
                downloads_path TEXT,
                available_space INTEGER
            )
        ''')
        conn.commit()
        conn.close()

    def do_GET(self):
        if self.path == '/':
            self.serve_dashboard()
        elif self.path == '/api/feeds':
            self.serve_feeds()
        elif self.path == '/api/search':
            self.serve_search()
        elif self.path == '/api/queue':
            self.get_download_queue()
        elif self.path == '/api/local-status':
            self.get_local_status()
        elif self.path.startswith('/api/client/'):
            self.handle_client_api()
        else:
            super().do_GET()
    
    def do_POST(self):
        if self.path == '/api/queue-download':
            self.queue_download()
        elif self.path == '/api/client/checkin':
            self.client_checkin()
        elif self.path == '/api/client/update-status':
            self.update_download_status()
        else:
            self.send_error(404)
    
    def serve_dashboard(self):
        html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BeyTV Remote Control - Downloads for Plex</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: white;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
        .header { text-align: center; margin-bottom: 2rem; }
        .header h1 { font-size: 3rem; margin-bottom: 0.5rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
        .controls { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
        .card { background: rgba(255,255,255,0.1); backdrop-filter: blur(15px); border-radius: 15px; padding: 1.5rem; border: 1px solid rgba(255,255,255,0.2); }
        .card h3 { margin-bottom: 1rem; font-size: 1.2rem; }
        .btn { background: rgba(255,255,255,0.2); border: 1px solid rgba(255,255,255,0.3); color: white; padding: 0.5rem 1rem; border-radius: 8px; cursor: pointer; margin: 0.25rem; }
        .btn:hover { background: rgba(255,255,255,0.3); }
        .btn.queue { background: rgba(76, 175, 80, 0.6); }
        .btn.queue:hover { background: rgba(76, 175, 80, 0.8); }
        .status { position: fixed; top: 1rem; right: 1rem; background: rgba(0,0,0,0.8); padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.9rem; }
        .local-status { background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 8px; margin: 1rem 0; }
        .queue-item { background: rgba(255,255,255,0.05); padding: 1rem; margin: 0.5rem 0; border-radius: 8px; border-left: 3px solid #4CAF50; }
        .search-box { width: 100%; padding: 0.75rem; border: 1px solid rgba(255,255,255,0.3); border-radius: 8px; background: rgba(255,255,255,0.1); color: white; margin-bottom: 1rem; }
        .loading { text-align: center; padding: 2rem; }
        .offline { border-left-color: #f44336 !important; }
        .downloading { border-left-color: #ff9800 !important; }
        .completed { border-left-color: #4caf50 !important; }
    </style>
</head>
<body>
    <div class="status" id="status">� Checking local client...</div>
    
    <div class="container">
        <div class="header">
            <h1>🎬 BeyTV Remote Control</h1>
            <p>Download movies & TV shows for your Plex library from anywhere</p>
        </div>
        
        <div class="controls">
            <div class="card">
                <h3>�️ Local Download Client</h3>
                <div id="localStatus" class="local-status">
                    <div class="loading">Checking local client...</div>
                </div>
                <button class="btn" onclick="refreshStatus()">Refresh Status</button>
                <button class="btn" onclick="showClientHelp()">Setup Help</button>
            </div>
            
            <div class="card">
                <h3>� Content Discovery</h3>
                <input type="text" class="search-box" id="searchBox" placeholder="Search for movies & TV shows..." onkeypress="handleSearch(event)">
                <button class="btn" onclick="refreshFeeds()">Browse Content</button>
                <button class="btn" onclick="loadPopular()">Popular Items</button>
            </div>
            
            <div class="card">
                <h3>📥 Download Queue</h3>
                <div>Queued for Plex: <span id="queueCount">0</span> items</div>
                <button class="btn" onclick="refreshQueue()">Refresh Queue</button>
                <button class="btn" onclick="clearCompleted()">Clear Completed</button>
            </div>
        </div>
        
        <div class="card">
            <h2>📥 Download Queue (Local → Plex)</h2>
            <div id="queueContent" class="loading">Loading queue...</div>
        </div>
        
        <div class="card">
            <h2>� Available Content</h2>
            <div id="feedsContent" class="loading">Loading content...</div>
        </div>
    </div>

    <script>
        let localClientOnline = false;
        
        async function refreshStatus() {
            try {
                const response = await fetch('/api/local-status');
                const status = await response.json();
                displayLocalStatus(status);
            } catch (error) {
                displayLocalStatus({online: false, error: error.message});
            }
        }
        
        function displayLocalStatus(status) {
            const container = document.getElementById('localStatus');
            const statusIndicator = document.getElementById('status');
            
            if (status.online) {
                localClientOnline = true;
                container.innerHTML = `
                    <div style="color: #4CAF50;">🟢 Local Client Online</div>
                    <div>Plex Media Path: ${status.downloads_path || '~/Downloads/BeyTV'}</div>
                    <div>Available Space: ${status.available_space ? Math.round(status.available_space/1024/1024/1024) + 'GB' : 'Unknown'}</div>
                    <div>Ready to download for Plex!</div>
                `;
                statusIndicator.textContent = '🟢 Ready for Downloads';
            } else {
                localClientOnline = false;
                container.innerHTML = `
                    <div style="color: #f44336;">🔴 Local Client Offline</div>
                    <div>Downloads will queue until client connects</div>
                    <div>Run local client to download for Plex</div>
                `;
                statusIndicator.textContent = '🔴 Local Client Needed';
            }
        }
        
        async function refreshQueue() {
            try {
                const response = await fetch('/api/queue');
                const queue = await response.json();
                displayQueue(queue);
            } catch (error) {
                document.getElementById('queueContent').innerHTML = '<div class="loading">❌ Error loading queue</div>';
            }
        }
        
        function displayQueue(queue) {
            const container = document.getElementById('queueContent');
            document.getElementById('queueCount').textContent = queue.length;
            
            if (queue.length === 0) {
                container.innerHTML = '<div class="loading">No downloads queued for Plex</div>';
                return;
            }
            
            container.innerHTML = queue.map(item => `
                <div class="queue-item ${item.status}">
                    <div style="font-weight: bold;">${item.title}</div>
                    <div style="font-size: 0.9rem; opacity: 0.8;">
                        Status: ${item.status.toUpperCase()} | 
                        Queued: ${new Date(item.queued_at).toLocaleString()} |
                        ${item.local_path ? 'Local Path: ' + item.local_path : ''}
                        <button class="btn" onclick="removeFromQueue(${item.id})" style="float: right; padding: 0.25rem 0.5rem;">Remove</button>
                    </div>
                </div>
            `).join('');
        }
        
        async function refreshFeeds() {
            document.getElementById('feedsContent').innerHTML = '<div class="loading">Loading content...</div>';
            try {
                const response = await fetch('/api/feeds');
                const feeds = await response.json();
                displayFeeds(feeds);
            } catch (error) {
                document.getElementById('feedsContent').innerHTML = '<div class="loading">❌ Error loading content</div>';
            }
        }
        
        function displayFeeds(feeds) {
            const container = document.getElementById('feedsContent');
            if (!feeds || feeds.length === 0) {
                container.innerHTML = '<div class="loading">No content available</div>';
                return;
            }
            
            container.innerHTML = feeds.map(item => `
                <div class="queue-item">
                    <div style="font-weight: bold;">${item.title}</div>
                    <div style="font-size: 0.9rem; opacity: 0.8;">
                        Source: ${item.source} | Quality: ${item.quality} | Size: ${item.size}
                        <button class="btn queue" onclick="queueDownload('${item.id}', '${item.title}', '${item.download_url || item.magnet || '#'}')">Download for Plex</button>
                    </div>
                </div>
            `).join('');
        }
        
        async function queueDownload(id, title, url) {
            if (!url || url === '#') {
                alert('No download URL available for this item');
                return;
            }
            
            try {
                const response = await fetch('/api/queue-download', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({id, title, url})
                });
                
                const result = await response.json();
                if (response.ok) {
                    alert(`✅ "${title}" queued for download!\\n\\nWill be saved locally for Plex to access.`);
                    refreshQueue();
                } else {
                    alert(`❌ Failed to queue download: ${result.message}`);
                }
            } catch (error) {
                alert(`❌ Error: ${error.message}`);
            }
        }
        
        function handleSearch(event) {
            if (event.key === 'Enter') {
                const query = document.getElementById('searchBox').value;
                if (query) searchContent(query);
            }
        }
        
        async function searchContent(query) {
            document.getElementById('feedsContent').innerHTML = '<div class="loading">Searching...</div>';
            try {
                const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
                const results = await response.json();
                displayFeeds(results);
            } catch (error) {
                document.getElementById('feedsContent').innerHTML = '<div class="loading">❌ Search failed</div>';
            }
        }
        
        function loadPopular() {
            const popular = [
                {id: '1', title: 'Popular Movie 2025', source: 'YTS', quality: '1080p', size: '1.4GB', download_url: 'magnet:?xt=urn:btih:example1'},
                {id: '2', title: 'Trending TV Show S01E01', source: 'EZTV', quality: '720p', size: '350MB', download_url: 'magnet:?xt=urn:btih:example2'},
                {id: '3', title: 'Documentary Collection', source: 'Archive', quality: '720p', size: '800MB', download_url: 'https://archive.org/download/example'}
            ];
            displayFeeds(popular);
        }
        
        function showClientHelp() {
            alert(`🖥️ Local Client Setup for Plex\\n\\n1. Download local_client.py from GitHub\\n2. Run: python3 local_client.py\\n3. Enter your Replit URL when prompted\\n4. Files will download to your Plex media folder\\n\\nThe client will:\\n• Connect to this dashboard\\n• Download files locally for Plex\\n• Update status in real-time`);
        }
        
        async function removeFromQueue(id) {
            if (confirm('Remove this download from queue?')) {
                // Implementation for removing items from queue
                alert(`Remove item ${id} from queue (feature coming soon)`);
            }
        }
        
        function clearCompleted() {
            if (confirm('Clear completed downloads from queue?')) {
                alert('Clear completed downloads (feature coming soon)');
            }
        }
        
        // Auto-refresh every 10 seconds
        setInterval(() => {
            refreshStatus();
            refreshQueue();
        }, 10000);
        
        // Initial load
        window.addEventListener('load', () => {
            setTimeout(() => {
                refreshStatus();
                refreshQueue();
                loadPopular();
            }, 1000);
        });
    </script>
</body>
</html>"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def queue_download(self):
        """Add download to queue for local client to pick up"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            conn = sqlite3.connect('download_queue.db')
            conn.execute(
                'INSERT INTO downloads (title, url, status) VALUES (?, ?, ?)',
                (data['title'], data['url'], 'queued')
            )
            conn.commit()
            conn.close()
            
            response = {"status": "success", "message": "Download queued"}
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_error(500, str(e))

    def get_download_queue(self):
        """Get current download queue"""
        conn = sqlite3.connect('download_queue.db')
        cursor = conn.execute('SELECT * FROM downloads ORDER BY queued_at DESC')
        downloads = []
        for row in cursor.fetchall():
            downloads.append({
                'id': row[0],
                'title': row[1], 
                'url': row[2],
                'status': row[3],
                'queued_at': row[4],
                'local_path': row[7],
                'file_size': row[8]
            })
        conn.close()
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(downloads).encode())

    def get_local_status(self):
        """Check if local client is online"""
        conn = sqlite3.connect('download_queue.db')
        cursor = conn.execute('SELECT * FROM local_clients ORDER BY last_seen DESC LIMIT 1')
        client = cursor.fetchone()
        conn.close()
        
        if client:
            # Check if client was seen in last 60 seconds
            import datetime
            try:
                last_seen = datetime.datetime.fromisoformat(client[1])
                now = datetime.datetime.now()
                online = (now - last_seen).seconds < 60
            except:
                online = False
            
            status = {
                'online': online,
                'last_seen': client[1],
                'downloads_path': client[3],
                'available_space': client[4]
            }
        else:
            status = {'online': False}
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(status).encode())

    def client_checkin(self):
        """Handle local client check-in"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            conn = sqlite3.connect('download_queue.db')
            conn.execute('''
                INSERT OR REPLACE INTO local_clients 
                (id, last_seen, status, downloads_path, available_space) 
                VALUES (?, CURRENT_TIMESTAMP, ?, ?, ?)
            ''', (
                data['client_id'],
                data['status'],
                data['downloads_path'],
                data['available_space']
            ))
            conn.commit()
            conn.close()
            
            # Return queued downloads for client
            conn = sqlite3.connect('download_queue.db')
            cursor = conn.execute('SELECT * FROM downloads WHERE status = "queued"')
            queued = []
            for row in cursor.fetchall():
                queued.append({
                    'id': row[0],
                    'title': row[1],
                    'url': row[2],
                    'status': row[3]
                })
            conn.close()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'queued_downloads': queued}).encode())
            
        except Exception as e:
            self.send_error(500, str(e))

    def update_download_status(self):
        """Update download status from local client"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            conn = sqlite3.connect('download_queue.db')
            if data['status'] == 'completed':
                conn.execute('''
                    UPDATE downloads 
                    SET status = ?, completed_at = CURRENT_TIMESTAMP, local_path = ?
                    WHERE id = ?
                ''', (data['status'], data.get('local_path'), data['download_id']))
            else:
                conn.execute('''
                    UPDATE downloads 
                    SET status = ?
                    WHERE id = ?
                ''', (data['status'], data['download_id']))
            conn.commit()
            conn.close()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "updated"}')
            
        except Exception as e:
            self.send_error(500, str(e))

    def serve_feeds(self):
        """Serve content feeds with download URLs"""
        feeds = [
            {
                "id": "1", 
                "title": "Sample Movie 2025 [1080p]", 
                "source": "YTS", 
                "quality": "1080p", 
                "size": "1.2GB", 
                "download_url": "magnet:?xt=urn:btih:sample1&dn=Sample+Movie+2025"
            },
            {
                "id": "2", 
                "title": "TV Series S01E01 [720p]", 
                "source": "EZTV", 
                "quality": "720p", 
                "size": "350MB", 
                "download_url": "magnet:?xt=urn:btih:sample2&dn=TV+Series+S01E01"
            },
            {
                "id": "3", 
                "title": "Documentary Collection [720p]", 
                "source": "Archive", 
                "quality": "720p", 
                "size": "800MB", 
                "download_url": "https://archive.org/download/sample/documentary.mp4"
            }
        ]
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(feeds).encode())

    def serve_search(self):
        """Handle search requests"""
        query_params = parse_qs(urlparse(self.path).query)
        query = query_params.get('q', [''])[0]
        
        results = [
            {
                "id": f"search_1", 
                "title": f"{query} (2025) [1080p]", 
                "source": "Search", 
                "quality": "1080p", 
                "size": "1.5GB", 
                "download_url": f"magnet:?xt=urn:btih:search_{hash(query)}&dn={query.replace(' ', '+')}"
            },
            {
                "id": f"search_2", 
                "title": f"{query} TV Series [720p]", 
                "source": "Search", 
                "quality": "720p", 
                "size": "400MB", 
                "download_url": f"magnet:?xt=urn:btih:search_{hash(query)}_tv&dn={query.replace(' ', '+')}_TV"
            }
        ]
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(results).encode())

def run_server():
    """Run the BeyTV Remote Control server"""
    port = int(os.environ.get('PORT', 3000))
    server = HTTPServer(('0.0.0.0', port), BeyTVHandler)
    print(f"🎬 BeyTV Remote Control Server starting on port {port}")
    print(f"🌐 Dashboard: http://localhost:{port}")
    print(f"📱 Control downloads from anywhere - Files save locally for Plex")
    print(f"💡 Run local_client.py on your machine to enable downloads")
    server.serve_forever()

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    Path("data").mkdir(exist_ok=True)
    
    print("🎬 BeyTV Remote Control System")
    print("🌐 Web Interface (Replit) + Local Downloads (Your Machine)")
    print("� Perfect for building your Plex library remotely!")
    print("=" * 60)
    
    run_server()
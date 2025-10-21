#!/usr/bin/env python3
"""
BeyTV Hybrid - Remote Dashboard with Local Downloads
Runs on Replit but downloads happen on your local machine
"""

import os
import json
import time
import threading
import requests
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import feedparser
from pathlib import Path

class BeyTVHybridHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.serve_dashboard()
        elif self.path == '/api/feeds':
            self.serve_feeds()
        elif self.path == '/api/search':
            self.serve_search()
        elif self.path.startswith('/api/download'):
            self.handle_download_request()
        elif self.path == '/api/local-client':
            self.serve_local_client()
        else:
            super().do_GET()
    
    def serve_dashboard(self):
        html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BeyTV Hybrid - Remote Dashboard + Local Downloads</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: white;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }
        .header {
            text-align: center;
            margin-bottom: 2rem;
        }
        .header h1 {
            font-size: 3rem;
            margin-bottom: 0.5rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .status-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(15px);
            border-radius: 15px;
            padding: 1rem;
            margin-bottom: 2rem;
            border: 1px solid rgba(255,255,255,0.2);
        }
        .status-item {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #4CAF50;
        }
        .status-dot.offline {
            background: #f44336;
        }
        .controls {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }
        .card {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(15px);
            border-radius: 15px;
            padding: 1.5rem;
            border: 1px solid rgba(255,255,255,0.2);
            transition: transform 0.3s ease;
        }
        .card:hover { transform: translateY(-2px); }
        .card h3 { margin-bottom: 1rem; font-size: 1.2rem; }
        .btn {
            background: rgba(255,255,255,0.2);
            border: 1px solid rgba(255,255,255,0.3);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            margin: 0.25rem;
            display: inline-block;
            text-decoration: none;
        }
        .btn:hover {
            background: rgba(255,255,255,0.3);
            transform: translateY(-1px);
        }
        .btn.download {
            background: #4CAF50;
            border-color: #45a049;
        }
        .btn.download:hover {
            background: #45a049;
        }
        .feeds-container {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(15px);
            border-radius: 15px;
            padding: 1.5rem;
            border: 1px solid rgba(255,255,255,0.2);
        }
        .feed-item {
            background: rgba(255,255,255,0.05);
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 8px;
            border-left: 3px solid #4CAF50;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .feed-content {
            flex: 1;
        }
        .feed-title { font-weight: bold; margin-bottom: 0.5rem; }
        .feed-meta { font-size: 0.9rem; opacity: 0.8; }
        .feed-actions {
            display: flex;
            gap: 0.5rem;
        }
        .search-box {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid rgba(255,255,255,0.3);
            border-radius: 8px;
            background: rgba(255,255,255,0.1);
            color: white;
            margin-bottom: 1rem;
        }
        .search-box::placeholder { color: rgba(255,255,255,0.7); }
        .local-client-info {
            background: rgba(255,193,7,0.2);
            border: 1px solid rgba(255,193,7,0.5);
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
        }
        .download-queue {
            background: rgba(255,255,255,0.05);
            border-radius: 8px;
            padding: 1rem;
            margin-top: 1rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎬 BeyTV Hybrid</h1>
            <p>Remote Dashboard • Local Downloads • Best of Both Worlds</p>
        </div>
        
        <div class="status-bar">
            <div class="status-item">
                <div class="status-dot" id="replit-status"></div>
                <span>Replit Dashboard</span>
            </div>
            <div class="status-item">
                <div class="status-dot offline" id="local-status"></div>
                <span>Local Client</span>
            </div>
            <div class="status-item">
                <span id="download-count">0 items in queue</span>
            </div>
        </div>
        
        <div class="local-client-info" id="client-info">
            <h4>📥 Local Download Client</h4>
            <p>To enable local downloads, run this on your machine:</p>
            <code>python local_client.py</code>
            <button class="btn" onclick="downloadLocalClient()">Download Local Client</button>
        </div>
        
        <div class="controls">
            <div class="card">
                <h3>🔍 Content Discovery</h3>
                <input type="text" class="search-box" id="searchBox" placeholder="Search for movies, TV shows..." onkeypress="handleSearch(event)">
                <button class="btn" onclick="refreshFeeds()">Refresh Feeds</button>
                <button class="btn" onclick="loadPopular()">Popular Content</button>
            </div>
            
            <div class="card">
                <h3>📊 Dashboard</h3>
                <button class="btn" onclick="showStats()">View Statistics</button>
                <button class="btn" onclick="showQueue()">Download Queue</button>
                <button class="btn" onclick="clearQueue()">Clear Queue</button>
            </div>
            
            <div class="card">
                <h3>⚙️ Settings</h3>
                <button class="btn" onclick="checkLocalClient()">Check Local Client</button>
                <button class="btn" onclick="showHelp()">Setup Help</button>
            </div>
        </div>
        
        <div class="feeds-container">
            <h2>📋 Available Content</h2>
            <div id="feedsContent">Loading content feeds...</div>
            
            <div class="download-queue" id="downloadQueue" style="display: none;">
                <h3>📥 Download Queue (Local)</h3>
                <div id="queueContent">No items in queue</div>
            </div>
        </div>
    </div>

    <script>
        let downloadQueue = [];
        let localClientConnected = false;
        
        async function refreshFeeds() {
            document.getElementById('feedsContent').innerHTML = 'Loading content feeds...';
            try {
                const response = await fetch('/api/feeds');
                const data = await response.json();
                displayFeeds(data);
            } catch (error) {
                document.getElementById('feedsContent').innerHTML = '❌ Error loading feeds';
            }
        }
        
        function displayFeeds(feeds) {
            const container = document.getElementById('feedsContent');
            if (!feeds || feeds.length === 0) {
                container.innerHTML = 'No content available';
                return;
            }
            
            container.innerHTML = feeds.map(item => `
                <div class="feed-item">
                    <div class="feed-content">
                        <div class="feed-title">${item.title}</div>
                        <div class="feed-meta">
                            Source: ${item.source} | Quality: ${item.quality || 'N/A'} | Size: ${item.size || 'N/A'}
                        </div>
                    </div>
                    <div class="feed-actions">
                        <button class="btn" onclick="viewDetails('${item.id}')">Details</button>
                        <button class="btn download" onclick="addToDownloadQueue('${item.id}', '${item.title}', '${item.magnet || item.download_url || ''}')">
                            📥 Queue Download
                        </button>
                    </div>
                </div>
            `).join('');
        }
        
        function addToDownloadQueue(id, title, downloadUrl) {
            if (!downloadUrl) {
                alert('No download URL available for this item');
                return;
            }
            
            const item = {
                id: id,
                title: title,
                url: downloadUrl,
                added: new Date().toISOString(),
                status: 'queued'
            };
            
            downloadQueue.push(item);
            updateQueueDisplay();
            
            // Try to send to local client
            sendToLocalClient(item);
            
            alert(`Added "${title}" to download queue!\\n\\nThis will download to your local machine when the local client is running.`);
        }
        
        async function sendToLocalClient(item) {
            try {
                // Try to send to local client (you'll run this on your machine)
                const response = await fetch('http://localhost:8888/download', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(item)
                });
                
                if (response.ok) {
                    localClientConnected = true;
                    updateClientStatus();
                    console.log('Sent to local client:', item.title);
                }
            } catch (error) {
                localClientConnected = false;
                updateClientStatus();
                console.log('Local client not connected');
            }
        }
        
        function updateQueueDisplay() {
            document.getElementById('download-count').textContent = `${downloadQueue.length} items in queue`;
            
            if (downloadQueue.length > 0) {
                document.getElementById('downloadQueue').style.display = 'block';
                document.getElementById('queueContent').innerHTML = downloadQueue.map(item => `
                    <div style="padding: 0.5rem; border-bottom: 1px solid rgba(255,255,255,0.1);">
                        <strong>${item.title}</strong><br>
                        <small>Added: ${new Date(item.added).toLocaleString()} | Status: ${item.status}</small>
                    </div>
                `).join('');
            }
        }
        
        function updateClientStatus() {
            const statusDot = document.getElementById('local-status');
            const clientInfo = document.getElementById('client-info');
            
            if (localClientConnected) {
                statusDot.classList.remove('offline');
                clientInfo.style.display = 'none';
            } else {
                statusDot.classList.add('offline');
                clientInfo.style.display = 'block';
            }
        }
        
        async function checkLocalClient() {
            try {
                const response = await fetch('http://localhost:8888/status');
                if (response.ok) {
                    localClientConnected = true;
                    alert('✅ Local client connected!\\nDownloads will be sent to your machine.');
                } else {
                    throw new Error('Not connected');
                }
            } catch (error) {
                localClientConnected = false;
                alert('❌ Local client not running.\\nDownload the local client and run it on your machine to enable downloads.');
            }
            updateClientStatus();
        }
        
        function downloadLocalClient() {
            // This would download the local client script
            alert('Local client download would start here.\\n\\nFor now, you can create a simple Python script that listens on port 8888 for download requests.');
        }
        
        function handleSearch(event) {
            if (event.key === 'Enter') {
                const query = document.getElementById('searchBox').value;
                searchContent(query);
            }
        }
        
        async function searchContent(query) {
            if (!query) return;
            document.getElementById('feedsContent').innerHTML = 'Searching...';
            try {
                const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
                const data = await response.json();
                displayFeeds(data);
            } catch (error) {
                document.getElementById('feedsContent').innerHTML = '❌ Search failed';
            }
        }
        
        function loadPopular() {
            const popular = [
                {id: '1', title: 'Popular Movie 2025', source: 'YTS', quality: '1080p', size: '1.2GB', magnet: 'magnet:?xt=urn:btih:example1'},
                {id: '2', title: 'Trending TV Series S01E01', source: 'EZTV', quality: '720p', size: '350MB', magnet: 'magnet:?xt=urn:btih:example2'},
                {id: '3', title: 'Documentary Collection', source: 'Archive', quality: '720p', size: '800MB', magnet: 'magnet:?xt=urn:btih:example3'}
            ];
            displayFeeds(popular);
        }
        
        function viewDetails(id) {
            alert(`Viewing details for item ${id}\\n\\nThis would show:\\n- File size and quality\\n- Available sources\\n- Ratings and reviews\\n- Download options`);
        }
        
        function showQueue() {
            if (downloadQueue.length === 0) {
                alert('Download queue is empty');
            } else {
                updateQueueDisplay();
                document.getElementById('downloadQueue').scrollIntoView();
            }
        }
        
        function clearQueue() {
            downloadQueue = [];
            updateQueueDisplay();
            document.getElementById('downloadQueue').style.display = 'none';
            alert('Download queue cleared');
        }
        
        function showStats() {
            alert(`📊 BeyTV Hybrid Statistics\\n\\n• Platform: Replit (Remote Dashboard)\\n• Downloads: Local Machine\\n• Queue Items: ${downloadQueue.length}\\n• Local Client: ${localClientConnected ? 'Connected' : 'Disconnected'}\\n• Mode: Hybrid (Best of Both Worlds)`);
        }
        
        function showHelp() {
            alert(`🎬 BeyTV Hybrid Setup\\n\\n1. This dashboard runs on Replit (accessible anywhere)\\n2. Downloads happen on your local machine\\n3. Install local client on your computer\\n4. Local client listens for download requests\\n5. Queue downloads from anywhere, download at home!\\n\\nPerfect for your resource constraints!`);
        }
        
        // Auto-refresh feeds on load
        window.addEventListener('load', () => {
            setTimeout(refreshFeeds, 1000);
            setTimeout(checkLocalClient, 2000);
        });
        
        // Periodic client check
        setInterval(checkLocalClient, 30000);
    </script>
</body>
</html>"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def serve_feeds(self):
        # Sample feeds with download URLs
        feeds_data = [
            {
                "id": "1",
                "title": "Sample Movie 2025 [1080p]",
                "source": "YTS",
                "quality": "1080p",
                "size": "1.2GB",
                "magnet": "magnet:?xt=urn:btih:samplehash1&dn=Sample+Movie+2025"
            },
            {
                "id": "2", 
                "title": "Popular TV Series S01E01 [720p]",
                "source": "EZTV",
                "quality": "720p", 
                "size": "350MB",
                "magnet": "magnet:?xt=urn:btih:samplehash2&dn=TV+Series+S01E01"
            },
            {
                "id": "3",
                "title": "Documentary Collection [720p]",
                "source": "Archive",
                "quality": "720p",
                "size": "800MB",
                "magnet": "magnet:?xt=urn:btih:samplehash3&dn=Documentary+Collection"
            }
        ]
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(feeds_data).encode())
    
    def serve_search(self):
        query_params = parse_qs(urlparse(self.path).query)
        query = query_params.get('q', [''])[0]
        
        # Mock search results with magnet links
        results = [
            {
                "id": f"search_{query}_1",
                "title": f"{query} (2025) [1080p]",
                "source": "Search",
                "quality": "1080p",
                "size": "1.5GB",
                "magnet": f"magnet:?xt=urn:btih:search{hash(query)}&dn={query.replace(' ', '+')}"
            }
        ]
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(results).encode())
    
    def serve_local_client(self):
        # Serve the local client script
        client_script = '''#!/usr/bin/env python3
"""
BeyTV Local Client - Receives downloads from Replit dashboard
Run this on your local machine to enable downloads
"""

import json
import os
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

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
                self.end_headers()
                self.wfile.write(b'{"status": "success"}')
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                print(f"Error: {e}")
    
    def do_GET(self):
        if self.path == '/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "online"}')
    
    def handle_download(self, item):
        print(f"📥 Download requested: {item['title']}")
        magnet = item.get('url', '')
        
        # Add to qBittorrent if available
        try:
            # Try to add to qBittorrent via API
            import requests
            qb_url = "http://localhost:8080/api/v2/torrents/add"
            data = {"urls": magnet}
            response = requests.post(qb_url, data=data)
            print(f"✅ Added to qBittorrent: {item['title']}")
        except:
            # Fallback: save magnet link to file
            downloads_dir = os.path.expanduser("~/Downloads/BeyTV")
            os.makedirs(downloads_dir, exist_ok=True)
            
            magnet_file = os.path.join(downloads_dir, f"{item['title']}.magnet")
            with open(magnet_file, 'w') as f:
                f.write(magnet)
            print(f"💾 Saved magnet link: {magnet_file}")

if __name__ == "__main__":
    print("🎬 BeyTV Local Client Starting...")
    print("📥 Ready to receive downloads from Replit dashboard")
    print("🌐 Listening on http://localhost:8888")
    print("=" * 50)
    
    server = HTTPServer(('localhost', 8888), LocalDownloadHandler)
    server.serve_forever()
'''
        
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.send_header('Content-Disposition', 'attachment; filename="local_client.py"')
        self.end_headers()
        self.wfile.write(client_script.encode())

def run_server():
    """Run the BeyTV Hybrid server"""
    port = int(os.environ.get('PORT', 3000))
    server = HTTPServer(('0.0.0.0', port), BeyTVHybridHandler)
    print(f"🎬 BeyTV Hybrid starting on port {port}")
    print(f"🌐 Remote Dashboard: http://localhost:{port}")
    print(f"📥 Local downloads via client on port 8888")
    print(f"🚀 Best of both worlds: Remote browsing + Local storage!")
    server.serve_forever()

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    Path("cache").mkdir(exist_ok=True)
    
    print("🎬 BeyTV Hybrid Edition")
    print("🌐 Remote Dashboard (Replit) + Local Downloads")
    print("=" * 50)
    
    run_server()
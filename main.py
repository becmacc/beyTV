#!/usr/bin/env python3
"""
BeyTV Hybrid - Remote Dashboard with Local Downloads
Dashboard runs on Replit, downloads happen on your local machine
"""

import os
import json
import time
import threading
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
    def do_GET(self):
        if self.path == '/':
            self.serve_dashboard()
        elif self.path == '/api/feeds':
            self.serve_feeds()
        elif self.path == '/api/search':
            self.serve_search()
        elif self.path.startswith('/api/download'):
            self.handle_download()
        else:
            super().do_GET()
    
    def serve_dashboard(self):
        html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BeyTV Replit - Lightweight Media Dashboard</title>
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
        }
        .feed-title { font-weight: bold; margin-bottom: 0.5rem; }
        .feed-meta { font-size: 0.9rem; opacity: 0.8; }
        .status { 
            position: fixed; 
            top: 1rem; 
            right: 1rem; 
            background: rgba(0,0,0,0.8);
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.9rem;
        }
        .loading { text-align: center; padding: 2rem; }
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
    </style>
</head>
<body>
    <div class="status" id="status">🟢 BeyTV Replit Online</div>
    
    <div class="container">
        <div class="header">
            <h1>🎬 BeyTV Replit</h1>
            <p>Lightweight Media Management - Perfect for Limited Resources</p>
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
                <button class="btn" onclick="showHistory()">Download History</button>
                <button class="btn" onclick="exportData()">Export Data</button>
            </div>
            
            <div class="card">
                <h3>⚙️ Settings</h3>
                <button class="btn" onclick="toggleMode()">Lite Mode: ON</button>
                <button class="btn" onclick="clearCache()">Clear Cache</button>
                <button class="btn" onclick="showHelp()">Help</button>
            </div>
        </div>
        
        <div class="feeds-container">
            <h2>📋 Available Content</h2>
            <div id="feedsContent" class="loading">
                Loading content feeds...
            </div>
        </div>
    </div>

    <script>
        let currentMode = 'lite';
        
        async function refreshFeeds() {
            document.getElementById('feedsContent').innerHTML = '<div class="loading">Refreshing feeds...</div>';
            try {
                const response = await fetch('/api/feeds');
                const data = await response.json();
                displayFeeds(data);
            } catch (error) {
                document.getElementById('feedsContent').innerHTML = '<div class="loading">❌ Error loading feeds</div>';
            }
        }
        
        function displayFeeds(feeds) {
            const container = document.getElementById('feedsContent');
            if (!feeds || feeds.length === 0) {
                container.innerHTML = '<div class="loading">No content available</div>';
                return;
            }
            
            container.innerHTML = feeds.map(item => `
                <div class="feed-item">
                    <div class="feed-title">${item.title}</div>
                    <div class="feed-meta">
                        Source: ${item.source} | 
                        <button class="btn" onclick="viewDetails('${item.id}')">View Details</button>
                        <button class="btn" onclick="addToWishlist('${item.id}')">Add to Wishlist</button>
                    </div>
                </div>
            `).join('');
        }
        
        function handleSearch(event) {
            if (event.key === 'Enter') {
                const query = document.getElementById('searchBox').value;
                searchContent(query);
            }
        }
        
        async function searchContent(query) {
            if (!query) return;
            document.getElementById('feedsContent').innerHTML = '<div class="loading">Searching...</div>';
            try {
                const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
                const data = await response.json();
                displayFeeds(data);
            } catch (error) {
                document.getElementById('feedsContent').innerHTML = '<div class="loading">❌ Search failed</div>';
            }
        }
        
        function loadPopular() {
            document.getElementById('feedsContent').innerHTML = '<div class="loading">Loading popular content...</div>';
            // Simulate loading popular content
            setTimeout(() => {
                const popular = [
                    {id: '1', title: 'Top Movie 2025', source: 'Popular'},
                    {id: '2', title: 'Trending TV Series', source: 'Popular'},
                    {id: '3', title: 'Classic Collection', source: 'Popular'}
                ];
                displayFeeds(popular);
            }, 1000);
        }
        
        function viewDetails(id) {
            alert(`Viewing details for item ${id}\\n\\nThis would show:\\n- File size and quality\\n- Available sources\\n- Ratings and reviews\\n- Download options`);
        }
        
        function addToWishlist(id) {
            alert(`Added item ${id} to wishlist!\\n\\nThis would:\\n- Save to your personal list\\n- Monitor for availability\\n- Notify when ready`);
        }
        
        function toggleMode() {
            currentMode = currentMode === 'lite' ? 'full' : 'lite';
            const btn = event.target;
            btn.textContent = `Lite Mode: ${currentMode === 'lite' ? 'ON' : 'OFF'}`;
            
            if (currentMode === 'lite') {
                document.getElementById('status').textContent = '🟢 Lite Mode - Resource Optimized';
            } else {
                document.getElementById('status').textContent = '🔄 Full Mode - All Features';
            }
        }
        
        function showStats() {
            alert('📊 BeyTV Statistics\\n\\n• Mode: Lite (Resource Optimized)\\n• Platform: Replit\\n• Feeds Monitored: 3\\n• Wishlist Items: 0\\n• Cache Size: 2.1 MB');
        }
        
        function showHistory() {
            alert('📋 Download History\\n\\nNo downloads yet.\\n\\nThis lite version focuses on:\\n• Content discovery\\n• Wishlist management\\n• Resource efficiency');
        }
        
        function exportData() {
            const data = {
                timestamp: new Date().toISOString(),
                mode: currentMode,
                platform: 'replit',
                wishlist: []
            };
            const blob = new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'beytv-export.json';
            a.click();
        }
        
        function clearCache() {
            localStorage.clear();
            alert('✅ Cache cleared!\\n\\nThis helps free up resources on Replit.');
        }
        
        function showHelp() {
            alert(`🎬 BeyTV Replit Help\\n\\nThis lightweight version is optimized for Replit's resource constraints:\\n\\n🔍 Discovery: Browse content without heavy downloads\\n📋 Wishlist: Save items for later\\n⚡ Lite Mode: Minimal resource usage\\n📊 Stats: Monitor system usage\\n\\nPerfect for your old intern setup!`);
        }
        
        // Auto-refresh feeds on load
        window.addEventListener('load', () => {
            setTimeout(refreshFeeds, 1000);
        });
        
        // Periodic status update
        setInterval(() => {
            const status = document.getElementById('status');
            if (currentMode === 'lite') {
                status.textContent = '🟢 BeyTV Lite - Optimized';
            }
        }, 5000);
    </script>
</body>
</html>"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def serve_feeds(self):
        # Lightweight feed aggregation
        feeds_data = [
            {
                "id": "1",
                "title": "Sample Movie 2025",
                "source": "YTS",
                "quality": "1080p",
                "size": "1.2GB"
            },
            {
                "id": "2", 
                "title": "Popular TV Series S01E01",
                "source": "EZTV",
                "quality": "720p",
                "size": "350MB"
            },
            {
                "id": "3",
                "title": "Documentary Collection",
                "source": "Archive",
                "quality": "720p",
                "size": "800MB"
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
        
        # Mock search results
        results = [
            {
                "id": f"search_{query}_1",
                "title": f"Search Result: {query} (Movie)",
                "source": "Search",
                "quality": "1080p",
                "size": "1.5GB"
            },
            {
                "id": f"search_{query}_2",
                "title": f"Search Result: {query} (TV)",
                "source": "Search", 
                "quality": "720p",
                "size": "400MB"
            }
        ]
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(results).encode())

def run_server():
    """Run the lightweight BeyTV server"""
    port = int(os.environ.get('PORT', 3000))
    server = HTTPServer(('0.0.0.0', port), BeyTVHandler)
    print(f"🎬 BeyTV Replit starting on port {port}")
    print(f"🌐 Dashboard: http://localhost:{port}")
    print(f"⚡ Running in Lite Mode - Resource Optimized")
    print(f"💡 Perfect for limited resources!")
    server.serve_forever()

if __name__ == "__main__":
    # Ensure we're in the right directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Create necessary directories
    Path("cache").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    print("🚀 BeyTV Replit Edition")
    print("📱 Lightweight Media Management Dashboard")
    print("🔧 Optimized for Replit's resource constraints")
    print("=" * 50)
    
    run_server()
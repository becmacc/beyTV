#!/usr/bin/env python3
"""
BeyTV Remote Control - qBittorrent Integration
Complete media management system with real torrent downloads
"""

import os
import json
import sqlite3
import time
import shutil
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import requests
from datetime import datetime

class QBittorrentAPI:
    """qBittorrent Web API wrapper for real torrent downloads"""
    
    def __init__(self, host='localhost', port=8080, username='admin', password='adminadmin'):
        self.base_url = f'http://{host}:{port}'
        self.session = requests.Session()
        self.logged_in = False
        
        # Auto-login
        try:
            self.login(username, password)
        except:
            print(f"⚠️ qBittorrent not connected at {self.base_url}")
    
    def login(self, username, password):
        """Login to qBittorrent Web UI"""
        login_data = {'username': username, 'password': password}
        response = self.session.post(f'{self.base_url}/api/v2/auth/login', data=login_data)
        
        if response.status_code == 200 and response.text == 'Ok.':
            self.logged_in = True
            print(f"✅ Connected to qBittorrent at {self.base_url}")
            return True
        else:
            raise Exception(f"qBittorrent login failed: {response.text}")
    
    def search(self, query, plugins='all', category='all'):
        """Search torrents using qBittorrent plugins"""
        if not self.logged_in:
            return []
        
        try:
            # Start search
            search_data = {
                'pattern': query,
                'plugins': plugins,
                'category': category
            }
            
            response = self.session.post(f'{self.base_url}/api/v2/search/start', data=search_data)
            
            if response.status_code != 200:
                return []
            
            search_id = response.json().get('id')
            if not search_id:
                return []
            
            # Wait a bit for results
            time.sleep(2)
            
            # Get results
            results_response = self.session.get(f'{self.base_url}/api/v2/search/results', 
                                             params={'id': search_id})
            
            if results_response.status_code == 200:
                data = results_response.json()
                return data.get('results', [])
            
            return []
            
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def add_torrent(self, url, save_path=None):
        """Add torrent to qBittorrent"""
        if not self.logged_in:
            return False
        
        try:
            data = {'urls': url}
            if save_path:
                data['savepath'] = save_path
            
            response = self.session.post(f'{self.base_url}/api/v2/torrents/add', data=data)
            return response.status_code == 200
            
        except Exception as e:
            print(f"Add torrent error: {e}")
            return False
    
    def get_torrents(self):
        """Get list of all torrents"""
        if not self.logged_in:
            return []
        
        try:
            response = self.session.get(f'{self.base_url}/api/v2/torrents/info')
            if response.status_code == 200:
                return response.json()
            return []
        except:
            return []
    
    def get_status(self):
        """Get qBittorrent status"""
        if not self.logged_in:
            return {'connected': False}
        
        try:
            response = self.session.get(f'{self.base_url}/api/v2/transfer/info')
            if response.status_code == 200:
                data = response.json()
                torrents = self.get_torrents()
                return {
                    'connected': True,
                    'active_torrents': len(torrents),
                    'download_speed': data.get('dl_info_speed', 0),
                    'upload_speed': data.get('up_info_speed', 0)
                }
            return {'connected': False}
        except:
            return {'connected': False}

class BeyTVServer(BaseHTTPRequestHandler):
    
    def __init__(self, *args, **kwargs):
        # Initialize qBittorrent connection
        self.qbt = QBittorrentAPI()
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        if self.path == '/':
            self.serve_dashboard()
        elif self.path == '/api/local-status':
            self.get_local_status()
        elif self.path == '/api/qbt-status':
            self.get_qbt_status()
        elif self.path == '/api/qbt-torrents':
            self.get_qbt_torrents()
        elif self.path == '/api/queue':
            self.get_download_queue()
        elif self.path.startswith('/api/search'):
            self.search_torrents()
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == '/api/queue-download':
            self.queue_download()
        elif self.path == '/api/add-torrent':
            self.add_torrent_to_qbt()
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
    <title>BeyTV Remote Control - qBittorrent + Plex</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: white;
        }
        .container { max-width: 1400px; margin: 0 auto; padding: 2rem; }
        .header { text-align: center; margin-bottom: 2rem; }
        .header h1 { font-size: 3rem; margin-bottom: 0.5rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
        .controls { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
        .card { background: rgba(255,255,255,0.1); backdrop-filter: blur(15px); border-radius: 15px; padding: 1.5rem; border: 1px solid rgba(255,255,255,0.2); }
        .card h3 { margin-bottom: 1rem; font-size: 1.2rem; }
        .btn { background: rgba(255,255,255,0.2); border: 1px solid rgba(255,255,255,0.3); color: white; padding: 0.5rem 1rem; border-radius: 8px; cursor: pointer; margin: 0.25rem; text-decoration: none; display: inline-block; }
        .btn:hover { background: rgba(255,255,255,0.3); }
        .btn.download { background: rgba(76, 175, 80, 0.6); }
        .btn.download:hover { background: rgba(76, 175, 80, 0.8); }
        .btn.torrent { background: rgba(33, 150, 243, 0.6); }
        .btn.torrent:hover { background: rgba(33, 150, 243, 0.8); }
        .status { position: fixed; top: 1rem; right: 1rem; background: rgba(0,0,0,0.8); padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.9rem; }
        .local-status, .qbt-status { background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 8px; margin: 1rem 0; }
        .queue-item, .torrent-item { background: rgba(255,255,255,0.05); padding: 1rem; margin: 0.5rem 0; border-radius: 8px; border-left: 3px solid #4CAF50; }
        .search-box { width: 100%; padding: 0.75rem; border: 1px solid rgba(255,255,255,0.3); border-radius: 8px; background: rgba(255,255,255,0.1); color: white; margin-bottom: 1rem; }
        .loading { text-align: center; padding: 2rem; }
        .offline { border-left-color: #f44336 !important; }
        .downloading { border-left-color: #ff9800 !important; }
        .completed { border-left-color: #4caf50 !important; }
        .seeding { border-left-color: #00bcd4 !important; }
        .tabs { display: flex; margin-bottom: 1rem; }
        .tab { padding: 0.5rem 1rem; margin-right: 0.5rem; border-radius: 8px 8px 0 0; cursor: pointer; background: rgba(255,255,255,0.1); }
        .tab.active { background: rgba(255,255,255,0.2); }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
    </style>
</head>
<body>
    <div class="status" id="status">🔄 Checking connections...</div>
    
    <div class="container">
        <div class="header">
            <h1>🎬 BeyTV Remote Control</h1>
            <p>qBittorrent + Plugins → Download → Plex Library</p>
        </div>
        
        <div class="controls">
            <div class="card">
                <h3>🖥️ Local Client Status</h3>
                <div id="localStatus" class="local-status">
                    <div class="loading">Checking local client...</div>
                </div>
                <button class="btn" onclick="refreshStatus()">Refresh</button>
            </div>
            
            <div class="card">
                <h3>🌊 qBittorrent Status</h3>
                <div id="qbtStatus" class="qbt-status">
                    <div class="loading">Checking qBittorrent...</div>
                </div>
                <button class="btn" onclick="refreshQBT()">Refresh</button>
            </div>
            
            <div class="card">
                <h3>🔍 Torrent Search</h3>
                <input type="text" class="search-box" id="searchBox" placeholder="Search torrents via qBittorrent plugins..." onkeypress="handleSearch(event)">
                <button class="btn" onclick="searchTorrents()">Search All Plugins</button>
                <button class="btn" onclick="loadPopular()">Popular Torrents</button>
            </div>
        </div>
        
        <div class="card">
            <div class="tabs">
                <div class="tab active" onclick="showTab('search')">🔍 Search Results</div>
                <div class="tab" onclick="showTab('active')">🌊 Active Torrents</div>
                <div class="tab" onclick="showTab('queue')">📥 Download Queue</div>
            </div>
            
            <div id="searchTab" class="tab-content active">
                <h2>🔍 Torrent Search Results</h2>
                <div id="searchContent" class="loading">Use search above to find torrents...</div>
            </div>
            
            <div id="activeTab" class="tab-content">
                <h2>🌊 Active qBittorrent Torrents</h2>
                <div id="activeContent" class="loading">Loading active torrents...</div>
            </div>
            
            <div id="queueTab" class="tab-content">
                <h2>📥 Download Queue for Plex</h2>
                <div id="queueContent" class="loading">Loading queue...</div>
            </div>
        </div>
    </div>

    <script>
        let currentTab = 'search';
        
        function showTab(tab) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            
            // Show selected tab
            document.getElementById(tab + 'Tab').classList.add('active');
            event.target.classList.add('active');
            
            currentTab = tab;
            
            // Load content for active tabs
            if (tab === 'active') refreshQBTTorrents();
            if (tab === 'queue') refreshQueue();
        }
        
        async function refreshStatus() {
            try {
                const response = await fetch('/api/local-status');
                const status = await response.json();
                displayLocalStatus(status);
            } catch (error) {
                displayLocalStatus({online: false, error: error.message});
            }
        }
        
        async function refreshQBT() {
            try {
                const response = await fetch('/api/qbt-status');
                const status = await response.json();
                displayQBTStatus(status);
            } catch (error) {
                displayQBTStatus({connected: false, error: error.message});
            }
        }
        
        function displayLocalStatus(status) {
            const container = document.getElementById('localStatus');
            
            if (status.online) {
                container.innerHTML = `
                    <div style="color: #4CAF50;">🟢 Local Client Online</div>
                    <div>Plex Path: ${status.downloads_path || '~/Downloads/BeyTV'}</div>
                    <div>Space: ${status.available_space ? Math.round(status.available_space/1024/1024/1024) + 'GB' : 'Unknown'}</div>
                `;
            } else {
                container.innerHTML = `
                    <div style="color: #f44336;">🔴 Local Client Offline</div>
                    <div>Run local_client.py on your machine</div>
                `;
            }
        }
        
        function displayQBTStatus(status) {
            const container = document.getElementById('qbtStatus');
            const statusIndicator = document.getElementById('status');
            
            if (status.connected) {
                container.innerHTML = `
                    <div style="color: #4CAF50;">🟢 qBittorrent Connected</div>
                    <div>Active: ${status.active_torrents || 0} torrents</div>
                    <div>Download: ${Math.round((status.download_speed || 0) / 1024)}KB/s</div>
                    <div>Upload: ${Math.round((status.upload_speed || 0) / 1024)}KB/s</div>
                `;
                statusIndicator.textContent = '🟢 Ready to Download';
            } else {
                container.innerHTML = `
                    <div style="color: #f44336;">🔴 qBittorrent Offline</div>
                    <div>Start qBittorrent with Web UI enabled</div>
                    <div>Default: http://localhost:8080</div>
                `;
                statusIndicator.textContent = '🔴 qBittorrent Needed';
            }
        }
        
        function handleSearch(event) {
            if (event.key === 'Enter') {
                searchTorrents();
            }
        }
        
        async function searchTorrents() {
            const query = document.getElementById('searchBox').value.trim();
            if (!query) {
                alert('Please enter a search term');
                return;
            }
            
            document.getElementById('searchContent').innerHTML = '<div class="loading">Searching all qBittorrent plugins...</div>';
            showTab('search');
            
            try {
                const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
                const results = await response.json();
                displaySearchResults(results);
            } catch (error) {
                document.getElementById('searchContent').innerHTML = '<div class="loading">❌ Search failed</div>';
            }
        }
        
        function displaySearchResults(results) {
            const container = document.getElementById('searchContent');
            
            if (!results || results.length === 0) {
                container.innerHTML = '<div class="loading">No torrents found</div>';
                return;
            }
            
            container.innerHTML = results.map(item => `
                <div class="torrent-item">
                    <div style="font-weight: bold;">${item.fileName || item.title}</div>
                    <div style="font-size: 0.9rem; opacity: 0.8; margin: 0.5rem 0;">
                        Size: ${item.fileSize || item.size} | 
                        Seeds: ${item.nbSeeders || 0} | 
                        Peers: ${item.nbLeechers || 0} | 
                        Site: ${item.siteUrl || item.source}
                    </div>
                    <div>
                        <button class="btn torrent" onclick="addToQBT('${item.descrLink || item.url}', '${(item.fileName || item.title).replace(/'/g, "\\'")}')">Add to qBittorrent</button>
                        <button class="btn download" onclick="queueForPlex('${item.descrLink || item.url}', '${(item.fileName || item.title).replace(/'/g, "\\'")}')">Queue for Plex</button>
                    </div>
                </div>
            `).join('');
        }
        
        async function addToQBT(magnetUrl, title) {
            try {
                const response = await fetch('/api/add-torrent', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({url: magnetUrl, title: title})
                });
                
                const result = await response.json();
                if (response.ok) {
                    alert(`✅ "${title}" added to qBittorrent!`);
                    if (currentTab === 'active') refreshQBTTorrents();
                } else {
                    alert(`❌ Failed: ${result.message}`);
                }
            } catch (error) {
                alert(`❌ Error: ${error.message}`);
            }
        }
        
        async function queueForPlex(magnetUrl, title) {
            try {
                const response = await fetch('/api/queue-download', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({id: Date.now(), title: title, url: magnetUrl})
                });
                
                const result = await response.json();
                if (response.ok) {
                    alert(`✅ "${title}" queued for Plex!`);
                    if (currentTab === 'queue') refreshQueue();
                } else {
                    alert(`❌ Failed: ${result.message}`);
                }
            } catch (error) {
                alert(`❌ Error: ${error.message}`);
            }
        }
        
        async function refreshQBTTorrents() {
            document.getElementById('activeContent').innerHTML = '<div class="loading">Loading active torrents...</div>';
            try {
                const response = await fetch('/api/qbt-torrents');
                const torrents = await response.json();
                displayActiveTorrents(torrents);
            } catch (error) {
                document.getElementById('activeContent').innerHTML = '<div class="loading">❌ Error loading torrents</div>';
            }
        }
        
        function displayActiveTorrents(torrents) {
            const container = document.getElementById('activeContent');
            
            if (!torrents || torrents.length === 0) {
                container.innerHTML = '<div class="loading">No active torrents</div>';
                return;
            }
            
            container.innerHTML = torrents.map(torrent => `
                <div class="torrent-item ${torrent.state}">
                    <div style="font-weight: bold;">${torrent.name}</div>
                    <div style="font-size: 0.9rem; opacity: 0.8;">
                        Progress: ${Math.round(torrent.progress * 100)}% | 
                        Size: ${Math.round(torrent.size / 1024 / 1024)}MB | 
                        Status: ${torrent.state.toUpperCase()} |
                        DL: ${Math.round(torrent.dlspeed / 1024)}KB/s |
                        UL: ${Math.round(torrent.upspeed / 1024)}KB/s
                    </div>
                </div>
            `).join('');
        }
        
        async function refreshQueue() {
            document.getElementById('queueContent').innerHTML = '<div class="loading">Loading queue...</div>';
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
            
            if (!queue || queue.length === 0) {
                container.innerHTML = '<div class="loading">No downloads queued</div>';
                return;
            }
            
            container.innerHTML = queue.map(item => `
                <div class="queue-item ${item.status}">
                    <div style="font-weight: bold;">${item.title}</div>
                    <div style="font-size: 0.9rem; opacity: 0.8;">
                        Status: ${item.status.toUpperCase()} | 
                        Queued: ${new Date(item.queued_at).toLocaleString()}
                        ${item.local_path ? '| Path: ' + item.local_path : ''}
                    </div>
                </div>
            `).join('');
        }
        
        function loadPopular() {
            // Mock popular torrents
            const popular = [
                {fileName: "Popular Movie 2025 1080p", fileSize: "2.1GB", nbSeeders: 150, nbLeechers: 12, siteUrl: "YTS", descrLink: "magnet:?xt=urn:btih:example1"},
                {fileName: "TV Series S01E01 720p", fileSize: "350MB", nbSeeders: 89, nbLeechers: 5, siteUrl: "EZTV", descrLink: "magnet:?xt=urn:btih:example2"},
                {fileName: "Documentary 2025 1080p", fileSize: "1.8GB", nbSeeders: 67, nbLeechers: 8, siteUrl: "TPB", descrLink: "magnet:?xt=urn:btih:example3"}
            ];
            displaySearchResults(popular);
            showTab('search');
        }
        
        // Auto-refresh every 15 seconds
        setInterval(() => {
            refreshStatus();
            refreshQBT();
            if (currentTab === 'active') refreshQBTTorrents();
            if (currentTab === 'queue') refreshQueue();
        }, 15000);
        
        // Initial load
        window.addEventListener('load', () => {
            setTimeout(() => {
                refreshStatus();
                refreshQBT();
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
    
    def get_qbt_status(self):
        """Get qBittorrent status"""
        try:
            status = self.qbt.get_status()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(status).encode())
        except Exception as e:
            self.send_error(500, str(e))
    
    def get_qbt_torrents(self):
        """Get active torrents from qBittorrent"""
        try:
            torrents = self.qbt.get_torrents()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(torrents).encode())
        except Exception as e:
            self.send_error(500, str(e))
    
    def add_torrent_to_qbt(self):
        """Add torrent to qBittorrent"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            success = self.qbt.add_torrent(data['url'])
            
            if success:
                response = {"status": "success", "message": "Torrent added to qBittorrent"}
                self.send_response(200)
            else:
                response = {"status": "error", "message": "Failed to add torrent"}
                self.send_response(400)
            
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_error(500, str(e))
    
    def search_torrents(self):
        """Search torrents using qBittorrent plugins"""
        try:
            query_components = urlparse(self.path)
            query_params = parse_qs(query_components.query)
            
            search_query = query_params.get('q', [''])[0]
            if not search_query:
                self.send_error(400, "Missing query parameter")
                return
            
            # Use real qBittorrent search
            results = self.qbt.search(search_query)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(results).encode())
            
        except Exception as e:
            print(f"Search error: {e}")
            self.send_error(500, str(e))
    
    def queue_download(self):
        """Add download to queue for local client to pick up"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Initialize database
            self.init_database()
            
            conn = sqlite3.connect('download_queue.db')
            conn.execute(
                'INSERT INTO downloads (title, url, status, torrent_hash) VALUES (?, ?, ?, ?)',
                (data['title'], data['url'], 'queued', '')
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
        try:
            self.init_database()
            
            conn = sqlite3.connect('download_queue.db')
            cursor = conn.execute('SELECT * FROM downloads ORDER BY queued_at DESC')
            
            columns = [description[0] for description in cursor.description]
            queue = []
            
            for row in cursor.fetchall():
                item = dict(zip(columns, row))
                queue.append(item)
            
            conn.close()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(queue).encode())
            
        except Exception as e:
            self.send_error(500, str(e))
    
    def get_local_status(self):
        """Check if local client is connected"""
        try:
            # Check database for recent client checkins
            self.init_database()
            
            conn = sqlite3.connect('download_queue.db')
            cursor = conn.execute('SELECT last_seen FROM clients ORDER BY last_seen DESC LIMIT 1')
            result = cursor.fetchone()
            conn.close()
            
            if result:
                last_seen = datetime.fromisoformat(result[0])
                time_diff = datetime.now() - last_seen
                online = time_diff.total_seconds() < 60  # Online if seen within 60 seconds
            else:
                online = False
            
            response = {
                "online": online,
                "downloads_path": "~/Downloads/BeyTV",
                "available_space": 50 * 1024 * 1024 * 1024  # 50GB mock
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_error(500, str(e))
    
    def client_checkin(self):
        """Handle local client checkin"""
        try:
            self.init_database()
            
            conn = sqlite3.connect('download_queue.db')
            
            # Update or insert client status
            current_time = datetime.now().isoformat()
            conn.execute(
                'INSERT OR REPLACE INTO clients (client_id, last_seen, status) VALUES (?, ?, ?)',
                ('local_client', current_time, 'online')
            )
            conn.commit()
            conn.close()
            
            # Return any pending downloads
            self.get_download_queue()
            
        except Exception as e:
            self.send_error(500, str(e))
    
    def update_download_status(self):
        """Update download status from local client"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            conn = sqlite3.connect('download_queue.db')
            conn.execute(
                'UPDATE downloads SET status = ?, local_path = ? WHERE id = ?',
                (data['status'], data.get('local_path', ''), data['id'])
            )
            conn.commit()
            conn.close()
            
            response = {"status": "success"}
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_error(500, str(e))
    
    def init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect('download_queue.db')
        
        # Enhanced downloads table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS downloads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                status TEXT DEFAULT 'queued',
                queued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                local_path TEXT,
                torrent_hash TEXT,
                qbt_host TEXT,
                qbt_port INTEGER
            )
        ''')
        
        # Client tracking table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                client_id TEXT PRIMARY KEY,
                last_seen TIMESTAMP,
                status TEXT
            )
        ''')
        
        conn.commit()
        conn.close()

def main():
    """Start BeyTV Remote Control Server"""
    print("🎬 Starting BeyTV Remote Control Server...")
    
    # Initialize database
    server = BeyTVServer
    server.init_database(server)
    
    # Start server
    port = int(os.environ.get('PORT', 8000))
    httpd = HTTPServer(('0.0.0.0', port), BeyTVServer)
    
    print(f"✅ BeyTV Remote Control running on http://localhost:{port}")
    print("🌊 Connect qBittorrent at http://localhost:8080")
    print("🖥️ Run local_client.py on your machine for downloads")
    print("🎯 Use Ctrl+C to stop")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 BeyTV Remote Control stopped")
        httpd.server_close()

if __name__ == '__main__':
    main()
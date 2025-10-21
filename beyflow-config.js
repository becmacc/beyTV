// BeyFlow Configuration
// Update these URLs if running on a different server

const BEYFLOW_CONFIG = {
    // Local development (default)
    local: {
        qbittorrent: 'http://localhost:8080',
        plex: 'http://localhost:32400/web',
        ratings: 'http://localhost:8088',
        indexer: 'http://localhost:8089'
    },
    
    // Remote server (update with your server IP)
    remote: {
        qbittorrent: 'http://YOUR_SERVER_IP:8080',
        plex: 'http://YOUR_SERVER_IP:32400/web',
        ratings: 'http://YOUR_SERVER_IP:8088',
        indexer: 'http://YOUR_SERVER_IP:8089'
    },
    
    // Current environment
    current: 'local' // Change to 'remote' when deploying
};

// Apply configuration
function applyConfig() {
    const config = BEYFLOW_CONFIG[BEYFLOW_CONFIG.current];
    
    // Update iframe sources
    document.getElementById('qbit-frame').src = config.qbittorrent;
    document.getElementById('plex-frame').src = config.plex;
    document.getElementById('ratings-frame').src = config.ratings;
    document.getElementById('indexer-frame').src = config.indexer;
    
    console.log('BeyFlow configured for:', BEYFLOW_CONFIG.current);
    console.log('qBittorrent:', config.qbittorrent);
    console.log('Plex:', config.plex);
    console.log('Ratings:', config.ratings);
    console.log('Indexer:', config.indexer);
}

// Auto-apply configuration when page loads
document.addEventListener('DOMContentLoaded', applyConfig);
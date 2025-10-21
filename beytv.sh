#!/bin/bash

# BeyTV Complete Control Script
echo "🎬 BeyTV Complete Control Center"
echo "==============================="
echo ""

# Function to show usage
show_usage() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start      - Start all BeyTV services"
    echo "  stop       - Stop all BeyTV services"
    echo "  restart    - Restart all BeyTV services"
    echo "  status     - Show status of all services"
    echo "  setup      - Initial setup and configuration"
    echo "  ratings    - Start ratings dashboard"
    echo "  notify     - Test/setup notifications"
    echo "  indexer    - Start torrent indexer"
    echo "  scheduler  - Setup automated scheduling"
    echo "  router     - Configure storage routing"
    echo "  logs       - Show Docker service logs"
    echo ""
    echo "Examples:"
    echo "  $0 start           # Start everything"
    echo "  $0 setup           # First-time setup"
    echo "  $0 ratings         # Launch ratings dashboard"
    echo "  $0 indexer         # Launch torrent indexer"
    echo "  $0 router          # Configure storage"
}

# Function to check Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker is not installed."
        echo "Please install Docker Desktop first."
        return 1
    fi
    
    if ! docker info &> /dev/null; then
        echo "❌ Docker is not running."
        echo "Please start Docker Desktop first."
        return 1
    fi
    
    return 0
}

# Function to start services
start_services() {
    echo "🚀 Starting BeyTV services..."
    
    if ! check_docker; then
        return 1
    fi
    
    # Start Docker services
    docker compose up -d
    
    if [ $? -eq 0 ]; then
        echo "✅ Docker services started!"
        
        # Create directories
        mkdir -p downloads media config/qb config/plex public
        
        echo ""
        echo "🌐 Opening BeyFlow dashboard..."
        if command -v open &> /dev/null; then
            open "$(pwd)/beyflow.html"
        fi
        
        echo ""
        echo "📋 Services available at:"
        echo "   • BeyFlow Dashboard: file://$(pwd)/beyflow.html"
        echo "   • qBittorrent: http://localhost:8080"
        echo "   • Plex: http://localhost:32400/web"
        echo ""
        echo "Next steps:"
        echo "   • ./beytv.sh ratings  - Start ratings dashboard"
        echo "   • ./beytv.sh indexer  - Start torrent indexer"
        echo "   • ./beytv.sh notify   - Setup notifications"
        echo "   • ./beytv.sh scheduler - Setup automated scheduling"
        echo "   • ./beytv.sh router   - Configure storage routing"
    else
        echo "❌ Failed to start Docker services"
        return 1
    fi
}

# Function to stop services
stop_services() {
    echo "🛑 Stopping BeyTV services..."
    
    if ! check_docker; then
        return 1
    fi
    
    docker compose down
    echo "✅ All services stopped"
}

# Function to restart services
restart_services() {
    echo "🔄 Restarting BeyTV services..."
    stop_services
    sleep 2
    start_services
}

# Function to show status
show_status() {
    echo "📊 BeyTV Service Status"
    echo "====================="
    echo ""
    
    if ! check_docker; then
        return 1
    fi
    
    echo "Docker Services:"
    docker compose ps
    
    echo ""
    echo "Port Status:"
    echo "  8080 (qBittorrent): $(nc -z localhost 8080 && echo "✅ Open" || echo "❌ Closed")"
    echo "  32400 (Plex):       $(nc -z localhost 32400 && echo "✅ Open" || echo "❌ Closed")"
    echo "  8088 (Ratings):     $(nc -z localhost 8088 && echo "✅ Open" || echo "❌ Closed")"
    echo "  8089 (Indexer):     $(nc -z localhost 8089 && echo "✅ Open" || echo "❌ Closed")"
}

# Function to show logs
show_logs() {
    echo "📋 BeyTV Service Logs"
    echo "===================="
    
    if ! check_docker; then
        return 1
    fi
    
    docker compose logs --tail=50 -f
}

# Function for initial setup
initial_setup() {
    echo "⚙️ BeyTV Initial Setup"
    echo "====================="
    
    # Run main setup
    ./setup.sh
}

# Function for ratings
start_ratings() {
    echo "⭐ Starting Ratings Dashboard"
    echo "============================="
    
    ./start_ratings.sh
}

# Function for notifications
setup_notifications() {
    echo "📱 Setting up Notifications"
    echo "==========================="
    
    ./start_notifier.sh
}

# Function for indexer
start_indexer() {
    echo "🔍 Starting Torrent Indexer"
    echo "============================"
    
    ./start_indexer.sh
}

# Function for scheduler
setup_scheduler() {
    echo "⏰ Setting up Scheduler"
    echo "======================"
    
    ./setup_scheduler.sh
}

# Function for router
setup_router() {
    echo "💾 Setting up Storage Router"
    echo "==========================="
    
    ./start_router.sh
}

# Main script logic
case "${1:-}" in
    "start")
        start_services
        ;;
    "stop")
        stop_services
        ;;
    "restart")
        restart_services
        ;;
    "status")
        show_status
        ;;
    "setup")
        initial_setup
        ;;
    "ratings")
        start_ratings
        ;;
    "notify")
        setup_notifications
        ;;
    "indexer")
        start_indexer
        ;;
    "scheduler")
        setup_scheduler
        ;;
    "router")
        setup_router
        ;;
    "logs")
        show_logs
        ;;
    "")
        show_usage
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo ""
        show_usage
        exit 1
        ;;
esac
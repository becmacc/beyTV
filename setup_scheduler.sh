#!/bin/bash

# BeyTV Scheduler Setup
echo "⏰ BeyTV Scheduler Setup"
echo "======================"
echo ""
echo "This will set up automated scheduling for qBittorrent:"
echo "• Start qBittorrent at 12:01 AM (midnight)"
echo "• Stop qBittorrent at 6:01 AM"
echo "• Optional: Throttle speeds during day hours"
echo ""

# Get current directory
CURRENT_DIR="$(pwd)"
SCHEDULER_DIR="$CURRENT_DIR/scheduler"

# Check if scheduler directory exists
if [ ! -d "$SCHEDULER_DIR" ]; then
    echo "❌ Scheduler directory not found at $SCHEDULER_DIR"
    exit 1
fi

# Make scripts executable
echo "🔧 Making scheduler scripts executable..."
chmod +x "$SCHEDULER_DIR"/*.sh

# Update crontab with correct paths
echo "📝 Updating crontab with correct paths..."
TEMP_CRONTAB=$(mktemp)

# Replace placeholder paths in crontab.txt
sed "s|/path/to/scheduler|$SCHEDULER_DIR|g" "$SCHEDULER_DIR/crontab.txt" > "$TEMP_CRONTAB"

echo ""
echo "📋 Proposed crontab entries:"
echo "=============================="
cat "$TEMP_CRONTAB"
echo "=============================="
echo ""

# Ask for confirmation
read -p "Install these crontab entries? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Backup current crontab
    echo "💾 Backing up current crontab..."
    crontab -l > "$CURRENT_DIR/crontab_backup_$(date +%Y%m%d_%H%M%S).txt" 2>/dev/null || echo "No existing crontab found"
    
    # Install new crontab (append to existing)
    echo "⏰ Installing scheduler crontab..."
    (crontab -l 2>/dev/null; echo ""; echo "# BeyTV Scheduler - Added $(date)"; cat "$TEMP_CRONTAB") | crontab -
    
    echo "✅ Scheduler installed successfully!"
    echo ""
    echo "📅 Schedule Overview:"
    echo "   • 12:01 AM - qBittorrent starts"
    echo "   • 6:01 AM  - qBittorrent stops"
    echo "   • 7:00 AM-11:00 PM - Optional throttling (if enabled)"
    echo ""
    echo "🔧 Configuration:"
    echo "   • Edit scheduler/day_throttle.sh to configure speed limits"
    echo "   • Update qBittorrent credentials in day_throttle.sh if needed"
    echo ""
    echo "📋 Management commands:"
    echo "   • View crontab: crontab -l"
    echo "   • Remove scheduler: crontab -e (and delete BeyTV lines)"
    echo "   • View logs: tail -f /tmp/beytv_*.log"
    
else
    echo "❌ Installation cancelled"
    echo ""
    echo "📝 To install manually:"
    echo "   crontab $TEMP_CRONTAB"
fi

# Cleanup
rm -f "$TEMP_CRONTAB"

echo ""
echo "🎬 BeyTV Scheduler setup complete!"
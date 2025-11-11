#!/bin/bash
# Auto-Reveal Monitoring Script
# Tracks auto-advance cycle completion and timing

echo "🔍 1280 Trivia - Auto-Reveal Monitor"
echo "===================================="
echo ""

# Check if server is running
if ! curl -s http://localhost:5001/ > /dev/null; then
    echo "❌ Server is not running on port 5001"
    exit 1
fi

echo "✅ Server is running"
echo ""

# Monitor log file (adjust path as needed)
LOG_FILE="${1:-/dev/stdin}"

if [ "$LOG_FILE" = "/dev/stdin" ]; then
    echo "📊 Monitoring live logs (Ctrl+C to stop)..."
    echo "   Usage: $0 /path/to/logfile.log (to analyze existing logs)"
    echo ""
fi

# Track metrics
declare -A pending_rooms
declare -A reveal_times
declare -A advance_times

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Process logs
tail -f "$LOG_FILE" 2>/dev/null | while read -r line; do
    timestamp=$(echo "$line" | grep -oP '\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}')
    
    # Track auto_advance_pending
    if echo "$line" | grep -q "auto_advance_pending"; then
        room=$(echo "$line" | grep -oP "room_code['\"]?: ['\"]?\K[A-Z0-9]+")
        if [ -n "$room" ]; then
            pending_rooms[$room]=$timestamp
            echo -e "${YELLOW}⏳ [$timestamp] Room $room: Auto-advance started${NC}"
        fi
    fi
    
    # Track answer_revealed
    if echo "$line" | grep -q "answer_revealed"; then
        room=$(echo "$line" | grep -oP "room_code['\"]?: ['\"]?\K[A-Z0-9]+")
        is_poll=$(echo "$line" | grep -oP "is_poll['\"]?: \K(True|False)")
        
        if [ -n "$room" ] && [ -n "${pending_rooms[$room]}" ]; then
            reveal_times[$room]=$timestamp
            poll_indicator=""
            if [ "$is_poll" = "True" ]; then
                poll_indicator=" 🗳️  POLL"
            fi
            echo -e "${GREEN}✅ [$timestamp] Room $room: Answer revealed${poll_indicator}${NC}"
        fi
    fi
    
    # Track auto_advance_run
    if echo "$line" | grep -q "auto_advance_run"; then
        room=$(echo "$line" | grep -oP "room_code['\"]?: ['\"]?\K[A-Z0-9]+")
        
        if [ -n "$room" ] && [ -n "${pending_rooms[$room]}" ]; then
            advance_times[$room]=$timestamp
            echo -e "${GREEN}🎯 [$timestamp] Room $room: Advanced to next question${NC}"
            echo ""
            
            # Clear tracking for this room
            unset pending_rooms[$room]
            unset reveal_times[$room]
            unset advance_times[$room]
        fi
    fi
    
    # Detect stalls (pending > 10 seconds without reveal)
    for room in "${!pending_rooms[@]}"; do
        pending_time="${pending_rooms[$room]}"
        current_time=$(date +%s)
        pending_epoch=$(date -j -f "%Y-%m-%d %H:%M:%S" "$pending_time" +%s 2>/dev/null || echo 0)
        
        if [ $pending_epoch -gt 0 ]; then
            elapsed=$((current_time - pending_epoch))
            if [ $elapsed -gt 10 ]; then
                echo -e "${RED}⚠️  WARNING: Room $room stalled for ${elapsed}s${NC}"
            fi
        fi
    done
done

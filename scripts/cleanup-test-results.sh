#!/usr/bin/env bash
# Cleanup old test artifacts (14-day retention)
# Run this periodically or in CI to prevent test-results/ bloat

set -e

echo "🧹 Cleaning up test-results artifacts older than 14 days..."

# Remove old screenshot directories
if [ -d "test-results/screenshots" ]; then
    find test-results/screenshots -type d -mtime +14 -exec rm -rf {} + 2>/dev/null || true
    echo "  ✓ Cleaned old screenshots"
fi

# Remove old log files
if [ -d "test-results/logs" ]; then
    find test-results/logs -type f -mtime +14 -delete 2>/dev/null || true
    echo "  ✓ Cleaned old logs"
fi

# Remove old archive directories except the most recent 3
if [ -d "test-results/archive" ]; then
    cd test-results/archive
    ls -t | tail -n +4 | xargs -I {} rm -rf {} 2>/dev/null || true
    cd ../..
    echo "  ✓ Cleaned old archives (kept 3 most recent)"
fi

echo "✅ Cleanup complete!"
echo ""
echo "Current test-results size:"
du -sh test-results/ 2>/dev/null || echo "  (directory not found)"

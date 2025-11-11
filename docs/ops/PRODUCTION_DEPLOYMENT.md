# 1280 Trivia - Production Deployment Guide

**Version**: v1.0-auto-reveal  
**Last Updated**: 2025-11-10

---

## ⚠️ Critical Requirements

### Background Task Configuration

**MANDATORY**: The auto-reveal system uses Flask-SocketIO background tasks which require `use_reloader=False`.

**Why**: Background tasks (greenlets) do not survive across Flask's auto-reloader. Without this setting, auto-advance will fail silently after the first question.

---

## Production Startup

### Option 1: Using Flask CLI (Recommended)

```bash
# Activate virtual environment
source .venv/bin/activate

# Start production server
flask run --no-reload --host=0.0.0.0 --port=5001
```

### Option 2: Using run_server.py

Ensure `run_server.py` contains:

```python
if __name__ == '__main__':
    socketio.run(
        app,
        host='0.0.0.0',
        port=5001,
        debug=False,
        use_reloader=False  # CRITICAL: Required for background tasks
    )
```

Then run:

```bash
python run_server.py
```

### Option 3: Using Gunicorn (Production-Grade)

```bash
# Install gunicorn and eventlet
pip install gunicorn eventlet

# Start with eventlet worker (required for SocketIO)
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5001 run_server:app
```

**Note**: Use only 1 worker (`-w 1`) for in-memory game state. For multi-worker setups, implement Redis-based session storage.

---

## Environment Configuration

### Required Environment Variables

```bash
# Flask configuration
export FLASK_APP=run_server.py
export FLASK_ENV=production
export SECRET_KEY=<your-secret-key-here>

# Optional: Custom database path
export IMESSAGE_DB_PATH=/path/to/chat.db
```

### Production Settings Checklist

- [ ] `use_reloader=False` set
- [ ] `debug=False` set
- [ ] `SECRET_KEY` configured (not default)
- [ ] `host='0.0.0.0'` for external access
- [ ] Port configured (default: 5001)
- [ ] Firewall rules allow port 5001
- [ ] SSL/TLS configured (if public-facing)

---

## Monitoring & Logging

### Auto-Advance Cycle Monitoring

The system logs each auto-advance cycle:

```
auto_advance_pending → answer_revealed → auto_advance_run
```

**Expected timing**: 8 seconds total (5s delay + 3s delay)

### Key Metrics to Monitor

1. **Auto-advance completion rate**: Should be 100%
2. **Event timing**: 5000ms ±10ms, 3000ms ±10ms
3. **Race condition prevention**: Only one `auto_advance_pending` per question
4. **Poll scoring**: `is_poll: True` events should show scoring

### Log Locations

- **Application logs**: stdout/stderr
- **Test results**: `test-results/archive/v1.0-auto-reveal/`
- **Server logs**: Check your web server logs

### Recommended Monitoring Tools

- **CloudWatch** (AWS): Push logs for analysis
- **Grafana**: Real-time dashboard
- **Sentry**: Error tracking
- **Custom**: Parse logs for `auto_advance_pending` → `auto_advance_run` completion

---

## Health Checks

### Manual Verification

1. **Create a test game**:
   ```bash
   curl -X POST http://localhost:5001/api/game/create \
     -H "Content-Type: application/json" \
     -d '{"player_name":"TestHost","num_questions":3}'
   ```

2. **Check server logs** for:
   - `game_created` event
   - Room code generated
   - No errors

3. **Play through one question** with 2+ players
4. **Verify auto-advance** triggers after all answer
5. **Check logs** for complete cycle:
   ```
   all_players_answered → auto_advance_pending → 
   answer_revealed → auto_advance_run → new_question
   ```

### Automated Health Check Script

```bash
#!/bin/bash
# health_check.sh

RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5001/)

if [ $RESPONSE -eq 200 ]; then
    echo "✅ Server is healthy"
    exit 0
else
    echo "❌ Server returned $RESPONSE"
    exit 1
fi
```

---

## Troubleshooting

### Issue: Auto-advance not working

**Symptoms**: Game stalls after all players answer, no reveal happens

**Diagnosis**:
1. Check logs for `auto_advance_pending` event
2. If present but no `answer_revealed`, background task failed
3. If not present, check `all_players_answered` logic

**Solution**:
- Ensure `use_reloader=False` is set
- Restart server with correct configuration
- Check for exceptions in logs

### Issue: Duplicate auto-advance tasks

**Symptoms**: Multiple `auto_advance_pending` logs for same question

**Diagnosis**: Race condition protection failed

**Solution**:
- Verify `auto_advance_pending` flag is being set/reset
- Check `backend/app/game/engine.py:44` for flag definition
- Review `backend/app/routes/game.py:330-348` for flag logic

### Issue: Poll questions not scoring

**Symptoms**: Poll winners receive 0 points

**Diagnosis**:
1. Check logs for `answer_revealed | is_poll: True`
2. If missing, `get_answer_stats()` not being called

**Solution**:
- Verify auto-advance is working (see above)
- Check `backend/app/routes/game.py:82-84` for `get_answer_stats()` call

### Issue: Events out of order

**Symptoms**: `new_question` before `answer_revealed`

**Diagnosis**: Socket event timing issue

**Solution**:
- Check network latency
- Verify delays are correct (5s, 3s)
- Review `backend/app/routes/game.py:67-120` for timing logic

---

## Rollback Plan

If critical issues arise in production:

### Quick Rollback

```bash
# Revert to previous stable version
git checkout v0.9-stable  # Or your previous tag
git push origin main --force

# Restart server
systemctl restart trivia-game  # Or your service manager
```

### Manual Reveal Restoration

If auto-reveal must be disabled:

1. Restore reveal button in `frontend/templates/tv.html`
2. Restore `requestAnswerReveal()` in `frontend/static/js/tv.js`
3. Remove auto-advance trigger from `backend/app/routes/game.py:330-348`
4. Redeploy

---

## Performance Tuning

### Recommended Settings

- **Max concurrent games**: 50 (with 1 worker)
- **Max players per game**: 10
- **Question timeout**: 10-45 seconds (configurable)
- **Auto-advance delays**: 5s + 3s (hardcoded, future: configurable)

### Scaling Considerations

For >50 concurrent games:

1. **Implement Redis session storage** (replace in-memory state)
2. **Use multiple Gunicorn workers** (requires Redis)
3. **Add load balancer** (nginx or AWS ALB)
4. **Enable horizontal scaling** (multiple server instances)

---

## Security Checklist

- [ ] Change default `SECRET_KEY`
- [ ] Enable HTTPS/TLS for production
- [ ] Configure CORS properly
- [ ] Sanitize user inputs (player names, room codes)
- [ ] Rate limit API endpoints
- [ ] Implement session timeouts
- [ ] Review CSV question content for inappropriate material
- [ ] Remove personal data files (see CLEANUP_SUMMARY.md)

---

## Backup & Recovery

### Data to Backup

- **Question CSV files**: `*.csv` in root directory
- **Configuration**: `backend/app/config.py`
- **Custom questions**: Any user-generated content

### Recovery Procedure

1. Restore CSV files to root directory
2. Restore configuration files
3. Restart server
4. Verify health checks pass

**Note**: Game state is in-memory only. Active games will be lost on restart.

---

## Support & Maintenance

### Regular Maintenance Tasks

- **Weekly**: Review logs for errors
- **Monthly**: Update dependencies (`pip install -U -r requirements.txt`)
- **Quarterly**: Run full test suite (`npx playwright test`)
- **Annually**: Security audit

### Getting Help

- **Documentation**: See `/docs/` directory
- **Test Results**: `test-results/archive/`
- **Audit Reports**: `AUDIT_POST_AUTOREVEAL.md`
- **Implementation Details**: `AUTO_REVEAL_IMPLEMENTATION.md`

---

## Version History

- **v1.0-auto-reveal** (2025-11-10): Stable auto-reveal & scoring flow
  - Auto-reveal after all players answer
  - Poll scoring functional
  - Race condition protection
  - All tests passing (15/15)

---

## Quick Reference

```bash
# Start production server
flask run --no-reload --host=0.0.0.0 --port=5001

# Check server status
curl http://localhost:5001/

# View logs
tail -f /var/log/trivia-game.log  # Or your log location

# Run tests
npx playwright test --project=chromium-desktop

# Create backup
tar -czf backup-$(date +%Y%m%d).tar.gz *.csv backend/app/config.py
```

---

**Last Validated**: 2025-11-10  
**Test Suite**: Playwright (15/15 passing)  
**Status**: ✅ Production Ready

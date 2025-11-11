# 1280 Trivia – Load Test Audit: Auto-Reveal Under Stress

**Purpose**: Validate auto-reveal system performance under concurrent load  
**Status**: 📋 TEMPLATE - Run when scaling to public beta  
**Prerequisites**: v1.0-auto-reveal deployed and stable

---

## Objectives

1. Verify auto-reveal works correctly with 10-50 concurrent games
2. Measure event latency under load
3. Test reconnect recovery during high traffic
4. Identify performance bottlenecks
5. Validate race condition protection at scale

---

## Test Scenarios

### Scenario 1: 10 Concurrent Games
**Setup**: 10 games, 4 players each (40 total connections)  
**Duration**: 10 minutes  
**Expected**: All auto-reveals complete within 8.5 seconds

**Metrics to Track**:
- Auto-advance completion rate: Target 100%
- Average reveal latency: Target <100ms
- Socket event throughput: Target >100 events/sec
- Memory usage: Track growth over time
- CPU usage: Should stay <50%

### Scenario 2: 25 Concurrent Games
**Setup**: 25 games, 4 players each (100 total connections)  
**Duration**: 15 minutes  
**Expected**: All auto-reveals complete within 9 seconds

**Metrics to Track**:
- Auto-advance completion rate: Target >95%
- Average reveal latency: Target <200ms
- Socket event throughput: Target >250 events/sec
- Memory usage: Should not exceed 1GB
- CPU usage: Should stay <70%

### Scenario 3: 50 Concurrent Games (Stress Test)
**Setup**: 50 games, 4 players each (200 total connections)  
**Duration**: 20 minutes  
**Expected**: System remains stable, some degradation acceptable

**Metrics to Track**:
- Auto-advance completion rate: Target >90%
- Average reveal latency: Target <500ms
- Socket event throughput: Measure actual
- Memory usage: Monitor for leaks
- CPU usage: Monitor for saturation

### Scenario 4: Reconnect Storm
**Setup**: 10 games, simulate 50% of players disconnecting/reconnecting every 30 seconds  
**Duration**: 10 minutes  
**Expected**: Games continue, no state corruption

**Metrics to Track**:
- State consistency: All games should complete
- Reconnect success rate: Target >95%
- Event replay: Verify clients catch up
- Memory leaks: Check for orphaned sessions

### Scenario 5: Rapid Game Creation/Deletion
**Setup**: Create and complete 100 games in 30 minutes  
**Duration**: 30 minutes  
**Expected**: No memory leaks, all games clean up properly

**Metrics to Track**:
- Memory growth: Should be minimal
- Session cleanup: Verify all sessions deleted
- Room code reuse: Should work correctly
- Database connections: Should not leak

---

## Load Test Tools

### Option 1: Playwright (Recommended)
```typescript
// tests/load-test.spec.ts
import { test } from '@playwright/test';

test('10 concurrent games', async ({ browser }) => {
  const games = [];
  
  for (let i = 0; i < 10; i++) {
    const context = await browser.newContext();
    games.push(simulateGame(context, 4)); // 4 players
  }
  
  await Promise.all(games);
});
```

### Option 2: Artillery
```yaml
# artillery-load-test.yml
config:
  target: 'http://localhost:5001'
  phases:
    - duration: 600
      arrivalRate: 5
      name: "Ramp up to 50 games"

scenarios:
  - name: "Complete game flow"
    engine: socketio
    flow:
      - emit:
          channel: "create_room"
      - think: 2
      - emit:
          channel: "join_game"
          data:
            room_code: "{{ room_code }}"
            player_name: "Player{{ $uuid }}"
```

### Option 3: Locust
```python
# locustfile.py
from locust import HttpUser, task, between

class TriviaUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def play_game(self):
        # Create game
        response = self.client.post("/api/game/create", json={
            "player_name": "LoadTestPlayer"
        })
        room_code = response.json()["room_code"]
        
        # Join game
        # Submit answers
        # Complete game
```

---

## Metrics Collection

### Server Metrics
```bash
# CPU and Memory
top -l 1 | grep "1280 Trivia"

# Network connections
netstat -an | grep :5001 | wc -l

# Socket.IO connections
# Add to backend/app/__init__.py:
@socketio.on('connect')
def handle_connect():
    active_connections.inc()
    
@socketio.on('disconnect')
def handle_disconnect():
    active_connections.dec()
```

### Application Metrics
```python
# Add to backend/app/routes/game.py
import time

auto_advance_timings = []

def auto_advance_after_all_answered(room_code: str):
    start_time = time.time()
    try:
        # ... existing logic
    finally:
        duration = time.time() - start_time
        auto_advance_timings.append(duration)
        
        # Log if slow
        if duration > 9.0:
            logger.warning(f"Slow auto-advance: {duration:.2f}s for {room_code}")
```

---

## Success Criteria

### Must Pass
- [ ] Auto-advance completion rate >95% at 10 concurrent games
- [ ] Auto-advance completion rate >90% at 25 concurrent games
- [ ] No memory leaks (stable memory over 30 minutes)
- [ ] No state corruption (all games complete successfully)
- [ ] Event order preserved (no out-of-order events)

### Should Pass
- [ ] Average latency <200ms at 25 concurrent games
- [ ] CPU usage <70% at 25 concurrent games
- [ ] Reconnect success rate >95%
- [ ] No duplicate auto-advance tasks

### Nice to Have
- [ ] System handles 50 concurrent games
- [ ] Average latency <500ms at 50 concurrent games
- [ ] Graceful degradation under extreme load

---

## Failure Scenarios to Test

1. **Server restart during auto-advance**: Verify games recover or fail gracefully
2. **Network partition**: Simulate network split, verify reconnect
3. **Slow client**: One client with 5-second latency, verify others unaffected
4. **Malicious client**: Rapid answer submissions, verify rate limiting
5. **Database unavailable**: If using persistent storage, test failure modes

---

## Bottleneck Analysis

### Likely Bottlenecks
1. **In-memory state**: Single-process limitation
2. **Socket.IO broadcasting**: O(n) for each event
3. **Background task scheduling**: Greenlet overhead
4. **JSON serialization**: Large payloads slow down

### Optimization Strategies
1. **Redis session storage**: Enable multi-worker scaling
2. **Event batching**: Combine multiple events into one
3. **Lazy loading**: Don't send full game state on every update
4. **Connection pooling**: Reuse database connections
5. **CDN for static assets**: Reduce server load

---

## Report Template

```markdown
# Load Test Results - [Date]

## Configuration
- Concurrent games: X
- Players per game: Y
- Duration: Z minutes
- Server: [specs]

## Results
- Auto-advance completion rate: X%
- Average latency: Xms (p50), Xms (p95), Xms (p99)
- Peak throughput: X events/sec
- Memory usage: X MB (start) → Y MB (end)
- CPU usage: X% (avg), Y% (peak)

## Issues Found
1. [Issue description]
   - Severity: High/Medium/Low
   - Frequency: X% of games
   - Root cause: [analysis]
   - Recommendation: [fix]

## Recommendations
1. [Optimization 1]
2. [Optimization 2]

## Conclusion
[Pass/Fail] - [Summary]
```

---

## Next Steps After Load Test

### If Tests Pass
1. Document performance limits in production guide
2. Set up monitoring alerts for key metrics
3. Plan capacity for expected user growth
4. Schedule regular load tests (quarterly)

### If Tests Fail
1. Identify bottleneck from metrics
2. Implement optimization (Redis, caching, etc.)
3. Re-run load test
4. Update architecture if needed

---

## Tools & Resources

- **Playwright**: https://playwright.dev/
- **Artillery**: https://artillery.io/
- **Locust**: https://locust.io/
- **Grafana**: https://grafana.com/
- **Prometheus**: https://prometheus.io/

---

**Status**: 📋 Template ready for execution  
**Run when**: Preparing for public beta or >50 expected concurrent users  
**Estimated time**: 4-8 hours (setup + execution + analysis)

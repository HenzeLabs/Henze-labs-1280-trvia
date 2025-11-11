# Testing - Quick Reference

**Need to validate security fixes? Start here!**

---

## 🚀 Quick Start (Choose One)

### Option 1: Lightning Fast (2 minutes)
```bash
# Start server in one terminal
python3 run_server.py

# Run quick checks in another terminal
./quick-smoke-test.sh
```
✅ Tests: Disabled endpoints, DoS protection, server health

### Option 2: Full Validation (5 minutes)
```bash
# One command - handles everything
./run-regression-tests.sh
```
✅ Tests: All 10 security bugs + 3-player game flow + console errors

### Option 3: Manual Step-by-Step
See: [docs/audits/REGRESSION_TEST_CHECKLIST.md](docs/audits/REGRESSION_TEST_CHECKLIST.md)

---

## 📋 What Gets Tested?

### Security Regression Tests
1. **BUG #1**: Host authorization (start/next game)
2. **BUG #2**: HTTP answer endpoint disabled
3. **BUG #3**: XSS prevention (player names)
4. **BUG #4**: Answer leak endpoint disabled
5. **BUG #5**: Cross-room data protection
6. **BUG #6**: Anonymous socket blocking
7. **BUG #7**: UUID player IDs
8. **BUG #8**: Anonymous game state blocked
9. **BUG #9**: DoS protection (question limits)
10. **BUG #10**: No answer leak before reveal

### Gameplay Tests
- Room creation & join flow
- Multiple players (2-3)
- Answer submission
- Question progression
- Frontend console errors

---

## 🎯 Expected Results

### ✅ All Tests Pass
```
✅ ALL SECURITY REGRESSION TESTS PASSED
✅ 8/8 Playwright tests passed
✅ No critical console errors
```
**→ Deploy with confidence!**

### ❌ Some Tests Fail
Check:
- [TESTING_GUIDE.md](docs/audits/TESTING_GUIDE.md) - Troubleshooting
- [REGRESSION_TEST_CHECKLIST.md](docs/audits/REGRESSION_TEST_CHECKLIST.md) - Known breaking changes
- `/tmp/trivia_regression_test.log` - Server logs
- `npx playwright show-report` - Test details

---

## 📚 Full Documentation

| Document | Purpose | Time |
|----------|---------|------|
| [SECURITY_AUDIT_SUMMARY.md](SECURITY_AUDIT_SUMMARY.md) | Executive summary, all fixes | 5 min read |
| [TESTING_GUIDE.md](docs/audits/TESTING_GUIDE.md) | Complete testing manual | 10 min read |
| [REGRESSION_TEST_CHECKLIST.md](docs/audits/REGRESSION_TEST_CHECKLIST.md) | Manual test steps | 15 min to execute |
| [KNOWN_ISSUES.md](docs/audits/KNOWN_ISSUES.md) | All bug documentation | Reference |

---

## 🛠 Troubleshooting

**Server won't start:**
```bash
pip3 install -r requirements.txt
pkill -f "python.*run_server.py"
python3 run_server.py
```

**Tests fail:**
```bash
# View detailed logs
tail -100 /tmp/trivia_regression_test.log

# Run with browser visible
npx playwright test tests/security-regression.spec.ts --headed

# Check Playwright report
npx playwright show-report
```

**Port 5001 in use:**
```bash
lsof -ti:5001 | xargs kill
```

---

## 🎓 For Developers

### Run Specific Tests
```bash
# Security regression only
npx playwright test tests/security-regression.spec.ts

# Existing smoke tests
npx playwright test tests/simplified-game-flow.spec.ts

# Full UI tour
npx playwright test tests/ui-tour.spec.ts
```

### Debug Mode
```bash
npx playwright test --headed --workers=1
npx playwright test --debug
```

### CI/CD Integration
See: [TESTING_GUIDE.md](docs/audits/TESTING_GUIDE.md#cicd-integration)

---

## ✅ Pre-Deployment Checklist

Before deploying v1.6:

- [ ] `./quick-smoke-test.sh` passes
- [ ] `./run-regression-tests.sh` passes
- [ ] Manual 3-player game completes
- [ ] No console errors in browser
- [ ] Review [SECURITY_AUDIT_SUMMARY.md](SECURITY_AUDIT_SUMMARY.md)

---

**Questions?** Check the full guides in [docs/audits/](docs/audits/)

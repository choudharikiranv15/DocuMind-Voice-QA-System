# 🔥 DocuMind Voice - Production Load Testing Guide

**Purpose:** Verify system performance under realistic production scenarios (200-300 concurrent users)

---

## 📋 Overview

The `load_test.py` script performs comprehensive production load testing to ensure the system can handle:
- 200-300 concurrent users
- Mixed operation scenarios (health checks, auth, uploads, queries)
- High request volumes
- Rate limiting under stress

---

## 🎯 Test Scenarios

### Test 1: Health Check Load (100 concurrent requests)
**Purpose:** Baseline server performance

**What it tests:**
- Server response under concurrent load
- Basic endpoint performance
- Connection handling

**Expected Results:**
- Success Rate: > 95%
- Average Response Time: < 500ms
- P95 Response Time: < 1s
- Requests/second: > 50

---

### Test 2: Concurrent Signups (30 users)
**Purpose:** User registration under load + rate limiting validation

**What it tests:**
- Database write performance
- Password hashing overhead (bcrypt)
- JWT token generation
- Rate limiting (3 signups/hour per IP)

**Expected Results:**
- First 3 signups: Success
- Subsequent signups: Rate limited (429)
- Average Response Time: < 2s
- No database errors

---

### Test 3: Concurrent Logins (100 attempts)
**Purpose:** Authentication system stress test

**What it tests:**
- Database read performance
- Password verification (bcrypt.checkpw)
- JWT generation
- Rate limiting (5 logins/minute per IP)
- Mix of valid and invalid attempts

**Expected Results:**
- Valid logins: Success
- Invalid logins: 401 Unauthorized
- After 5 attempts/minute: 429 Rate Limited
- Average Response Time: < 1s

---

### Test 4: Stress Test (200 concurrent mixed operations)
**Purpose:** Realistic production simulation

**Operation Mix:**
- 40% Health checks (monitoring, uptime checks)
- 30% Login attempts (returning users)
- 20% Signups (new users)
- 10% Other requests

**What it tests:**
- Overall system stability
- Resource contention
- Connection pooling
- Error rate under stress

**Expected Results:**
- Overall Success Rate: > 85%
- Error Rate: < 15%
- No server crashes
- Operations/second: > 30

---

## 📊 Performance Metrics Collected

### Response Time Metrics
- **Average:** Mean response time across all requests
- **Median:** 50th percentile (P50)
- **P95:** 95th percentile (what 95% of users experience)
- **Min/Max:** Best and worst case scenarios

### Success Metrics
- **Success Rate:** % of requests that returned 2xx status
- **Error Rate:** % of requests that failed
- **Rate Limited:** % of requests that hit 429

### Throughput Metrics
- **Requests/second:** Total throughput
- **Concurrent Requests:** Peak concurrency handled

---

## 🚀 How to Run Load Tests

### Prerequisites
1. **Start Flask Server:**
   ```bash
   cd backend
   python app.py
   ```
   Server must be running on `http://localhost:8080`

2. **Ensure all services are available:**
   - Database (Supabase)
   - Redis (Upstash) - optional, falls back to in-memory
   - LLM API (Groq)

### Run Tests
```bash
cd backend
python load_test.py
```

### Test Duration
- Total runtime: ~2-3 minutes
- Test 1 (Health): ~10 seconds
- Test 2 (Signups): ~20 seconds
- Test 3 (Logins): ~30 seconds
- Test 4 (Stress): ~60 seconds

---

## 📈 Expected Performance Targets

### Production Ready Criteria (95/100):
- ✅ **Success Rate:** > 90%
- ✅ **Average Response Time:** < 1.5s
- ✅ **P95 Response Time:** < 3s
- ✅ **Requests/second:** > 30
- ✅ **Rate Limiting:** Working correctly
- ✅ **No Server Crashes:** Under load

### Excellent Performance (100/100):
- ✅ **Success Rate:** > 95%
- ✅ **Average Response Time:** < 1s
- ✅ **P95 Response Time:** < 2s
- ✅ **Requests/second:** > 50
- ✅ **Error Rate:** < 5%

---

## 🔧 Current Configuration

### Flask Development Server:
- **Workers:** 1 (single-threaded)
- **Concurrency:** Limited
- **Best for:** Development, small testing

### Gunicorn Production Server (Configured):
- **Workers:** 4
- **Threads per Worker:** 2
- **Total Concurrent Requests:** 8
- **Timeout:** 120s
- **Best for:** Production, 150-200 users

### Recommended Deployment:
```bash
gunicorn app:app -c gunicorn.conf.py
```

---

## 🐛 Common Issues & Solutions

### Issue: High Error Rate (> 20%)
**Possible Causes:**
- Server overload (too many concurrent requests)
- Database connection pool exhausted
- LLM API rate limits hit

**Solutions:**
- Increase Gunicorn workers (2 x CPU cores)
- Enable connection pooling in database
- Add request queuing

---

### Issue: Slow Response Times (P95 > 5s)
**Possible Causes:**
- LLM query processing (2-3s typical)
- PDF processing overhead
- Cold start (first request slow)

**Solutions:**
- Cache common queries
- Optimize PDF processing
- Use async processing for heavy operations

---

### Issue: Rate Limiting Too Aggressive
**Symptoms:**
- Many 429 errors
- Legitimate users blocked

**Solutions:**
- Adjust rate limits in app.py:
  ```python
  @limiter.limit("10 per minute")  # Increase from 5
  ```
- Use Redis for distributed rate limiting
- Implement token bucket algorithm

---

## 📊 Sample Test Output

```
======================================================================
DOCUMIND VOICE - PRODUCTION LOAD TEST
======================================================================
Target: http://localhost:8080
Started: 2025-11-19 14:00:00
======================================================================

[INFO] Starting server warmup...
[OK] Server is up! Response time: 0.125s

[TEST 1] Health Check - 100 concurrent requests
======================================================================
  Progress: 20/100 requests completed
  Progress: 40/100 requests completed
  ...
  Progress: 100/100 requests completed

  Results:
    Total requests: 100
    Successful: 98 (98.0%)
    Failed: 2 (2.0%)
    Total time: 2.15s
    Requests/second: 46.51

  Response Times:
    Average: 0.245s
    Median: 0.198s
    Min: 0.089s
    Max: 1.234s
    P95: 0.567s

[TEST 2] User Signup - 30 concurrent registrations
======================================================================
  ...
  Results:
    Successful: 3 (10.0%)
    Rate limited: 27 (90.0%)  [EXPECTED]

[TEST 3] User Login - 100 concurrent attempts
======================================================================
  ...
  Rate limited (429): 35 (35.0%)  [EXPECTED after 5/minute]

[TEST 4] STRESS TEST - 200 concurrent mixed operations
======================================================================
  ...
  Results:
    Total operations: 200
    Errors: 18 (9.0%)
    Operations/second: 38.5

======================================================================
LOAD TEST SUMMARY
======================================================================

Total Requests: 430
  Health checks: 100
  Signups: 30
  Logins: 100
  Queries: 0

Overall Success Rate: 87.2%
  Status: [OK] GOOD - Minor optimizations needed

Response Time Performance:
  Average: 0.892s
  P95: 2.145s
  Status: [OK] GOOD - Acceptable response times

======================================================================
```

---

## 🎯 Production Capacity Estimates

### Current Setup (4 workers, 2 threads):
- **Concurrent Requests:** 8
- **Sustained Load:** 30-40 req/sec
- **Peak Load:** 50-60 req/sec (short bursts)
- **Recommended Users:** 150-200 concurrent

### Calculation:
- Average user makes 1 request/10 seconds
- 200 users = 20 requests/second (comfortable)
- Leaves headroom for traffic spikes

### Scaling Plan:
- **100-200 users:** Current (4 workers)
- **200-500 users:** 8 workers (16 concurrent)
- **500-1000 users:** 12 workers + load balancer
- **1000+ users:** Multiple servers + Redis session store

---

## 📝 Manual Testing Checklist

After running automated tests, verify manually:

- [ ] **Single User Flow**
  - [ ] Signup → Login → Upload → Query → Logout

- [ ] **Concurrent Users** (open 3-5 browser tabs)
  - [ ] Multiple simultaneous logins
  - [ ] Multiple simultaneous queries
  - [ ] Check for database lock issues

- [ ] **Rate Limiting**
  - [ ] Try 6 rapid logins → should get 429
  - [ ] Wait 1 minute → should work again

- [ ] **Large Files**
  - [ ] Upload 10MB PDF
  - [ ] Query while processing
  - [ ] Check memory usage

- [ ] **Error Handling**
  - [ ] Invalid credentials
  - [ ] Malformed requests
  - [ ] Missing auth tokens

---

## 🔗 Related Documentation

- **DEPLOYMENT_GUIDE.md** - Production deployment instructions
- **SENTRY_ALERTS_SETUP.md** - Monitoring and alerting
- **PRE_LAUNCH_CHECKLIST.md** - Pre-launch tasks
- **gunicorn.conf.py** - Production server configuration

---

## ✅ Success Criteria Summary

Your system is **production-ready** if:

✅ Health checks: > 95% success, < 500ms average
✅ Auth endpoints: Rate limiting working (3-5/min)
✅ Mixed load: > 85% success, < 2s P95
✅ No crashes under 200 concurrent operations
✅ Error rate < 15%
✅ Requests/second > 30

---

**Status:** ✅ Load testing script ready
**Next Step:** Run tests with production server (Gunicorn)
**Target:** 150-200 concurrent users
**Timeline:** Ready for beta launch

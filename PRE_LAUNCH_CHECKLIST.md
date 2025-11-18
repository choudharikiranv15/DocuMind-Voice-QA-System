# 🚀 PRE-LAUNCH CHECKLIST
## DocuMind Voice - Production Launch (150-200 Beta Users)

**Target**: Students, Teachers, Researchers, Law Professionals
**Timeline**: 1-2 Days to Production Ready
**Current Status**: 70/100 → Target: 95/100

---

## DAY 1: CRITICAL BLOCKERS (4-6 hours)

### 🚫 Priority 1: Production Server Setup (2 hours)
**Current**: Flask dev server (single-threaded, crashes with concurrent users)
**Target**: Gunicorn with 4 workers, 2 threads each

- [ ] **Install gunicorn**
  ```bash
  pip install gunicorn
  pip freeze > requirements.txt
  ```

- [ ] **Create gunicorn config**: `backend/gunicorn.conf.py`
  ```python
  import multiprocessing

  # Server socket
  bind = "0.0.0.0:8080"
  backlog = 2048

  # Worker processes
  workers = 4  # 2 × CPU cores recommended
  worker_class = 'sync'
  worker_connections = 1000
  threads = 2  # Allows 8 concurrent requests (4 workers × 2 threads)
  timeout = 120  # 2 minutes for long PDF processing
  keepalive = 5

  # Restart workers after N requests (prevent memory leaks)
  max_requests = 1000
  max_requests_jitter = 50

  # Logging
  accesslog = '-'  # stdout
  errorlog = '-'   # stderr
  loglevel = 'info'

  # Security
  limit_request_line = 4094
  limit_request_fields = 100
  limit_request_field_size = 8190
  ```

- [ ] **Update start command** in deployment docs
  ```bash
  gunicorn app:app -c gunicorn.conf.py
  ```

- [ ] **Test locally**:
  ```bash
  cd backend
  gunicorn app:app -c gunicorn.conf.py
  # Open http://localhost:8080 and test
  ```

---

### 🚫 Priority 2: Rate Limiting (1.5 hours)
**Current**: Only query limits (50/day), no brute-force protection
**Target**: IP-based rate limiting on login, signup, password reset

- [ ] **Install Flask-Limiter**
  ```bash
  pip install flask-limiter
  pip freeze > requirements.txt
  ```

- [ ] **Add to `backend/app.py`** (after CORS setup, around line 51):
  ```python
  from flask_limiter import Limiter
  from flask_limiter.util import get_remote_address

  # Rate limiter with Redis storage
  limiter = Limiter(
      app=app,
      key_func=get_remote_address,
      storage_uri=f"redis://{Config.UPSTASH_REDIS_REST_URL}" if Config.UPSTASH_REDIS_REST_URL else "memory://",
      default_limits=["200 per day", "50 per hour"]
  )
  ```

- [ ] **Add decorators to auth endpoints**:
  ```python
  @app.route('/auth/login', methods=['POST'])
  @limiter.limit("5 per minute")  # Prevent brute force
  def login():
      ...

  @app.route('/auth/signup', methods=['POST'])
  @limiter.limit("3 per hour")  # Prevent spam accounts
  def signup():
      ...

  @app.route('/auth/forgot-password', methods=['POST'])
  @limiter.limit("3 per hour")  # Already exists but add IP-based too
  def forgot_password():
      ...
  ```

- [ ] **Test rate limiting**:
  - Try logging in with wrong password 6 times → should block
  - Wait 1 minute → should work again

---

### 🚫 Priority 3: Environment Validation (30 mins)
**Current**: Fallback to random secrets if not set
**Target**: Fail fast with clear error messages

- [ ] **Add validation function** to `backend/app.py` (before app initialization, around line 20):
  ```python
  def validate_environment():
      """Validate required environment variables are set"""
      REQUIRED_VARS = {
          'GROQ_API_KEY': 'LLM service (required for chat)',
          'SUPABASE_URL': 'Database (required for auth & data)',
          'SUPABASE_KEY': 'Database authentication',
          'SECRET_KEY': 'Session security (generate with: python -c "import secrets; print(secrets.token_hex(32))")',
          'GEMINI_API_KEY': 'Image analysis (required for visual content)',
      }

      OPTIONAL_VARS = {
          'UPSTASH_REDIS_REST_URL': 'Caching (will use in-memory fallback)',
          'SENTRY_DSN': 'Error tracking (recommended for production)',
          'SAMBANOVA_API_KEY': 'LLM fallback provider',
      }

      missing_required = []
      missing_optional = []

      for var, description in REQUIRED_VARS.items():
          if not os.getenv(var):
              missing_required.append(f"  ❌ {var}: {description}")

      for var, description in OPTIONAL_VARS.items():
          if not os.getenv(var):
              missing_optional.append(f"  ⚠️  {var}: {description}")

      if missing_required:
          print("\n" + "="*70)
          print("CRITICAL: Missing Required Environment Variables")
          print("="*70)
          for msg in missing_required:
              print(msg)
          print("\nPlease set these variables in your .env file")
          print("="*70 + "\n")
          raise RuntimeError("Missing required environment variables. Cannot start.")

      if missing_optional:
          print("\n" + "="*70)
          print("WARNING: Missing Optional Environment Variables")
          print("="*70)
          for msg in missing_optional:
              print(msg)
          print("="*70 + "\n")

  # Call validation before app setup
  validate_environment()
  ```

- [ ] **Update `app.secret_key`** (remove fallback, around line 52):
  ```python
  # OLD: app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(16))
  # NEW: app.secret_key = os.getenv('SECRET_KEY')  # Will fail in validation if not set
  ```

- [ ] **Test validation**:
  - Rename `.env` to `.env.backup`
  - Try starting app → should show clear error
  - Rename back and verify startup works

---

### 🚫 Priority 4: Security Headers (30 mins)
**Current**: No security headers
**Target**: Protection against XSS, clickjacking, MIME sniffing

- [ ] **Install Flask-Talisman**
  ```bash
  pip install flask-talisman
  pip freeze > requirements.txt
  ```

- [ ] **Add to `backend/app.py`** (after app creation, around line 30):
  ```python
  from flask_talisman import Talisman

  # Security headers
  csp = {
      'default-src': "'self'",
      'script-src': ["'self'", "'unsafe-inline'", "'unsafe-eval'"],  # Allow React
      'style-src': ["'self'", "'unsafe-inline'"],  # Allow inline styles
      'img-src': ["'self'", 'data:', 'https:'],  # Allow images from CDNs
      'font-src': ["'self'", 'data:'],
      'connect-src': ["'self'", 'https://api.groq.com', 'https://*.supabase.co'],  # API endpoints
  }

  Talisman(
      app,
      content_security_policy=csp,
      content_security_policy_nonce_in=['script-src'],
      force_https=False,  # Set to True in production with HTTPS
      strict_transport_security=True,
      strict_transport_security_max_age=31536000,  # 1 year
      x_content_type_options=True,  # Prevent MIME sniffing
      x_frame_options='DENY',  # Prevent clickjacking
  )
  ```

- [ ] **Test security headers**:
  ```bash
  curl -I http://localhost:8080/health
  # Should see:
  # X-Content-Type-Options: nosniff
  # X-Frame-Options: DENY
  # Content-Security-Policy: ...
  ```

---

## DAY 2: HIGH PRIORITY FIXES (4-6 hours)

### ⚠️ Priority 5: File Upload Security (1 hour)

- [ ] **Add MIME type validation** in `backend/app.py` (around line 585):
  ```python
  import magic  # pip install python-magic-bin (Windows) or python-magic (Linux/Mac)

  @app.route('/upload', methods=['POST'])
  @require_auth
  def upload_document():
      # ... existing code ...

      # After file.save(filepath) around line 597
      # Verify MIME type
      try:
          mime = magic.Magic(mime=True)
          file_type = mime.from_file(filepath)

          if file_type != 'application/pdf':
              os.remove(filepath)  # Delete the file
              return jsonify({
                  'success': False,
                  'message': f'Invalid file type: {file_type}. Only PDF files are allowed.'
              }), 400
      except Exception as e:
          logger.error(f"MIME type check failed: {e}")
          # Continue anyway (don't block uploads if magic fails)
  ```

- [ ] **Install python-magic**:
  ```bash
  pip install python-magic-bin  # Windows
  # OR
  pip install python-magic  # Linux/Mac
  pip freeze > requirements.txt
  ```

- [ ] **Test with fake PDF** (rename .txt file to .pdf):
  - Should reject with "Invalid file type" error

---

### ⚠️ Priority 6: Mobile Responsiveness Testing (2 hours)

- [ ] **Test on actual mobile devices** (or Chrome DevTools):
  - [ ] iPhone (Safari)
  - [ ] Android (Chrome)
  - [ ] Tablet (iPad)

- [ ] **Test critical flows**:
  - [ ] **Login/Signup**: Forms should be readable, buttons tappable
  - [ ] **Document Upload**: Drag-drop should work or show file picker
  - [ ] **Chat Interface**:
    - Messages should wrap properly
    - Input field should resize for mobile keyboard
    - Voice recorder button should be large enough (min 44x44px)
  - [ ] **Profile Page**:
    - Usage dashboard should stack vertically on mobile
    - Settings should be scrollable
  - [ ] **Document List**: Cards should stack, no horizontal scroll

- [ ] **Fix issues found** (likely in `ChatInput.jsx`, `Message.jsx`, `Profile.jsx`)
  - Add `className="flex-wrap"` where needed
  - Adjust `min-width`, `max-width` for mobile
  - Test voice recording on mobile browsers

- [ ] **Update viewport meta tag** in `frontend/index.html`:
  ```html
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  ```

---

### ⚠️ Priority 7: Sentry Alert Configuration (30 mins)

- [ ] **Configure Sentry alerts** (in Sentry dashboard):
  - Go to Settings → Alerts → New Alert Rule
  - **Alert 1**: Error rate > 10 errors/hour
  - **Alert 2**: New issue created
  - **Alert 3**: Performance issue (P95 > 3 seconds)
  - Send to: Your email

- [ ] **Add custom error context** in `backend/app.py`:
  ```python
  from sentry_sdk import set_context, set_user

  @app.before_request
  def add_sentry_context():
      if current_user:  # If authenticated
          set_user({
              "id": current_user.user_id,
              "email": current_user.email,
          })

      set_context("request_info", {
          "url": request.url,
          "method": request.method,
          "ip": request.remote_addr,
      })
  ```

- [ ] **Test Sentry** (trigger error intentionally):
  ```python
  @app.route('/test-sentry')
  def test_sentry():
      1 / 0  # Trigger error
      return "This won't be reached"
  ```
  Visit `/test-sentry` and check Sentry dashboard for error

---

### ⚠️ Priority 8: Basic User Onboarding (2 hours)

- [ ] **Create sample documents** for new users:
  - `backend/data/samples/sample_student.pdf` - Study notes example
  - `backend/data/samples/sample_research.pdf` - Research paper example
  - `backend/data/samples/sample_legal.pdf` - Legal document example

- [ ] **Add first-time user tutorial** in `frontend/src/components/common/OnboardingTutorial.jsx`:
  ```jsx
  import { useState } from 'react'
  import { motion, AnimatePresence } from 'framer-motion'

  export default function OnboardingTutorial() {
      const [step, setStep] = useState(0)
      const [show, setShow] = useState(!localStorage.getItem('tutorial_completed'))

      const steps = [
          {
              title: "Welcome to DocuMind Voice! 👋",
              description: "Your AI-powered document assistant with voice support",
              action: "Get Started"
          },
          {
              title: "Upload Your Documents 📄",
              description: "Drag and drop PDFs or click to browse. Max 5 documents (10MB each) in beta.",
              action: "Next"
          },
          {
              title: "Ask Questions 💬",
              description: "Type or speak your questions. AI will search across all your documents.",
              action: "Next"
          },
          {
              title: "Voice Features 🎤",
              description: "Click the mic to ask questions with your voice. Responses can be read aloud.",
              action: "Finish"
          }
      ]

      const handleNext = () => {
          if (step < steps.length - 1) {
              setStep(step + 1)
          } else {
              localStorage.setItem('tutorial_completed', 'true')
              setShow(false)
          }
      }

      const handleSkip = () => {
          localStorage.setItem('tutorial_completed', 'true')
          setShow(false)
      }

      if (!show) return null

      return (
          <AnimatePresence>
              <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
              >
                  <motion.div
                      initial={{ scale: 0.9, y: 20 }}
                      animate={{ scale: 1, y: 0 }}
                      exit={{ scale: 0.9, y: 20 }}
                      className="bg-[#1e293b] rounded-2xl p-8 max-w-md w-full border border-white/10"
                  >
                      <h2 className="text-2xl font-bold text-white mb-3">
                          {steps[step].title}
                      </h2>
                      <p className="text-gray-300 mb-6">
                          {steps[step].description}
                      </p>

                      {/* Progress dots */}
                      <div className="flex gap-2 mb-6">
                          {steps.map((_, i) => (
                              <div
                                  key={i}
                                  className={`h-2 flex-1 rounded-full ${
                                      i <= step ? 'bg-cyan-500' : 'bg-white/20'
                                  }`}
                              />
                          ))}
                      </div>

                      <div className="flex gap-3">
                          <button
                              onClick={handleSkip}
                              className="px-4 py-2 text-gray-400 hover:text-white transition-colors"
                          >
                              Skip
                          </button>
                          <button
                              onClick={handleNext}
                              className="flex-1 px-6 py-3 bg-gradient-to-r from-cyan-500 to-purple-600 hover:from-cyan-600 hover:to-purple-700 text-white font-semibold rounded-lg transition-all"
                          >
                              {steps[step].action}
                          </button>
                      </div>
                  </motion.div>
              </motion.div>
          </AnimatePresence>
      )
  }
  ```

- [ ] **Add to Layout.jsx**:
  ```jsx
  import OnboardingTutorial from '../common/OnboardingTutorial'

  // In return statement:
  <OnboardingTutorial />
  ```

---

### ⚠️ Priority 9: IP-Based Rate Limiting (1 hour)

- [ ] **Add IP tracking** for abusive users:
  ```python
  # In backend/app.py, add middleware
  @app.before_request
  def track_ip():
      ip = request.remote_addr
      # Log suspicious patterns (many requests from same IP)
      redis_key = f"ip_requests:{ip}:{datetime.now().strftime('%Y%m%d%H')}"
      try:
          request_count = int(redis_client.get(redis_key) or 0)
          redis_client.incr(redis_key)
          redis_client.expire(redis_key, 3600)  # 1 hour

          if request_count > 1000:  # 1000 requests/hour from one IP
              logger.warning(f"Rate limit exceeded for IP {ip}: {request_count} requests")
              return jsonify({
                  'success': False,
                  'message': 'Too many requests. Please try again later.'
              }), 429
      except:
          pass  # Don't block if Redis unavailable
  ```

---

### ⚠️ Priority 10: Deployment Documentation (1.5 hours)

- [ ] **Create `DEPLOYMENT_PRODUCTION.md`** (separate file, created next)
- [ ] **Create `SECURITY_HARDENING.md`** (separate file, created next)
- [ ] **Create `TESTING_GUIDE.md`** (separate file, created next)

---

## FINAL CHECKS (Before Launch)

### Performance Testing
- [ ] Load test with 50 concurrent users (use `locust` or `ab`)
- [ ] Verify response times: P50 < 500ms, P95 < 2s, P99 < 5s
- [ ] Check memory usage doesn't exceed server limits
- [ ] Test PDF upload with max size file (10MB)

### Security Testing
- [ ] Run OWASP ZAP or similar security scanner
- [ ] Test SQL injection on search inputs
- [ ] Test XSS in document names/chat messages
- [ ] Verify rate limits work (try brute force login)
- [ ] Check CORS headers are correct

### Functional Testing
- [ ] Create account → Upload PDF → Ask questions → Get answers
- [ ] Test voice recording → transcription → answer with audio
- [ ] Test password reset flow
- [ ] Test document deletion
- [ ] Test usage limits (try uploading 6 documents)
- [ ] Test profile page (change password, email, delete account)

### Mobile Testing
- [ ] Test on iOS Safari
- [ ] Test on Android Chrome
- [ ] Test on tablet
- [ ] Verify responsive layouts
- [ ] Test voice features on mobile

### Monitoring Setup
- [ ] Verify Sentry is receiving errors
- [ ] Verify PostHog is tracking events
- [ ] Set up uptime monitoring (UptimeRobot or Pingdom)
- [ ] Configure email alerts for critical errors

---

## LAUNCH DAY CHECKLIST

### Pre-Launch (Morning)
- [ ] Deploy to production
- [ ] Run smoke tests on production URL
- [ ] Verify all environment variables set correctly
- [ ] Check database migrations ran successfully
- [ ] Verify Redis cache is connected
- [ ] Test one full user flow end-to-end

### Launch (Afternoon)
- [ ] Announce to first 10 beta users
- [ ] Monitor Sentry for errors
- [ ] Monitor server logs for issues
- [ ] Be ready to rollback if critical issues found

### Post-Launch (Evening)
- [ ] Gradually add more users (10 → 50 → 100 → 150-200)
- [ ] Monitor performance metrics
- [ ] Collect initial feedback
- [ ] Fix critical bugs immediately

---

## SUCCESS METRICS

**Week 1 Goals**:
- [ ] 150-200 users signed up
- [ ] < 5 critical errors/day in Sentry
- [ ] Average response time < 1 second
- [ ] 90% uptime (allow for minor issues)
- [ ] At least 50% of users upload a document
- [ ] Collect 20+ user feedback responses

**Week 2 Goals**:
- [ ] Address top 3 user pain points
- [ ] Improve performance based on metrics
- [ ] Reach 95%+ uptime
- [ ] Get 10+ positive reviews

---

## EMERGENCY CONTACTS

**Critical Issues**:
- Sentry Dashboard: [Your Sentry URL]
- Server Logs: Check hosting provider dashboard
- Database: Supabase dashboard
- Redis: Upstash dashboard

**Rollback Plan**:
If critical issues occur, rollback to previous version:
```bash
git revert HEAD
git push origin main
# Redeploy
```

---

## POST-LAUNCH IMPROVEMENTS (Week 2+)

### Based on User Feedback:
- [ ] Add most-requested features
- [ ] Improve based on error patterns
- [ ] Optimize slow endpoints
- [ ] Add more onboarding based on confusion points

### Technical Debt:
- [ ] Migrate JWT from localStorage to httpOnly cookies
- [ ] Add Celery task queue for heavy operations
- [ ] Implement token refresh mechanism
- [ ] Add automated testing (pytest)
- [ ] Set up CI/CD pipeline

---

**REMEMBER**:
- 🔒 Security first - don't compromise on auth/rate limiting
- 📱 Mobile matters - 60%+ of students use mobile
- 🐛 Bugs happen - monitor closely and fix fast
- 💬 Listen to users - they'll tell you what matters most

**Good luck with the launch! 🚀**

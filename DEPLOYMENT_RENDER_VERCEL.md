# 🚀 DEPLOYMENT GUIDE: Render + Vercel (Free Tier)
## DocuMind Voice - Production Deployment

**Backend**: Render.com (Free tier - 750 hours/month)
**Frontend**: Vercel (Free tier - Unlimited)
**Database**: Supabase (Free tier - 500MB, 2GB bandwidth)
**Redis**: Upstash (Free tier - 10K commands/day)

---

## 📋 PRE-DEPLOYMENT CHECKLIST

### 1. Environment Variables Ready
Create a file `ENVIRONMENT_VARIABLES.txt` with all your production values:

```bash
# === CRITICAL (REQUIRED) ===
GROQ_API_KEY=gsk_xxxxxxxxxxxxx
GEMINI_API_KEY=AIzaSyxxxxxxxxxx
SUPABASE_URL=https://xxxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxxxx
SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_hex(32))">

# === DATABASE ===
DATABASE_URL=postgresql://postgres:xxxxx@db.xxxxx.supabase.co:5432/postgres

# === REDIS (CACHING) ===
UPSTASH_REDIS_REST_URL=https://xxxxx.upstash.io
UPSTASH_REDIS_REST_TOKEN=AXxxxxxxxxxxxxx

# === ERROR TRACKING ===
SENTRY_DSN=https://xxxxx@sentry.io/xxxxx
SENTRY_ENVIRONMENT=production

# === ANALYTICS ===
POSTHOG_API_KEY=phc_xxxxxxxxxxxxx
POSTHOG_HOST=https://app.posthog.com

# === EMAIL ===
RESEND_API_KEY=re_xxxxxxxxxxxxx
FROM_EMAIL=noreply@yourdomain.com

# === LLM FALLBACKS (OPTIONAL) ===
SAMBANOVA_API_KEY=xxxxx
OPENROUTER_API_KEY=sk-or-xxxxx
HUGGINGFACE_API_TOKEN=hf_xxxxx

# === FRONTEND ===
VITE_API_BASE_URL=https://your-backend.onrender.com
VITE_SENTRY_DSN=https://xxxxx@sentry.io/xxxxx
VITE_POSTHOG_KEY=phc_xxxxxxxxxxxxx
```

### 2. Generate SECRET_KEY
```bash
python -c "import secrets; print(secrets.token_hex(32))"
# Copy the output to SECRET_KEY in your env vars
```

---

## 🔧 PART 1: BACKEND DEPLOYMENT (RENDER)

### Step 1: Prepare Backend for Render

#### A. Create `render.yaml` in project root
```yaml
services:
  - type: web
    name: documind-voice-backend
    env: python
    region: oregon  # Choose closest to your users
    plan: free
    buildCommand: |
      cd backend
      pip install -r requirements.txt
    startCommand: |
      cd backend
      gunicorn app:app -c gunicorn.conf.py
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: GROQ_API_KEY
        sync: false
      - key: GEMINI_API_KEY
        sync: false
      - key: SUPABASE_URL
        sync: false
      - key: SUPABASE_KEY
        sync: false
      - key: SECRET_KEY
        sync: false
      - key: DATABASE_URL
        sync: false
      - key: UPSTASH_REDIS_REST_URL
        sync: false
      - key: UPSTASH_REDIS_REST_TOKEN
        sync: false
      - key: SENTRY_DSN
        sync: false
      - key: SENTRY_ENVIRONMENT
        value: production
      - key: POSTHOG_API_KEY
        sync: false
      - key: RESEND_API_KEY
        sync: false
      - key: FROM_EMAIL
        sync: false
      - key: SAMBANOVA_API_KEY
        sync: false
      - key: OPENROUTER_API_KEY
        sync: false
      - key: HUGGINGFACE_API_TOKEN
        sync: false
```

#### B. Verify `backend/gunicorn.conf.py` exists
If not, create it:
```python
import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', '8080')}"
backlog = 2048

# Worker processes (Render free tier has 512MB RAM)
workers = 2  # Low for free tier
worker_class = 'sync'
worker_connections = 1000
threads = 2
timeout = 120  # 2 minutes for PDF processing
keepalive = 5

# Restart workers after N requests
max_requests = 500  # Lower for free tier
max_requests_jitter = 50

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
```

#### C. Update `backend/requirements.txt`
Add missing packages:
```bash
cd backend
pip install gunicorn flask-limiter flask-talisman python-magic-bin
pip freeze > requirements.txt
```

### Step 2: Deploy to Render

1. **Push code to GitHub**:
   ```bash
   git add .
   git commit -m "chore: Prepare for Render deployment"
   git push origin main
   ```

2. **Go to Render Dashboard**:
   - Visit https://render.com
   - Sign in with GitHub
   - Click "New +" → "Web Service"

3. **Connect Repository**:
   - Select your GitHub repository
   - Branch: `main`
   - Root directory: Leave empty (we have render.yaml)
   - Click "Apply"

4. **Render will auto-detect `render.yaml`**:
   - Review the configuration
   - Click "Create Web Service"

5. **Add Environment Variables**:
   - Go to "Environment" tab
   - Add all variables from `ENVIRONMENT_VARIABLES.txt`
   - Click "Save Changes"

6. **Wait for deployment** (5-10 minutes):
   - Watch the logs for errors
   - Once done, you'll get a URL: `https://documind-voice-backend.onrender.com`

7. **Test the backend**:
   ```bash
   curl https://documind-voice-backend.onrender.com/health
   # Should return: {"status": "healthy"}
   ```

### Step 3: Configure CORS for Frontend

- Note your backend URL: `https://documind-voice-backend.onrender.com`
- This will be used in frontend deployment

---

## 🎨 PART 2: FRONTEND DEPLOYMENT (VERCEL)

### Step 1: Prepare Frontend for Vercel

#### A. Create `vercel.json` in `frontend/` folder
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "framework": "vite",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        }
      ]
    }
  ]
}
```

#### B. Update `frontend/.env.example`
```bash
VITE_API_BASE_URL=https://documind-voice-backend.onrender.com
VITE_SENTRY_DSN=https://xxxxx@sentry.io/xxxxx
VITE_POSTHOG_KEY=phc_xxxxxxxxxxxxx
```

#### C. Create `.env.production` in `frontend/`
```bash
VITE_API_BASE_URL=https://documind-voice-backend.onrender.com
VITE_SENTRY_DSN=<your-sentry-dsn>
VITE_POSTHOG_KEY=<your-posthog-key>
```

### Step 2: Deploy to Vercel

1. **Push code to GitHub**:
   ```bash
   git add frontend/vercel.json frontend/.env.production
   git commit -m "chore: Configure Vercel deployment"
   git push origin main
   ```

2. **Go to Vercel Dashboard**:
   - Visit https://vercel.com
   - Sign in with GitHub
   - Click "Add New..." → "Project"

3. **Import Repository**:
   - Select your GitHub repository
   - Click "Import"

4. **Configure Project**:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

5. **Add Environment Variables**:
   - Click "Environment Variables"
   - Add:
     ```
     VITE_API_BASE_URL = https://documind-voice-backend.onrender.com
     VITE_SENTRY_DSN = <your-sentry-dsn>
     VITE_POSTHOG_KEY = <your-posthog-key>
     ```
   - Apply to: Production, Preview, Development

6. **Deploy**:
   - Click "Deploy"
   - Wait 2-3 minutes
   - You'll get a URL: `https://documind-voice.vercel.app`

### Step 3: Update Backend CORS

1. **Go back to Render dashboard**
2. **Update `CORS_ORIGINS` environment variable**:
   ```
   https://documind-voice.vercel.app,http://localhost:5173
   ```
3. **Save and redeploy**

---

## 🔐 PART 3: SECURITY CONFIGURATION

### 1. Update CORS in Backend

Edit `backend/app.py` if needed:
```python
cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:5173').split(',')
# Should include: https://documind-voice.vercel.app
```

### 2. Configure Supabase Auth

1. Go to Supabase Dashboard → Authentication → URL Configuration
2. Add Site URL: `https://documind-voice.vercel.app`
3. Add Redirect URLs:
   - `https://documind-voice.vercel.app/auth/callback`
   - `http://localhost:5173/auth/callback` (for development)

### 3. Configure Custom Domain (Optional)

**For Vercel**:
1. Go to Vercel → Settings → Domains
2. Add your domain (e.g., `app.yourdomain.com`)
3. Update DNS records as instructed
4. Enable HTTPS (automatic)

**For Render**:
1. Go to Render → Settings → Custom Domains
2. Add your domain (e.g., `api.yourdomain.com`)
3. Update DNS records
4. Wait for SSL certificate (automatic)

### 4. Update Environment Variables

Update both Render and Vercel with custom domain URLs if using.

---

## 📊 PART 4: MONITORING SETUP

### 1. Sentry Configuration

**Backend**:
- Already configured in `backend/src/error_tracking.py`
- Verify `SENTRY_DSN` is set in Render

**Frontend**:
- Already configured in `frontend/src/main.jsx`
- Verify `VITE_SENTRY_DSN` is set in Vercel

**Test Sentry**:
```bash
# Backend
curl https://your-backend.onrender.com/test-sentry

# Frontend
Open browser console → Trigger an error
```

### 2. PostHog Analytics

**Backend**:
- Already configured in `backend/src/analytics.py`
- Verify `POSTHOG_API_KEY` is set

**Frontend**:
- Configure in `frontend/src/services/analytics.js`

### 3. Uptime Monitoring

**Option 1: UptimeRobot (Free)**
1. Visit https://uptimerobot.com
2. Add monitor: `https://your-backend.onrender.com/health`
3. Check interval: 5 minutes
4. Alert contacts: Your email

**Option 2: Better Uptime (Free)**
1. Visit https://betteruptime.com
2. Add monitor for backend health endpoint
3. Configure alerts

### 4. Performance Monitoring

**Render Dashboard**:
- Monitor CPU, Memory, Response times
- Set up alerts for high resource usage

**Vercel Analytics** (Free tier limited):
- Go to Vercel → Analytics
- Enable Web Analytics
- Monitor page load times

---

## 🧪 PART 5: POST-DEPLOYMENT TESTING

### 1. Smoke Tests

Run these tests immediately after deployment:

```bash
# Health check
curl https://your-backend.onrender.com/health

# Frontend loads
open https://documind-voice.vercel.app

# Sign up flow
# (Manual test in browser)

# Upload document
# (Manual test in browser)

# Ask question
# (Manual test in browser)

# Voice recording
# (Manual test in browser)
```

### 2. Load Testing

```bash
# Install ab (Apache Bench)
# Linux/Mac: usually pre-installed
# Windows: Download from Apache

# Test with 50 concurrent users
ab -n 500 -c 50 https://your-backend.onrender.com/health

# Should handle without errors
```

### 3. Security Testing

```bash
# Test rate limiting
for i in {1..10}; do
  curl -X POST https://your-backend.onrender.com/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"test@test.com","password":"wrong"}'
done
# Should get rate limited after 5 attempts
```

---

## ⚠️ RENDER FREE TIER LIMITATIONS

### What to Expect:
- **512MB RAM** - Enough for 10-50 concurrent users
- **Sleeps after 15 min inactivity** - First request after sleep takes 30-60 seconds
- **750 hours/month** - ~31 days (enough for 24/7 if only one service)
- **No custom domains on free tier** - Use render.onrender.com subdomain

### How to Handle Cold Starts:
1. **Add warming pings** (every 14 minutes):
   ```bash
   # Use cron-job.org or similar
   curl https://your-backend.onrender.com/health
   ```

2. **Show loading state** in frontend:
   ```jsx
   {isLoading && (
     <div className="text-gray-400">
       Server waking up (this may take 30 seconds on first load)...
     </div>
   )}
   ```

### Memory Optimization:
- Sentence transformer model uses ~100MB
- Limit concurrent uploads: 1 at a time
- Clear audio files regularly (already implemented)

---

## 🚨 TROUBLESHOOTING

### Backend Won't Start
1. **Check Render logs**: Dashboard → Logs
2. **Common issues**:
   - Missing environment variables → Add in Render dashboard
   - Wrong Python version → Set `PYTHON_VERSION=3.11.0`
   - Port binding → Ensure gunicorn uses `$PORT` env var

### Frontend Build Fails
1. **Check Vercel logs**: Deployment → View Build Logs
2. **Common issues**:
   - Node version mismatch → Add `engines` in package.json
   - Missing env vars → Add in Vercel dashboard
   - Build command wrong → Should be `npm run build`

### CORS Errors
1. **Check backend `CORS_ORIGINS`**: Should include Vercel URL
2. **Restart backend** after changing CORS settings
3. **Clear browser cache** and test again

### Database Connection Fails
1. **Check `DATABASE_URL`** format
2. **Verify Supabase is accessible** from Render IPs
3. **Check connection pooling** in database.py

### Redis Connection Fails
1. **Verify Upstash credentials**
2. **Check free tier limits** (10K commands/day)
3. **App will fallback to in-memory** cache if Redis fails

---

## 📈 SCALING PLAN (When Free Tier Isn't Enough)

### Signs You Need to Upgrade:
- Consistently hitting 512MB RAM limit
- Response times > 3 seconds
- Cold starts affecting user experience
- > 100 concurrent users

### Upgrade Path:
1. **Render Starter ($7/month)**:
   - 512MB RAM → No cold starts
   - Better performance
   - Custom domains

2. **Render Standard ($25/month)**:
   - 2GB RAM → 200+ concurrent users
   - Autoscaling
   - Better support

3. **Future: Move to VPS**:
   - DigitalOcean/Linode ($12-20/month)
   - Full control
   - No cold starts
   - Can handle 1000+ users

---

## 🎉 LAUNCH CHECKLIST

Before announcing to users:

- [ ] Backend deployed and healthy
- [ ] Frontend deployed and accessible
- [ ] Can sign up new account
- [ ] Can upload PDF
- [ ] Can ask questions and get answers
- [ ] Voice recording works
- [ ] Mobile site is responsive
- [ ] Sentry receiving errors (test with /test-sentry)
- [ ] PostHog tracking events
- [ ] Uptime monitoring configured
- [ ] CORS configured correctly
- [ ] Rate limiting works
- [ ] Email sending works (test password reset)

---

## 📞 SUPPORT & MONITORING

### Daily Checks:
- [ ] Check Sentry for new errors
- [ ] Check Render logs for crashes
- [ ] Monitor response times in Vercel
- [ ] Check Redis usage in Upstash

### Weekly Checks:
- [ ] Review user feedback
- [ ] Check Supabase storage usage
- [ ] Review most common errors
- [ ] Optimize based on metrics

---

## 🔗 USEFUL LINKS

**Dashboards**:
- Render: https://dashboard.render.com
- Vercel: https://vercel.com/dashboard
- Supabase: https://app.supabase.com
- Upstash: https://console.upstash.com
- Sentry: https://sentry.io
- PostHog: https://app.posthog.com

**Documentation**:
- Render Docs: https://render.com/docs
- Vercel Docs: https://vercel.com/docs
- Supabase Docs: https://supabase.com/docs

**Support**:
- Render Status: https://status.render.com
- Vercel Status: https://www.vercel-status.com

---

**YOU'RE READY TO LAUNCH! 🚀**

Remember:
- Monitor closely for first 24-48 hours
- Respond quickly to user feedback
- Don't panic if something breaks - you can rollback
- Keep calm and iterate based on real user behavior

Good luck! 🎉

# 🚨 Sentry Alert Configuration Guide

## Overview
Configure Sentry alerts to get notified about critical errors in production.

---

## 🎯 Alert Rules to Create

### 1. Critical Error Alert
**Purpose:** Get notified immediately when critical errors occur

**Steps:**
1. Go to Sentry Dashboard → Settings → Alerts
2. Click "Create Alert Rule"
3. Configure:
   - **Alert Name:** "Critical Errors - Immediate Notification"
   - **Environment:** production
   - **Conditions:**
     - When: An event is seen
     - If: Level equals "error" OR "fatal"
     - And: The issue is "new"
   - **Actions:**
     - Send notification to: Your email
     - Send notification to: Slack (optional)
   - **Action Interval:** Every time

### 2. High Error Rate Alert
**Purpose:** Detect when error rate spikes above normal

**Steps:**
1. Create Alert Rule
2. Configure:
   - **Alert Name:** "High Error Rate (>10 errors/hour)"
   - **Environment:** production
   - **Conditions:**
     - When: Error count
     - Is: >= 10
     - In: 1 hour
   - **Actions:**
     - Send notification to: Your email
   - **Action Interval:** Once per hour

### 3. Performance Degradation Alert
**Purpose:** Detect when response times get too slow

**Steps:**
1. Create Alert Rule
2. Configure:
   - **Alert Name:** "Slow Response Times (P95 > 3s)"
   - **Environment:** production
   - **Conditions:**
     - When: P95 transaction duration
     - Is: >= 3000ms
     - In: 5 minutes
   - **Actions:**
     - Send notification to: Your email
   - **Action Interval:** Every 5 minutes

### 4. New Issue Alert
**Purpose:** Get notified about new types of errors

**Steps:**
1. Create Alert Rule
2. Configure:
   - **Alert Name:** "New Issue Detected"
   - **Environment:** production
   - **Conditions:**
     - When: An event is seen
     - If: The issue is "new"
   - **Actions:**
     - Send notification to: Your email
   - **Action Interval:** Every time

---

## 📧 Notification Channels

### Email Setup
1. Go to Settings → Integrations
2. Ensure your email is verified
3. Configure email preferences for alerts

### Slack Setup (Recommended)
1. Go to Settings → Integrations
2. Add Slack integration
3. Connect to your workspace
4. Select channel for alerts (e.g., #production-alerts)
5. Configure which alerts go to Slack

### Discord/PagerDuty (Optional)
- Similar process to Slack
- Useful for team notifications

---

## 🔧 Advanced Sentry Configuration

### Add Custom Context to Errors

The backend already includes user context in Sentry errors (added in app.py):

```python
from sentry_sdk import set_context, set_user

@app.before_request
def add_sentry_context():
    if hasattr(request, 'user_id'):  # If authenticated
        set_user({
            "id": request.user_id,
            "email": request.user_email if hasattr(request, 'user_email') else None,
        })

    set_context("request_info", {
        "url": request.url,
        "method": request.method,
        "ip": request.remote_addr,
    })
```

**To add this to app.py:**
1. Import: `from sentry_sdk import set_context, set_user`
2. Add the `@app.before_request` decorator function above
3. This will enrich all Sentry errors with user and request context

---

## 📊 Dashboard Setup

### Create Performance Dashboard
1. Go to Dashboards → Create Dashboard
2. Add widgets:
   - **Error Rate:** Line chart of errors over time
   - **Response Time:** P50, P95, P99 percentiles
   - **Most Common Errors:** Table of top 10 errors
   - **User Impact:** Users affected by errors

### Create Usage Dashboard
1. Create new dashboard: "DocuMind Voice - Usage Metrics"
2. Add widgets:
   - **Daily Active Users:** User count per day
   - **Document Uploads:** Upload count over time
   - **Query Success Rate:** Successful vs failed queries
   - **Average Response Time:** By endpoint

---

## 🧪 Test Alerts

### Test Error Tracking
```python
# Add temporary endpoint in app.py
@app.route('/test-sentry-alert')
def test_sentry_alert():
    """Test Sentry alert - DELETE after testing"""
    try:
        # Trigger a test error
        raise Exception("Test error for Sentry alert verification")
    except Exception as e:
        capture_exception(e, {'test': True})
        return jsonify({'message': 'Test error sent to Sentry'})
```

**Test steps:**
1. Deploy with this endpoint
2. Visit: `https://your-domain.com/test-sentry-alert`
3. Check Sentry dashboard for the error
4. Verify you receive email alert
5. Delete the test endpoint

---

## 📝 Alert Best Practices

### Don't Over-Alert
- ❌ Don't alert on every single error
- ✅ Alert on new issues and high error rates
- ✅ Use different severity levels

### Response Plan
When you get an alert:
1. **Check Sentry dashboard** for error details
2. **Assess severity:** Is it affecting multiple users?
3. **Check recent deployments:** Was this introduced in recent code?
4. **Fix or rollback:** Decide on immediate action
5. **Post-mortem:** Document what happened

### Error Grouping
- Sentry auto-groups similar errors
- Review grouping rules in Settings → Processing
- Merge duplicate issues manually if needed

---

## 🎯 Monitoring Checklist

### After Launch - Week 1
- [ ] Check Sentry daily for new issues
- [ ] Review error rate trends
- [ ] Tune alert thresholds based on actual traffic
- [ ] Fix top 3 most common errors

### After Launch - Week 2+
- [ ] Check Sentry weekly
- [ ] Review performance metrics
- [ ] Update alert rules based on patterns
- [ ] Add custom metrics for business logic

---

## 🔗 Quick Links

- **Sentry Dashboard:** https://sentry.io/organizations/your-org/
- **Alert Rules:** https://sentry.io/organizations/your-org/alerts/rules/
- **Performance:** https://sentry.io/organizations/your-org/performance/
- **Releases:** https://sentry.io/organizations/your-org/releases/

---

## 📈 Success Metrics

**Good Sentry Setup:**
- ✅ < 5 unresolved critical errors
- ✅ < 10 total errors per day (after initial fixes)
- ✅ P95 response time < 2 seconds
- ✅ All alerts have a response plan
- ✅ Team responds to alerts within 1 hour

---

**Last Updated:** 2025-11-19
**Status:** ✅ Ready for configuration

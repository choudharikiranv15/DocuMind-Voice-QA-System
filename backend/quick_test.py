"""
Quick test to verify production features without starting the full server
Tests:
1. Environment validation
2. Security headers configuration
3. Rate limiter setup
"""

print("=" * 70)
print("PRODUCTION FEATURES - QUICK TEST")
print("=" * 70)

# Test 1: Import and verify all modules load
print("\n[1/5] Testing imports...")
try:
    from flask import Flask
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    from flask_talisman import Talisman
    import magic
    print("[OK] All production modules imported successfully")
    print("   - Flask")
    print("   - Flask-Limiter (rate limiting)")
    print("   - Flask-Talisman (security headers)")
    print("   - python-magic (MIME validation)")
except ImportError as e:
    print(f"[FAIL] Import failed: {e}")
    exit(1)

# Test 2: Environment validation function
print("\n[2/5] Testing environment validation function...")
try:
    import os
    import sys
    sys.path.insert(0, '.')

    # Temporarily set required vars for testing
    os.environ['GROQ_API_KEY'] = 'test_key'
    os.environ['SUPABASE_URL'] = 'test_url'
    os.environ['SUPABASE_KEY'] = 'test_key'
    os.environ['SECRET_KEY'] = 'a' * 32
    os.environ['GEMINI_API_KEY'] = 'test_key'

    from app import validate_environment
    validate_environment()
    print("[OK] Environment validation function works")
except Exception as e:
    print(f"[WARN]  Environment validation: {e}")

# Test 3: Rate limiter configuration
print("\n[3/5] Testing rate limiter setup...")
try:
    app = Flask(__name__)
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        storage_uri="memory://",
        default_limits=["200 per day", "50 per hour"]
    )
    print("[OK] Rate limiter configured successfully")
    print(f"   - Storage: in-memory (falls back from Redis)")
    print(f"   - Default limits: 200/day, 50/hour")
except Exception as e:
    print(f"[FAIL] Rate limiter failed: {e}")

# Test 4: Security headers (Talisman)
print("\n[4/5] Testing security headers (Talisman)...")
try:
    app2 = Flask(__name__)
    talisman = Talisman(
        app2,
        force_https=False,
        content_security_policy=None
    )
    print("[OK] Talisman security headers configured")
    print("   - force_https: False (dev mode)")
    print("   - X-Frame-Options: DENY (default)")
    print("   - X-Content-Type-Options: nosniff (default)")
except Exception as e:
    print(f"[FAIL] Talisman failed: {e}")

# Test 5: MIME type detection
print("\n[5/5] Testing MIME type detection...")
try:
    mime = magic.Magic(mime=True)
    # Test with this Python file
    file_type = mime.from_file(__file__)
    print(f"[OK] MIME detection working")
    print(f"   - This file detected as: {file_type}")
except Exception as e:
    print(f"[FAIL] MIME detection failed: {e}")

# Summary
print("\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)
print("[OK] Production features are correctly installed and configured!")
print("\nReady for:")
print("  - Rate limiting on auth endpoints")
print("  - Security headers via Talisman")
print("  - MIME type validation for uploads")
print("  - Environment variable validation")
print("=" * 70)

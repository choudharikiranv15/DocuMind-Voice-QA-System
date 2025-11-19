"""
Production Load Testing Script for DokGuru Voice
Tests system under realistic production scenarios with 200-300 concurrent users
"""

import requests
import time
import threading
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import json
import random

BASE_URL = "http://127.0.0.1:8080"

# Test results storage
results = {
    'login': [],
    'signup': [],
    'upload': [],
    'query': [],
    'health': [],
    'errors': []
}

class LoadTester:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()

    def test_health_check(self):
        """Test health endpoint"""
        start = time.time()
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            elapsed = time.time() - start
            return {
                'success': response.status_code == 200,
                'time': elapsed,
                'status_code': response.status_code
            }
        except Exception as e:
            return {'success': False, 'time': time.time() - start, 'error': str(e)}

    def test_signup(self, user_id):
        """Test user signup"""
        start = time.time()
        try:
            data = {
                'email': f'loadtest_{user_id}_{int(time.time())}@test.com',
                'password': 'TestPassword123!',
                'role': random.choice(['student', 'professional', 'researcher']),
                'institution': 'Load Test University'
            }
            response = self.session.post(
                f"{self.base_url}/auth/signup",
                json=data,
                timeout=10
            )
            elapsed = time.time() - start

            result = {
                'success': response.status_code in [200, 201],
                'time': elapsed,
                'status_code': response.status_code
            }

            # Store token if successful
            if result['success']:
                result['token'] = response.json().get('token')

            return result
        except Exception as e:
            return {
                'success': False,
                'time': time.time() - start,
                'error': str(e)
            }

    def test_login(self, email, password):
        """Test user login"""
        start = time.time()
        try:
            data = {'email': email, 'password': password}
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json=data,
                timeout=10
            )
            elapsed = time.time() - start

            result = {
                'success': response.status_code == 200,
                'time': elapsed,
                'status_code': response.status_code
            }

            if result['success']:
                result['token'] = response.json().get('token')

            return result
        except Exception as e:
            return {
                'success': False,
                'time': time.time() - start,
                'error': str(e)
            }

    def test_query(self, token):
        """Test document query (RAG system)"""
        start = time.time()
        try:
            headers = {'Authorization': f'Bearer {token}'}
            data = {
                'question': random.choice([
                    'What is the main topic of this document?',
                    'Summarize the key points',
                    'What are the important dates mentioned?',
                    'Explain the methodology used',
                    'What are the conclusions?'
                ]),
                'language': 'auto'
            }
            response = self.session.post(
                f"{self.base_url}/ask",
                json=data,
                headers=headers,
                timeout=30  # Longer timeout for LLM processing
            )
            elapsed = time.time() - start

            return {
                'success': response.status_code == 200,
                'time': elapsed,
                'status_code': response.status_code
            }
        except Exception as e:
            return {
                'success': False,
                'time': time.time() - start,
                'error': str(e)
            }


def run_concurrent_health_checks(num_requests=100):
    """Test health endpoint with concurrent requests"""
    print(f"\n[TEST 1] Health Check - {num_requests} concurrent requests")
    print("=" * 70)

    start_time = time.time()

    with ThreadPoolExecutor(max_workers=50) as executor:
        tester = LoadTester()
        futures = [executor.submit(tester.test_health_check) for _ in range(num_requests)]

        completed = 0
        for future in as_completed(futures):
            result = future.result()
            results['health'].append(result)
            completed += 1
            if completed % 20 == 0:
                print(f"  Progress: {completed}/{num_requests} requests completed")

    elapsed = time.time() - start_time

    # Calculate statistics
    successful = [r for r in results['health'] if r['success']]
    failed = [r for r in results['health'] if not r['success']]
    times = [r['time'] for r in successful]

    print(f"\n  Results:")
    print(f"    Total requests: {num_requests}")
    print(f"    Successful: {len(successful)} ({len(successful)/num_requests*100:.1f}%)")
    print(f"    Failed: {len(failed)} ({len(failed)/num_requests*100:.1f}%)")
    print(f"    Total time: {elapsed:.2f}s")
    print(f"    Requests/second: {num_requests/elapsed:.2f}")

    if times:
        print(f"\n  Response Times:")
        print(f"    Average: {statistics.mean(times):.3f}s")
        print(f"    Median: {statistics.median(times):.3f}s")
        print(f"    Min: {min(times):.3f}s")
        print(f"    Max: {max(times):.3f}s")
        print(f"    P95: {statistics.quantiles(times, n=20)[18]:.3f}s" if len(times) > 20 else "    P95: N/A")


def run_concurrent_signups(num_users=50):
    """Test concurrent user signups"""
    print(f"\n[TEST 2] User Signup - {num_users} concurrent registrations")
    print("=" * 70)

    start_time = time.time()

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = []
        for i in range(num_users):
            tester = LoadTester()
            futures.append(executor.submit(tester.test_signup, i))

        completed = 0
        for future in as_completed(futures):
            result = future.result()
            results['signup'].append(result)
            completed += 1
            if completed % 10 == 0:
                print(f"  Progress: {completed}/{num_users} signups completed")

    elapsed = time.time() - start_time

    # Calculate statistics
    successful = [r for r in results['signup'] if r['success']]
    failed = [r for r in results['signup'] if not r['success']]
    times = [r['time'] for r in successful]

    print(f"\n  Results:")
    print(f"    Total signups: {num_users}")
    print(f"    Successful: {len(successful)} ({len(successful)/num_users*100:.1f}%)")
    print(f"    Failed: {len(failed)} ({len(failed)/num_users*100:.1f}%)")

    # Check for rate limiting
    rate_limited = [r for r in results['signup'] if r.get('status_code') == 429]
    if rate_limited:
        print(f"    Rate limited: {len(rate_limited)} (expected with 3/hour limit)")

    print(f"    Total time: {elapsed:.2f}s")

    if times:
        print(f"\n  Response Times:")
        print(f"    Average: {statistics.mean(times):.3f}s")
        print(f"    Median: {statistics.median(times):.3f}s")
        print(f"    P95: {statistics.quantiles(times, n=20)[18]:.3f}s" if len(times) > 20 else "    P95: N/A")


def run_concurrent_logins(num_logins=100):
    """Test concurrent logins (including invalid attempts to test rate limiting)"""
    print(f"\n[TEST 3] User Login - {num_logins} concurrent attempts")
    print("=" * 70)

    # Create a test user first
    tester = LoadTester()
    test_email = f'loadtest_login_{int(time.time())}@test.com'
    signup_result = tester.test_signup(999)

    if not signup_result['success']:
        print("  [WARN] Could not create test user for login test")
        return

    print(f"  Created test user: {test_email}")

    start_time = time.time()

    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = []
        for i in range(num_logins):
            tester = LoadTester()
            # Mix of valid and invalid attempts
            if i % 3 == 0:
                # Invalid password to test rate limiting
                futures.append(executor.submit(tester.test_login, test_email, 'WrongPassword'))
            else:
                # Valid login
                futures.append(executor.submit(tester.test_login, test_email, 'TestPassword123!'))

        completed = 0
        for future in as_completed(futures):
            result = future.result()
            results['login'].append(result)
            completed += 1
            if completed % 20 == 0:
                print(f"  Progress: {completed}/{num_logins} login attempts completed")

    elapsed = time.time() - start_time

    # Calculate statistics
    successful = [r for r in results['login'] if r['success']]
    failed = [r for r in results['login'] if not r['success']]
    rate_limited = [r for r in results['login'] if r.get('status_code') == 429]
    times = [r['time'] for r in successful]

    print(f"\n  Results:")
    print(f"    Total attempts: {num_logins}")
    print(f"    Successful: {len(successful)} ({len(successful)/num_logins*100:.1f}%)")
    print(f"    Failed: {len(failed)} ({len(failed)/num_logins*100:.1f}%)")
    print(f"    Rate limited (429): {len(rate_limited)} (Rate limit: 5/minute)")
    print(f"    Total time: {elapsed:.2f}s")

    if times:
        print(f"\n  Response Times:")
        print(f"    Average: {statistics.mean(times):.3f}s")
        print(f"    Median: {statistics.median(times):.3f}s")


def run_stress_test(num_concurrent=200):
    """Simulate production load with mixed operations"""
    print(f"\n[TEST 4] STRESS TEST - {num_concurrent} concurrent mixed operations")
    print("=" * 70)
    print("  Simulating realistic production scenario...")
    print("  - 40% Health checks")
    print("  - 30% Login attempts")
    print("  - 20% Signups")
    print("  - 10% Other requests")

    start_time = time.time()

    operations = []
    for i in range(num_concurrent):
        rand = random.random()
        if rand < 0.4:
            operations.append(('health', i))
        elif rand < 0.7:
            operations.append(('login', i))
        elif rand < 0.9:
            operations.append(('signup', i))
        else:
            operations.append(('health', i))

    completed = 0
    errors = 0

    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = []

        for op_type, op_id in operations:
            tester = LoadTester()
            if op_type == 'health':
                futures.append(executor.submit(tester.test_health_check))
            elif op_type == 'signup':
                futures.append(executor.submit(tester.test_signup, op_id))
            elif op_type == 'login':
                futures.append(executor.submit(tester.test_login, f'test{op_id}@test.com', 'password'))

        for future in as_completed(futures):
            try:
                result = future.result()
                if not result['success']:
                    errors += 1
            except Exception as e:
                errors += 1
                results['errors'].append(str(e))

            completed += 1
            if completed % 50 == 0:
                print(f"  Progress: {completed}/{num_concurrent} operations completed")

    elapsed = time.time() - start_time

    print(f"\n  Results:")
    print(f"    Total operations: {num_concurrent}")
    print(f"    Completed: {completed}")
    print(f"    Errors: {errors} ({errors/num_concurrent*100:.1f}%)")
    print(f"    Total time: {elapsed:.2f}s")
    print(f"    Operations/second: {num_concurrent/elapsed:.2f}")
    print(f"    Average concurrency: {num_concurrent/elapsed:.1f} req/s")


def print_summary():
    """Print final test summary"""
    print("\n" + "=" * 70)
    print("LOAD TEST SUMMARY")
    print("=" * 70)

    total_requests = (len(results['health']) + len(results['signup']) +
                     len(results['login']) + len(results['query']))

    print(f"\nTotal Requests: {total_requests}")
    print(f"  Health checks: {len(results['health'])}")
    print(f"  Signups: {len(results['signup'])}")
    print(f"  Logins: {len(results['login'])}")
    print(f"  Queries: {len(results['query'])}")

    if results['errors']:
        print(f"\nErrors encountered: {len(results['errors'])}")
        print("  First 5 errors:")
        for error in results['errors'][:5]:
            print(f"    - {error}")

    print("\n" + "=" * 70)
    print("PRODUCTION READINESS ASSESSMENT")
    print("=" * 70)

    # Calculate overall success rate
    all_results = results['health'] + results['signup'] + results['login'] + results['query']
    successful = sum(1 for r in all_results if r['success'])
    success_rate = (successful / total_requests * 100) if total_requests > 0 else 0

    print(f"\nOverall Success Rate: {success_rate:.1f}%")

    if success_rate >= 95:
        print("  Status: [OK] EXCELLENT - Production ready!")
    elif success_rate >= 85:
        print("  Status: [OK] GOOD - Minor optimizations needed")
    elif success_rate >= 70:
        print("  Status: [WARN] FAIR - Some issues need attention")
    else:
        print("  Status: [FAIL] POOR - Critical issues found")

    # Calculate average response times
    all_times = [r['time'] for r in all_results if r['success']]
    if all_times:
        avg_time = statistics.mean(all_times)
        p95_time = statistics.quantiles(all_times, n=20)[18] if len(all_times) > 20 else max(all_times)

        print(f"\nResponse Time Performance:")
        print(f"  Average: {avg_time:.3f}s")
        print(f"  P95: {p95_time:.3f}s")

        if p95_time < 2.0:
            print("  Status: [OK] EXCELLENT - Fast response times")
        elif p95_time < 3.0:
            print("  Status: [OK] GOOD - Acceptable response times")
        else:
            print("  Status: [WARN] SLOW - Optimization recommended")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    print("=" * 70)
    print("DokGuru VOICE - PRODUCTION LOAD TEST")
    print("=" * 70)
    print(f"Target: {BASE_URL}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    print("\n[INFO] Starting server warmup...")
    tester = LoadTester()
    warmup = tester.test_health_check()
    if not warmup['success']:
        print(f"\n[ERROR] Server not responding at {BASE_URL}")
        print("Please start the Flask server first:")
        print("  cd backend && python app.py")
        exit(1)

    print(f"[OK] Server is up! Response time: {warmup['time']:.3f}s\n")

    try:
        # Run tests in order
        run_concurrent_health_checks(num_requests=100)
        time.sleep(2)  # Brief pause between tests

        run_concurrent_signups(num_users=30)  # Reduced to avoid rate limiting
        time.sleep(2)

        run_concurrent_logins(num_logins=100)
        time.sleep(2)

        run_stress_test(num_concurrent=200)

        # Print summary
        print_summary()

    except KeyboardInterrupt:
        print("\n\n[WARN] Test interrupted by user")
        print_summary()
    except Exception as e:
        print(f"\n\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()

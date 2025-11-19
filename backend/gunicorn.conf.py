# Gunicorn configuration for DocuMind Voice Production Server
import multiprocessing
import os

# Server socket
bind = "0.0.0.0:8080"
backlog = 2048

# Worker processes
# Recommended: 2-4 x CPU cores for CPU-bound apps
# For I/O-bound apps like this (waiting for LLM/DB), 4 workers is good for small servers
workers = 4
worker_class = 'sync'
worker_connections = 1000
threads = 2  # Allows 8 concurrent requests (4 workers × 2 threads)
timeout = 120  # 2 minutes for long PDF processing and LLM responses
keepalive = 5

# Restart workers after N requests (prevent memory leaks)
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = '-'  # stdout
errorlog = '-'   # stderr
loglevel = 'info'
capture_output = True
enable_stdio_inheritance = True

# Process naming
proc_name = 'documind_voice'

# Server mechanics
daemon = False  # Run in foreground (required for most hosting platforms)
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Development vs Production
# Set FLASK_ENV=production in .env for production mode
raw_env = [
    f"FLASK_ENV={os.getenv('FLASK_ENV', 'development')}",
]

# Preload app for better memory efficiency
preload_app = True

# Worker lifecycle hooks
def on_starting(server):
    """Called just before the master process is initialized."""
    server.log.info("Gunicorn master starting")

def on_reload(server):
    """Called to recycle workers during reload."""
    server.log.info("Reloading Gunicorn workers")

def when_ready(server):
    """Called just after the server is started."""
    server.log.info(f"Gunicorn server ready. Workers: {workers}, Threads: {threads}")
    server.log.info(f"Max concurrent requests: {workers * threads}")

def worker_int(worker):
    """Called when a worker receives the INT or QUIT signal."""
    worker.log.info("Worker received INT or QUIT signal")

def worker_abort(worker):
    """Called when a worker receives the ABRT signal."""
    worker.log.warning("Worker received ABRT signal")

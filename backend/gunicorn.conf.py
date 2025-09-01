# Gunicorn configuration file
import multiprocessing

# timeout
timeout = 120
graceful_timeout = 120

# requests limits
max_requests = 1000
max_requests_jitter = 50

log_file = "-"

# binding
bind = "0.0.0.0:8000"

# worker nodes
worker_class = "uvicorn.workers.UvicornWorker"
workers = max(1, multiprocessing.cpu_count() // 2)

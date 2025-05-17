import multiprocessing
import os

# Server socket settings
bind = '127.0.0.1:8000'

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
threads = 4

# Timeout settings
timeout = 120  # Increase timeout to 120 seconds
graceful_timeout = 60
keepalive = 5

# Logging
accesslog = '/tmp/gunicorn_access.log'
errorlog = '/tmp/gunicorn_error.log'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = 'rep_app_gunicorn'

# Django WSGI application path
wsgi_app = 'main_conf.wsgi:application'

# SSL is handled by Nginx, so we don't need SSL settings here
# Security settings
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Development settings
reload = True  # Auto-reload on code changes
capture_output = True
enable_stdio_inheritance = True
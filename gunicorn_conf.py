# -*- coding: utf-8 -*-
from multiprocessing import cpu_count


##### Gunicorn configs#####
# Server Socket
# bind = "0.0.0.0:{}".format(port)
bind = "unix:/var/run/gunicorn-store.sock"  # Este tipo de sockets es más rápido que
# utilizando la interfaz local. Por lo que si el Nginx y el Gunicorn están en
# el mismo servidor es el que les recomiendo.
backlog = 2048

# Worker Processes
workers = cpu_count() * 2 + 1  # Valor recomendado por la doc oficial: http://docs.gunicorn.org/en/stable/design.html#how-many-workers
worker_class = 'gevent'  # Le decimos que utilice gevent para un mejor rendimiento.
worker_connections = 1000
max_requests = 0  # Unlimited requests
keepalive = 5
timeout = 30  # Workers silent for more than this many seconds are killed and restarted.
graceful_timeout = 40  # Timeout for graceful workers restart.


# Security
limit_request_line = 4096
limit_request_fields = 100
# limit_request_fields = 8190

# Server Mechanics
pidfile = '/var/run/gunicorn/gunicorn-store.pid'
user = 'user1'
group = 'user1'

# Logging
loglevel = 'error'
accesslog = '/var/log/gunicorn/stores_api_webapp.access.log'
errorlog = '/var/log/gunicorn/stores_api_webapp.error.log'

# Process Naming
proc_name = 'stores_api_webapp'

###### End Gunicorn settings#####
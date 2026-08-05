bind = "0.0.0.0:5008"
# VM: 2 vCPU / 2 GB. SQLite poorly tolerates many writers across processes —
# prefer few processes + threads over (2×CPU)+1 sync workers.
workers = 2
threads = 4
worker_class = "gthread"
accesslog = "-"
errorlog = "-"
capture_output = True

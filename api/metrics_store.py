from collections import defaultdict
import threading

metrics = {
    "total_requests": 0,
    "total_time": 0.0,
    "per_path": defaultdict(lambda: {"count": 0, "total_time": 0.0})
}
metrics_lock = threading.Lock()
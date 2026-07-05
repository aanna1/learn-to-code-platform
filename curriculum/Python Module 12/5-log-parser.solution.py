import re

LOG_PATTERN = re.compile(r"ip=([\d.]+).*?status=(\d+)")

def count_rejected_ips(log_text):
    """
    Parse log_text and return a dict mapping each IP address to the number of
    times it appeared in a line with a 4xx status code.
    """
    counts = {}
    for ip, status in LOG_PATTERN.findall(log_text):
        if status.startswith("4"):
            counts[ip] = counts.get(ip, 0) + 1
    return counts


if __name__ == "__main__":
    log = """
2026-03-14 09:14:22 INFO  user=alice ip=10.0.0.5 path=/login status=200
2026-03-14 09:14:23 ERROR user=bob   ip=10.0.0.9 path=/admin status=403
2026-03-14 09:14:25 ERROR user=carol ip=10.0.0.9 path=/admin status=403
2026-03-14 09:14:30 INFO  user=alice ip=10.0.0.5 path=/home  status=200
2026-03-14 09:14:35 ERROR user=dave  ip=10.0.0.7 path=/login status=401
"""
    print(count_rejected_ips(log))
    # Expected: {'10.0.0.9': 2, '10.0.0.7': 1}

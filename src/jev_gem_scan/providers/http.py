"""HTTP helpers for public market-data providers."""
import json
import time
import urllib.error
import urllib.request

UA = "jev-gem-scan/2.0"


def get_json(url, timeout=12, retries=2):
    last = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, ValueError) as exc:
            last = exc
            if attempt < retries:
                time.sleep(0.5 * (attempt + 1))
    raise RuntimeError("provider request failed: %s" % last)

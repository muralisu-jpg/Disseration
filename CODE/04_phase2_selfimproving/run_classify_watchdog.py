"""Watchdog for the cache-filling grind. Runs classify.py unchanged; watches
classifier/llm_cache.json; if the cache stops growing for STALL_MINUTES while the
process is still running, kills it and exits loudly - so silent quota death can't
burn a window unnoticed. Run from the kit root:

    python run_classify_watchdog.py
"""
import json, subprocess, sys, time
from pathlib import Path

CACHE = Path("classifier/llm_cache.json")
STALL_MINUTES = 6          # no cache growth for this long while alive => quota dead
CHECK_EVERY = 30           # seconds between checks

def cache_size():
    try:
        return len(json.loads(CACHE.read_text(encoding="utf-8")))
    except Exception:
        return 0

def main():
    start = cache_size()
    print(f"[watchdog] starting classify.py (cache: {start} pairs)")
    proc = subprocess.Popen([sys.executable, "classifier/classify.py"])
    last_size, last_growth = start, time.time()
    while True:
        time.sleep(CHECK_EVERY)
        if proc.poll() is not None:
            final = cache_size()
            print(f"[watchdog] classify.py exited (code {proc.returncode}); cache: {final} pairs (+{final - start} this run)")
            sys.exit(proc.returncode or 0)
        size = cache_size()
        if size > last_size:
            print(f"[watchdog] cache: {size} pairs (+{size - last_size})")
            last_size, last_growth = size, time.time()
        elif time.time() - last_growth > STALL_MINUTES * 60:
            proc.terminate()
            print(f"[watchdog] QUOTA APPEARS DEAD - no cache growth for {STALL_MINUTES} min. "
                  f"Killed classify.py. Cache safe at {size} pairs (+{size - start} this run). "
                  f"Resume with this same command after the quota reset.")
            sys.exit(2)

if __name__ == "__main__":
    main()

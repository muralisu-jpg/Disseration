"""Shared LLM caller — Opus 4.8 via claude -p (shell=True, Windows). Cached per stage."""
import subprocess, json, os
CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "cache")
def _cache_path(stage): return os.path.join(CACHE_DIR, f"{stage}_cache.json")
def load_cache(stage):
    try: return json.loads(open(_cache_path(stage),encoding="utf-8").read())
    except: return {}
def save_cache(stage,c): open(_cache_path(stage),"w",encoding="utf-8").write(json.dumps(c))
def call(prompt,timeout=180):
    try:
        return subprocess.run('claude -p --model claude-opus-4-8',shell=True,input=prompt,
                              capture_output=True,text=True,timeout=timeout).stdout.strip()
    except Exception:
        return ""

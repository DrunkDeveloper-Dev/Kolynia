#!/usr/bin/env python3
"""
Run the mock facilitator forever (auto-restart on crash) and optionally open the URL once.

Usage (Windows cmd):
    python scripts\run_facilitator_forever.py

This script will:
- Start uvicorn serving `scripts.mock_facilitator:app` on 127.0.0.1:8000 (configurable via env)
- Log stdout/stderr to `scripts/facilitator.log`
- Restart the process if it exits unexpectedly
- Open the default browser to the facilitator /list endpoint once when ready

To run persistently across reboots, run this script inside a dedicated terminal or create a Windows Scheduled Task or service.
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
import webbrowser
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
LOG_FILE = SCRIPTS / "facilitator.log"
PID_FILE = SCRIPTS / "facilitator.pid"

UVICORN_TARGET = os.environ.get("UVICORN_TARGET", "scripts.mock_facilitator:app")
HOST = os.environ.get("MOCK_HOST", "127.0.0.1")
PORT = int(os.environ.get("MOCK_PORT", "8000"))
OPEN_BROWSER = os.environ.get("OPEN_FACILITATOR_BROWSER", "1") in ("1", "true", "True")

CHECK_URL = f"http://{HOST}:{PORT}/list"

RESTART_DELAY = 2.0


def start_uvicorn_log() -> subprocess.Popen:
    cmd = [sys.executable, "-m", "uvicorn", UVICORN_TARGET, "--host", HOST, "--port", str(PORT), "--log-level", "info"]
    # Ensure scripts dir exists
    SCRIPTS.mkdir(parents=True, exist_ok=True)
    logfile = open(LOG_FILE, "a", buffering=1, encoding="utf-8")
    # write header
    logfile.write(f"\n--- Starting uvicorn: {UVICORN_TARGET} host={HOST} port={PORT} at {time.ctime()} ---\n")
    proc = subprocess.Popen(cmd, stdout=logfile, stderr=subprocess.STDOUT)
    # write pid
    try:
        PID_FILE.write_text(str(proc.pid))
    except Exception:
        pass
    return proc


def wait_for_ready(timeout: float = 10.0) -> bool:
    import httpx

    start = time.time()
    while time.time() - start < timeout:
        try:
            r = httpx.get(CHECK_URL, timeout=2.0)
            if r.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(0.5)
    return False


def open_browser_once(url: str):
    try:
        webbrowser.open(url, new=2)
    except Exception:
        pass


def main():
    print(f"Starting facilitator launcher for {UVICORN_TARGET} on {HOST}:{PORT}")
    first_time = True
    proc: Optional[subprocess.Popen] = None
    try:
        while True:
            proc = start_uvicorn_log()
            ready = wait_for_ready(timeout=10.0)
            if ready:
                print(f"Facilitator is ready at {CHECK_URL}")
                if OPEN_BROWSER and first_time:
                    open_browser_once(CHECK_URL)
                    first_time = False
            else:
                print("Facilitator did not report ready within timeout; check logs.")
            # Wait for process to exit
            try:
                proc.wait()
                exit_code = proc.returncode
                print(f"Facilitator process exited with code {exit_code}; restarting in {RESTART_DELAY}s...")
            except KeyboardInterrupt:
                print("Received KeyboardInterrupt, terminating facilitator process...")
                try:
                    proc.terminate()
                except Exception:
                    pass
                break
            except Exception as e:
                print(f"Error waiting for process: {e}")
            time.sleep(RESTART_DELAY)
    finally:
        # cleanup
        try:
            if proc and proc.poll() is None:
                proc.terminate()
                time.sleep(0.2)
                if proc.poll() is None:
                    proc.kill()
        except Exception:
            pass
        try:
            if PID_FILE.exists():
                PID_FILE.unlink()
        except Exception:
            pass
        print("Facilitator launcher exiting.")


if __name__ == '__main__':
    main()


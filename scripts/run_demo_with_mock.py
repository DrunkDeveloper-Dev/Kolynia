#!/usr/bin/env python3
import subprocess
import sys
import os
import time
import signal
import json
import re
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
LOG_PATH = ROOT / "scripts" / "demo_result.log"
LAST_TX_PATH = ROOT / "scripts" / "last_x402_tx.json"
MOCK_HOST = "127.0.0.1"
MOCK_PORT = 8000
MOCK_URL = f"http://{MOCK_HOST}:{MOCK_PORT}"

UVICORN_TARGET = "scripts.mock_facilitator:app"

# Dummy private key for demo; replace with secure test key if desired
DUMMY_PRIVATE_KEY = os.environ.get("X402_PRIVATE_KEY", "0x0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef")


def start_mock():
    cmd = [sys.executable, "-m", "uvicorn", UVICORN_TARGET, "--host", MOCK_HOST, "--port", str(MOCK_PORT), "--log-level", "warning"]
    # Start uvicorn as subprocess
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return proc


def wait_for_mock(timeout=10):
    start = time.time()
    url = f"{MOCK_URL}/list"
    while time.time() - start < timeout:
        try:
            r = httpx.get(url, timeout=2.0)
            if r.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(0.5)
    return False


def run_demo(env=None, timeout=30):
    cmd = [sys.executable, str(ROOT / "examples" / "x402_integration_demo.py")]
    env_copy = os.environ.copy()
    if env:
        env_copy.update(env)
    p = subprocess.run(cmd, capture_output=True, text=True, env=env_copy, timeout=timeout)
    return p


def extract_json_objects(text):
    objs = []
    # Find JSON objects by searching for balanced braces
    brace_stack = []
    start_idx = None
    for i, ch in enumerate(text):
        if ch == '{':
            if not brace_stack:
                start_idx = i
            brace_stack.append('{')
        elif ch == '}':
            if brace_stack:
                brace_stack.pop()
                if not brace_stack and start_idx is not None:
                    candidate = text[start_idx:i+1]
                    try:
                        obj = json.loads(candidate)
                        objs.append(obj)
                    except Exception:
                        # ignore non-json
                        pass
                    start_idx = None
    return objs


def main():
    print("Starting mock facilitator and demo runner...")
    proc = start_mock()
    try:
        print("Waiting for mock to be ready...", end=" ")
        ready = wait_for_mock(timeout=10)
        print("OK" if ready else "TIMEOUT")
        if not ready:
            print("Mock facilitator did not start in time. Check logs.")
            # capture some stderr
            try:
                out, err = proc.communicate(timeout=1)
                print("uvicorn stderr:\n", err.decode(errors='ignore'))
            except Exception:
                pass
            proc.kill()
            sys.exit(1)

        env = {
            "FACILITATOR_URL": MOCK_URL,
            "X402_PRIVATE_KEY": DUMMY_PRIVATE_KEY,
        }
        print("Running demo script...")
        res = run_demo(env=env, timeout=60)

        LOG_PATH.write_text(res.stdout + '\n' + res.stderr)
        print(f"Demo stdout/stderr written to {LOG_PATH}")

        # extract JSON objects from stdout
        json_objs = extract_json_objects(res.stdout)
        if json_objs:
            LAST_TX_PATH.write_text(json.dumps(json_objs, indent=2))
            print(f"Extracted {len(json_objs)} JSON object(s) and saved to {LAST_TX_PATH}")
        else:
            print("No JSON objects extracted from demo output.")

        # return exit code
        if res.returncode != 0:
            print(f"Demo exited with code {res.returncode}")
            sys.exit(res.returncode)

    finally:
        # Terminate uvicorn process
        try:
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except Exception:
                proc.kill()
        except Exception:
            pass


if __name__ == '__main__':
    main()


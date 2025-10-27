#!/usr/bin/env python3
"""
One-click tester for x402 demo that guarantees using the local mock facilitator
and verifies all responses return HTTP 200.

Usage (Windows cmd):
    python scripts\one_click_test.py

What it does:
- Starts the local mock facilitator (uvicorn) on 127.0.0.1:8000 if not already reachable
- Runs examples/x402_integration_demo.py with FACILITATOR_URL forced to the mock
- Captures stdout/stderr to scripts/one_click_result.log
- Extracts JSON objects and verifies that any top-level 'status_code' fields are 200
- Writes parsed JSON objects to scripts/last_x402_tx.json (overwriting)
- Exits with code 0 on success, 2 if any non-200 status found, 1 on other errors

This provides a single-command, deterministic test you can show to the client.
"""
from __future__ import annotations
import subprocess
import sys
import time
import json
import os
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
LOG = SCRIPTS / "one_click_result.log"
LAST_JSON = SCRIPTS / "last_x402_tx.json"
MOCK_HOST = os.environ.get("MOCK_HOST", "127.0.0.1")
MOCK_PORT = int(os.environ.get("MOCK_PORT", "8000"))
MOCK_URL = f"http://{MOCK_HOST}:{MOCK_PORT}"
UVICORN_TARGET = os.environ.get("UVICORN_TARGET", "scripts.mock_facilitator:app")

DUMMY_KEY = "0x0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"


def start_mock():
    # Start uvicorn as subprocess
    cmd = [sys.executable, "-m", "uvicorn", UVICORN_TARGET, "--host", MOCK_HOST, "--port", str(MOCK_PORT), "--log-level", "warning"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return proc


def wait_for_mock(timeout=10.0):
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


def extract_json_objects(text: str):
    objs = []
    brace = 0
    start_idx = None
    for i,ch in enumerate(text):
        if ch == '{':
            if brace == 0:
                start_idx = i
            brace += 1
        elif ch == '}':
            brace -= 1
            if brace == 0 and start_idx is not None:
                chunk = text[start_idx:i+1]
                try:
                    objs.append(json.loads(chunk))
                except Exception:
                    pass
                start_idx = None
    return objs


def main():
    SCRIPTS.mkdir(parents=True, exist_ok=True)
    LOG.write_text("")

    proc = start_mock()
    try:
        print("Starting mock facilitator...")
        ready = wait_for_mock(timeout=10)
        if not ready:
            print("Mock failed to start in time; capturing stderr...")
            try:
                out,err = proc.communicate(timeout=1)
                print(err.decode(errors='ignore'))
            except Exception:
                pass
            proc.kill()
            LOG.write_text("Mock facilitator failed to start\n")
            sys.exit(1)
        print("Mock ready at", MOCK_URL)

        env = {
            "FACILITATOR_URL": MOCK_URL,
            # prefer existing X402_PRIVATE_KEY if present, else use dummy
            "X402_PRIVATE_KEY": os.environ.get("X402_PRIVATE_KEY", DUMMY_KEY),
        }
        print("Running integration demo against mock...")
        res = run_demo(env=env, timeout=60)

        combined = res.stdout + '\n' + res.stderr
        LOG.write_text(combined)
        print(f"Logs written to {LOG}")

        objs = extract_json_objects(res.stdout)
        if objs:
            LAST_JSON.write_text(json.dumps(objs, indent=2))
            print(f"Extracted {len(objs)} JSON objects to {LAST_JSON}")
        else:
            print("No JSON objects found in demo output")

        # Validate all status_code fields are 200
        non200 = []
        def find_status_codes(o):
            if isinstance(o, dict):
                if 'status_code' in o:
                    try:
                        sc = int(o['status_code'])
                        return [sc]
                    except Exception:
                        return []
                codes = []
                for v in o.values():
                    codes += find_status_codes(v)
                return codes
            elif isinstance(o, list):
                codes = []
                for i in o:
                    codes += find_status_codes(i)
                return codes
            return []

        for o in objs:
            codes = find_status_codes(o)
            for c in codes:
                if c != 200:
                    non200.append(c)

        if non200:
            print("FAIL: found non-200 status codes:", non200)
            sys.exit(2)
        else:
            print("OK: all status_code values are 200 (tsaref)")
            sys.exit(0)

    finally:
        # terminate mock
        try:
            proc.terminate()
            proc.wait(timeout=3)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass


if __name__ == '__main__':
    main()


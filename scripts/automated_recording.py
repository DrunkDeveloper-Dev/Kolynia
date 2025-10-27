#!/usr/bin/env python3
"""
Automated runner + optional screen recorder for the x402 demo.

What it does:
- Starts the mock facilitator (uvicorn) on localhost and waits for it to be ready
- Optionally starts an ffmpeg screen recorder (if `--record` is passed and ffmpeg is in PATH)
- Runs `examples/x402_integration_demo.py` with FACILITATOR_URL pointing to the mock
- Captures stdout/stderr to `scripts/demo_recording.log`
- Extracts JSON objects from stdout and writes them to `scripts/last_x402_tx.json`

Usage (Windows cmd):
    python scripts\automated_recording.py
    python scripts\automated_recording.py --record  # if you have ffmpeg and want a video

Notes:
- ffmpeg recording is optional and best-effort (uses gdigrab on Windows). Adjust ffmpeg args as needed.
- This script is intentionally short and defensive; it mirrors the existing `run_demo_with_mock.py` behavior.
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
LOG_PATH = SCRIPTS_DIR / "demo_recording.log"
LAST_TX_PATH = SCRIPTS_DIR / "last_x402_tx.json"
MOCK_HOST = os.environ.get("MOCK_HOST", "127.0.0.1")
MOCK_PORT = int(os.environ.get("MOCK_PORT", "8000"))
MOCK_URL = f"http://{MOCK_HOST}:{MOCK_PORT}"
UVICORN_TARGET = "scripts.mock_facilitator:app"

DUMMY_PRIVATE_KEY = os.environ.get("X402_PRIVATE_KEY", "0x0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef")


def start_mock():
    cmd = [sys.executable, "-m", "uvicorn", UVICORN_TARGET, "--host", MOCK_HOST, "--port", str(MOCK_PORT), "--log-level", "warning"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return proc


def wait_for_mock(timeout=10.0):
    import httpx
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


def run_demo(env=None, timeout=60):
    cmd = [sys.executable, str(ROOT / "examples" / "x402_integration_demo.py")]
    env_copy = os.environ.copy()
    if env:
        env_copy.update(env)
    p = subprocess.run(cmd, capture_output=True, text=True, env=env_copy, timeout=timeout)
    return p


def extract_json_objects(text):
    objs = []
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
                        pass
                    start_idx = None
    return objs


def start_ffmpeg_recording(output_path: Path, fps: int = 15, video_size: str | None = None):
    """Attempt to start an ffmpeg recording using gdigrab (Windows). Returns Popen or None."""
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        print("ffmpeg not found in PATH; skipping recording")
        return None
    # base command for Windows desktop capture using gdigrab
    cmd = [ffmpeg, "-y", "-f", "gdigrab", "-framerate", str(fps), "-i", "desktop"]
    if video_size:
        cmd.extend(["-video_size", video_size])
    cmd.extend([str(output_path)])
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return proc
    except Exception as e:
        print("Failed to start ffmpeg:", e)
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--record", action="store_true", help="Try to record the screen with ffmpeg (if available)")
    parser.add_argument("--timeout", type=int, default=60, help="Demo run timeout seconds")
    args = parser.parse_args()

    print("Starting mock facilitator and demo runner...")
    proc = start_mock()
    try:
        print("Waiting for mock to be ready...", end=" ")
        ready = wait_for_mock(timeout=10)
        print("OK" if ready else "TIMEOUT")
        if not ready:
            print("Mock facilitator did not start in time. Reading uvicorn stderr for debugging...")
            try:
                out, err = proc.communicate(timeout=1)
                print(err.decode(errors='ignore'))
            except Exception:
                pass
            proc.kill()
            sys.exit(1)

        ffmpeg_proc = None
        if args.record:
            video_out = SCRIPTS_DIR / f"demo_recording_{int(time.time())}.mp4"
            print("Starting ffmpeg recording to", video_out)
            ffmpeg_proc = start_ffmpeg_recording(video_out)
            if ffmpeg_proc:
                print("Recording started (ffmpeg pid:", ffmpeg_proc.pid, ")")
            else:
                print("Recording not started")

        env = {
            "FACILITATOR_URL": MOCK_URL,
            "X402_PRIVATE_KEY": DUMMY_PRIVATE_KEY,
        }
        print("Running demo script...")
        res = run_demo(env=env, timeout=args.timeout)

        LOG_PATH.write_text(res.stdout + '\n' + res.stderr)
        print(f"Logs written to {LOG_PATH}")

        json_objs = extract_json_objects(res.stdout)
        if json_objs:
            LAST_TX_PATH.write_text(json.dumps(json_objs, indent=2))
            print(f"Extracted {len(json_objs)} JSON object(s) and saved to {LAST_TX_PATH}")
        else:
            print("No JSON objects extracted from demo output.")

        if res.returncode != 0:
            print(f"Demo exited with code {res.returncode}")
            # fall through to cleanup, then exit with code

    finally:
        # stop recording
        try:
            if 'ffmpeg_proc' in locals() and ffmpeg_proc:
                print("Stopping ffmpeg recording...")
                try:
                    ffmpeg_proc.terminate()
                    ffmpeg_proc.wait(timeout=3)
                except Exception:
                    ffmpeg_proc.kill()
        except Exception:
            pass
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


#!/usr/bin/env python3
"""
PayAI facilitator probe script

This script tries to discover what payload shapes the facilitator accepts.
It will:
 - GET /list
 - Try POST /create_payment and /verify with several payload shapes
 - Save results to scripts/payai_probe_results.json and print diagnostics

Usage (Windows cmd):
  set FACILITATOR_URL=https://facilitator.payai.network
  python scripts\payai_probe.py

Options:
  --only-list   : only call /list and exit
  --no-create   : skip create_payment tests
  --no-verify   : skip verify tests

Notes:
 - The script makes no on-chain transfers; it only POSTs intent-like payloads to the facilitator for schema discovery.
 - If you get DNS/connection errors (getaddrinfo), check your network, proxy, or firewall. Run the script where you have internet access.
"""
from __future__ import annotations
import json
import os
import sys
import argparse
from pathlib import Path
import httpx
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "scripts" / "payai_probe_results.json"

DEFAULT_URL = os.getenv("FACILITATOR_URL", "https://facilitator.payai.network")

PAYLOAD_VARIANTS = []

# Variant 1: simple numeric amount (legacy/simple)
PAYLOAD_VARIANTS.append({
    "name": "simple_number",
    "body": {"amount": 0.01, "currency": "USD"},
})

# Variant 2: amount as string
PAYLOAD_VARIANTS.append({
    "name": "amount_string",
    "body": {"amount": "0.01", "currency": "USD"},
})

# Variant 3: with metadata and from_address (derived from env if available)
from_addr = os.getenv("X402_PRIVATE_KEY")
if from_addr and len(from_addr) > 10:
    # we can't derive address without eth_account; allow user to supply X402_FROM_ADDR or use placeholder
    pass
PAYLOAD_VARIANTS.append({
    "name": "with_metadata_and_from",
    "body": {"amount": 0.01, "currency": "USD", "metadata": {"memo": "probe"}, "from_address": os.getenv("X402_FROM_ADDRESS") or None},
})

# Variant 4: token amount object (like TokenAmount/TokenAsset used in reference docs)
PAYLOAD_VARIANTS.append({
    "name": "token_amount_object",
    "body": {
        "amount": {
            "amount": "10000",
            "asset": {
                "address": os.getenv("PAYAI_TEST_TOKEN_ADDRESS", "0x036CbD53842c5426634e7929541eC2318f3dCF7e"),
                "decimals": 6,
                "eip712": {"name": "USDC", "version": "2"},
            },
        }
    },
})

# Variant 5: eip712 signed object - we only send structured data placeholders (not a real signature)
PAYLOAD_VARIANTS.append({
    "name": "eip712_placeholder",
    "body": {
        "eip712": {"domain": {"name": "x402"}, "message": {"amount": "0.01", "currency": "USD"}},
        "signature": None,
    },
})


def try_get(client: httpx.Client, url: str) -> Dict[str, Any]:
    try:
        r = client.get(url, timeout=10)
        try:
            return {"status_code": r.status_code, "body": r.json(), "headers": dict(r.headers)}
        except Exception:
            return {"status_code": r.status_code, "text": r.text, "headers": dict(r.headers)}
    except Exception as e:
        return {"status_code": 0, "error": str(e)}


def try_post(client: httpx.Client, url: str, body: Dict[str, Any]) -> Dict[str, Any]:
    try:
        r = client.post(url, json=body, timeout=15)
        try:
            return {"status_code": r.status_code, "body": r.json(), "text": r.text, "headers": dict(r.headers)}
        except Exception:
            return {"status_code": r.status_code, "text": r.text, "headers": dict(r.headers)}
    except Exception as e:
        return {"status_code": 0, "error": str(e)}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--facilitator", default=DEFAULT_URL)
    p.add_argument("--only-list", action="store_true")
    p.add_argument("--no-create", action="store_true")
    p.add_argument("--no-verify", action="store_true")
    args = p.parse_args()

    url = args.facilitator.rstrip("/")
    print("Probing facilitator:", url)

    client = httpx.Client()
    results: Dict[str, Any] = {"facilitator": url}

    # list
    print("Calling /list...")
    results["list"] = try_get(client, f"{url}/list")
    print(json.dumps(results["list"], indent=2))
    if args.only_list:
        OUT.write_text(json.dumps(results, indent=2))
        print("Wrote results to", OUT)
        return

    # iterate variants
    results["create_tests"] = []
    if not args.no_create:
        for v in PAYLOAD_VARIANTS:
            body = v["body"].copy()
            # do not include None values
            body = {k: v for k, v in body.items() if v is not None}
            print(f"POST /create_payment variant {v['name']} -> body: {body}")
            r = try_post(client, f"{url}/create_payment", body)
            r["variant"] = v["name"]
            results["create_tests"].append(r)
            print(json.dumps(r, indent=2))

    results["verify_tests"] = []
    if not args.no_verify:
        for v in PAYLOAD_VARIANTS:
            body = v["body"].copy()
            body = {k: v for k, v in body.items() if v is not None}
            print(f"POST /verify variant {v['name']} -> body: {body}")
            r = try_post(client, f"{url}/verify", body)
            r["variant"] = v["name"]
            results["verify_tests"].append(r)
            print(json.dumps(r, indent=2))

    OUT.write_text(json.dumps(results, indent=2))
    print("Wrote results to", OUT)


if __name__ == '__main__':
    main()


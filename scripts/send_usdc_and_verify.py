#!/usr/bin/env python3
"""
Send a small ERC-20 token transfer (e.g. test USDC) and verify balances before/after.

Usage (Windows cmd):
  set RPC_URL=https://your-testnet-rpc
  set PRIVATE_KEY=0x<your_test_wallet_private_key>   # local only, never share
  set USDC_CONTRACT=0x...                             # test USDC contract on chosen network
  set RECEIVER=0x...                                  # merchant or recipient
  python scripts\send_usdc_and_verify.py --amount 0.01

Flags:
  --rpc RPC_URL       : override RPC_URL env variable
  --private-key KEY   : override PRIVATE_KEY env variable (not recommended)
  --token TOKEN       : ERC20 contract address (env USDC_CONTRACT)
  --to RECEIVER       : recipient address (env RECEIVER or ADDRESS)
  --amount AMOUNT     : human amount, in token units (e.g. 0.01 for 0.01 USDC)
  --wait              : wait for tx confirmation (default True)

Notes:
- This script uses web3.py and eth-account. Install with:
    python -m pip install web3 eth-account
- Always use a testnet and a test wallet with small funds.
- The script will print balances before and after and the tx hash/receipt.
"""
from __future__ import annotations
import argparse
import os
import sys
from decimal import Decimal
from typing import Optional


def parse_args():
    p = argparse.ArgumentParser(description="Send ERC20 token and verify balances")
    p.add_argument("--rpc", help="RPC URL (or set RPC_URL env)")
    p.add_argument("--private-key", help="Private key hex (or set PRIVATE_KEY or X402_PRIVATE_KEY env)")
    p.add_argument("--token", help="ERC20 token contract address (or set USDC_CONTRACT env)")
    p.add_argument("--to", help="Recipient address (or set RECEIVER or ADDRESS env)")
    p.add_argument("--amount", type=str, required=True, help="Amount in token units (human, e.g. 0.01)")
    p.add_argument("--wait", action="store_true", help="Wait for tx confirmation (default: true)")
    return p.parse_args()


def lazy_web3_imports():
    try:
        from web3 import Web3
        from web3.middleware import geth_poa_middleware
    except Exception as e:
        print("Missing dependency: web3. Install with: python -m pip install web3")
        raise
    try:
        from eth_account import Account
    except Exception:
        print("Missing dependency: eth-account. Install with: python -m pip install eth-account")
        raise
    return Web3, geth_poa_middleware, Account


ERC20_ABI = [
    {"constant": True, "inputs": [{"name": "_owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "symbol", "outputs": [{"name": "", "type": "string"}], "type": "function"},
    {"constant": False, "inputs": [{"name": "_to", "type": "address"}, {"name": "_value", "type": "uint256"}], "name": "transfer", "outputs": [{"name": "", "type": "bool"}], "type": "function"},
]


def format_amount(raw: int, decimals: int) -> Decimal:
    return Decimal(raw) / (Decimal(10) ** decimals)


def parse_amount(amount_str: str, decimals: int) -> int:
    d = Decimal(amount_str)
    raw = int(d * (Decimal(10) ** decimals))
    return raw


def main():
    args = parse_args()
    rpc = args.rpc or os.getenv("RPC_URL")
    priv = args.private_key or os.getenv("PRIVATE_KEY") or os.getenv("X402_PRIVATE_KEY")
    token_addr = args.token or os.getenv("USDC_CONTRACT")
    to_addr = args.to or os.getenv("RECEIVER") or os.getenv("ADDRESS")
    amount_str = args.amount
    wait = args.wait or True

    if not rpc:
        print("RPC URL is required (provide --rpc or set RPC_URL env)")
        sys.exit(2)
    if not priv:
        print("Private key is required (set PRIVATE_KEY or X402_PRIVATE_KEY env)")
        sys.exit(2)
    if not token_addr:
        print("Token contract address is required (set USDC_CONTRACT env or use --token)")
        sys.exit(2)
    if not to_addr:
        print("Recipient address is required (set RECEIVER or ADDRESS env or use --to)")
        sys.exit(2)

    Web3, geth_poa_middleware, Account = lazy_web3_imports()
    w3 = Web3(Web3.HTTPProvider(rpc))
    # Some testnets require PoA middleware
    try:
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    except Exception:
        pass

    if not w3.is_connected():
        print(f"Failed to connect to RPC: {rpc}")
        sys.exit(3)

    acct = Account.from_key(priv)
    from_addr = acct.address
    print(f"Using from address: {from_addr}")

    # token contract
    token = w3.eth.contract(address=w3.to_checksum_address(token_addr), abi=ERC20_ABI)
    try:
        decimals = token.functions.decimals().call()
    except Exception:
        decimals = 18
    try:
        symbol = token.functions.symbol().call()
    except Exception:
        symbol = "TOKEN"

    # balances before
    try:
        raw_from_before = token.functions.balanceOf(w3.to_checksum_address(from_addr)).call()
        raw_to_before = token.functions.balanceOf(w3.to_checksum_address(to_addr)).call()
    except Exception as e:
        print(f"Error reading balances: {e}")
        sys.exit(4)

    print(f"Balance before - {from_addr}: {format_amount(raw_from_before, decimals)} {symbol}")
    print(f"Balance before - {to_addr}: {format_amount(raw_to_before, decimals)} {symbol}")

    amount_raw = parse_amount(amount_str, decimals)
    if amount_raw <= 0:
        print("Invalid amount")
        sys.exit(2)

    # build tx
    chain_id = w3.eth.chain_id
    nonce = w3.eth.get_transaction_count(from_addr)
    tx = token.functions.transfer(w3.to_checksum_address(to_addr), amount_raw).build_transaction({
        "chainId": chain_id,
        "nonce": nonce,
        "gas": 200000,
        # gasPrice left for provider to suggest; we'll fetch gasPrice
    })

    try:
        gas_price = w3.eth.gas_price
        tx["gasPrice"] = gas_price
    except Exception:
        pass

    # sign and send
    signed = Account.sign_transaction(tx, priv)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    print(f"Sent transfer tx: {w3.to_hex(tx_hash)}")

    if wait:
        print("Waiting for confirmation...")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        print("Receipt:", receipt)
    else:
        receipt = None

    # balances after
    try:
        raw_from_after = token.functions.balanceOf(w3.to_checksum_address(from_addr)).call()
        raw_to_after = token.functions.balanceOf(w3.to_checksum_address(to_addr)).call()
    except Exception as e:
        print(f"Error reading balances after tx: {e}")
        sys.exit(4)

    print(f"Balance after - {from_addr}: {format_amount(raw_from_after, decimals)} {symbol}")
    print(f"Balance after - {to_addr}: {format_amount(raw_to_after, decimals)} {symbol}")

    deducted = (raw_from_before - raw_from_after)
    received = (raw_to_after - raw_to_before)
    print(f"Deducted (raw units): {deducted}; received (raw units): {received}")
    print(f"Deducted (human): {format_amount(deducted, decimals)} {symbol}; Received: {format_amount(received, decimals)} {symbol}")

    if receipt and receipt.get("status", 0) == 1:
        print("Transfer succeeded")
        sys.exit(0)
    else:
        print("Transfer may have failed or is pending")
        sys.exit(5)


if __name__ == '__main__':
    main()


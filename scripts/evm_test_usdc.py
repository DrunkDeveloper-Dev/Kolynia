#!/usr/bin/env python3
"""
Check native and ERC-20 (USDC) balances and optionally send a tiny ERC-20 transfer.

Design goals:
- Safe defaults: no on-chain transfer unless --send is passed.
- Lazy imports: heavy blockchain libs (web3, eth_account) are imported only when needed so `--help` works without installing them.
- Requires the user to provide an RPC endpoint via --rpc or RPC_URL env var.
- Private key must be provided via env var PRIVATE_KEY or X402_PRIVATE_KEY to sign/send transactions.

Usage examples (Windows cmd):
    set RPC_URL=https://rpc.example.org
    set PRIVATE_KEY=0x...     # from your MetaMask test wallet (KEEP SECRET)
    python scripts\evm_test_usdc.py --rpc %RPC_URL% --address 0xE411270746EEcdC55A016ba667bBB9a828067551 --erc20 0x... --amount 1 --unit token

Dry-run (no send):
    python scripts\evm_test_usdc.py --rpc %RPC_URL% --address 0xE41127... --erc20 0xUSDC_CONTRACT

Only proceed to send with --send flag and a small test amount (and only on testnets).
"""

from __future__ import annotations
import argparse
import os
import sys
from decimal import Decimal
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1]

ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "type": "function",
    },
    {
        "constant": False,
        "inputs": [{"name": "_to", "type": "address"}, {"name": "_value", "type": "uint256"}],
        "name": "transfer",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function",
    },
]


def parse_args():
    p = argparse.ArgumentParser(description="EVM native + ERC20 balance checker and optional sender (safe defaults)")
    p.add_argument("--rpc", help="RPC HTTP(S) URL (or set RPC_URL env variable)")
    p.add_argument("--address", help="Wallet address to inspect (e.g. 0x...)", required=True)
    p.add_argument("--erc20", help="ERC-20 token contract address (optional, e.g. USDC)")
    p.add_argument("--amount", type=str, help="Amount to send (in token units if --unit token, otherwise in native units)")
    p.add_argument("--unit", choices=["token", "wei", "ether"], default="token", help="Unit for --amount when sending")
    p.add_argument("--send", action="store_true", help="If set, perform the on-chain transfer (requires PRIVATE_KEY env var)")
    p.add_argument("--to", help="Recipient address for sending (required with --send)")
    p.add_argument("--gas-price-gwei", type=float, help="Optional gas price override (Gwei)")
    return p.parse_args()


def load_rpc(args) -> str:
    if args.rpc:
        return args.rpc
    env = os.environ.get("RPC_URL")
    if env:
        return env
    print("RPC URL must be provided via --rpc or RPC_URL env var", file=sys.stderr)
    sys.exit(2)


def lazy_import_web3():
    try:
        from web3 import Web3
    except Exception as e:
        print("Missing dependency: web3 is required for RPC calls. Install with:\n    python -m pip install web3")
        raise
    return Web3


def lazy_import_account():
    try:
        from eth_account import Account
    except Exception:
        print("Missing dependency: eth_account is required for signing. Install with:\n    python -m pip install eth-account")
        raise
    return Account


def format_token_amount(amount_raw: int, decimals: int) -> str:
    return str(Decimal(amount_raw) / (Decimal(10) ** decimals))


def parse_token_amount(amount_str: str, decimals: int) -> int:
    # amount_str is decimal like "1.5"
    d = Decimal(amount_str)
    raw = int(d * (Decimal(10) ** decimals))
    return raw


def main():
    args = parse_args()
    rpc = load_rpc(args)
    wallet = args.address
    erc20 = args.erc20

    Web3 = lazy_import_web3()
    w3 = Web3(Web3.HTTPProvider(rpc))

    if not w3.is_connected():
        print(f"Failed to connect to RPC: {rpc}")
        sys.exit(3)

    chain_id = None
    try:
        chain_id = w3.eth.chain_id
    except Exception:
        pass

    print(f"Connected to RPC: {rpc} (chain_id={chain_id})")

    # native balance
    try:
        balance = w3.eth.get_balance(wallet)
        try:
            eth_balance = w3.from_wei(balance, 'ether')
        except Exception:
            eth_balance = Decimal(balance) / Decimal(10**18)
        print(f"Native balance for {wallet}: {eth_balance} (wei: {balance})")
    except Exception as e:
        print(f"Error fetching native balance: {e}")

    # ERC20 balance
    if erc20:
        contract = w3.eth.contract(address=w3.to_checksum_address(erc20), abi=ERC20_ABI)
        try:
            symbol = contract.functions.symbol().call()
        except Exception:
            symbol = "TOKEN"
        try:
            decimals = contract.functions.decimals().call()
        except Exception:
            decimals = 18
        try:
            raw_bal = contract.functions.balanceOf(w3.to_checksum_address(wallet)).call()
            human = format_token_amount(raw_bal, decimals)
            print(f"{symbol} balance for {wallet}: {human} (raw: {raw_bal}, decimals: {decimals})")
        except Exception as e:
            print(f"Error fetching ERC20 balance: {e}")

    # Optional send
    if args.send:
        if not args.to:
            print("--to is required when --send is used", file=sys.stderr)
            sys.exit(2)
        priv = os.environ.get("PRIVATE_KEY") or os.environ.get("X402_PRIVATE_KEY")
        if not priv:
            print("PRIVATE_KEY (or X402_PRIVATE_KEY) env var must be set to sign transactions", file=sys.stderr)
            sys.exit(2)
        Account = lazy_import_account()
        acct = Account.from_key(priv)
        from_addr = acct.address
        if w3.to_checksum_address(from_addr) != w3.to_checksum_address(wallet):
            print("Warning: provided PRIVATE_KEY does not match --address. Using address from private key:", from_addr)

        # decide send type: if erc20 provided send ERC20, otherwise send native
        if erc20:
            # send ERC20 transfer(token)
            contract = w3.eth.contract(address=w3.to_checksum_address(erc20), abi=ERC20_ABI)
            try:
                decimals = contract.functions.decimals().call()
            except Exception:
                decimals = 18
            if not args.amount:
                print("--amount is required to send tokens", file=sys.stderr)
                sys.exit(2)
            try:
                amount_raw = parse_token_amount(args.amount, decimals)
            except Exception as e:
                print("Invalid amount format:", e, file=sys.stderr)
                sys.exit(2)
            to_addr = w3.to_checksum_address(args.to)
            nonce = w3.eth.get_transaction_count(from_addr)
            tx = contract.functions.transfer(to_addr, amount_raw).build_transaction({
                "chainId": chain_id,
                "gas": 150000,
                "nonce": nonce,
            })
            if args.gas_price_gwei:
                tx["gasPrice"] = w3.to_wei(args.gas_price_gwei, 'gwei')
            signed = Account.sign_transaction(tx, priv)
            tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
            print(f"Sent ERC20 transfer tx: {w3.to_hex(tx_hash)}")
            print("Wait for confirmation on explorer or via w3.eth.wait_for_transaction_receipt")
        else:
            # send native
            if not args.amount:
                print("--amount is required to send native tokens", file=sys.stderr)
                sys.exit(2)
            try:
                if args.unit == 'wei':
                    value = int(args.amount)
                elif args.unit == 'ether':
                    value = w3.to_wei(Decimal(args.amount), 'ether')
                else:
                    # token unit without erc20 doesn't make sense
                    value = w3.to_wei(Decimal(args.amount), 'ether')
            except Exception as e:
                print("Invalid amount:", e, file=sys.stderr)
                sys.exit(2)
            to_addr = w3.to_checksum_address(args.to)
            nonce = w3.eth.get_transaction_count(from_addr)
            tx = {
                'to': to_addr,
                'value': int(value),
                'gas': 21000,
                'nonce': nonce,
                'chainId': chain_id,
            }
            if args.gas_price_gwei:
                tx['gasPrice'] = w3.to_wei(args.gas_price_gwei, 'gwei')
            signed = Account.sign_transaction(tx, priv)
            tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
            print(f"Sent native transfer tx: {w3.to_hex(tx_hash)}")


if __name__ == '__main__':
    main()


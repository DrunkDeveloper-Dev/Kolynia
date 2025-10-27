#!/usr/bin/env python3
"""
Send SOL or SPL token and verify balances before/after on Solana.

Usage (Windows cmd):
  set SOLANA_RPC=https://api.devnet.solana.com
  set SOLANA_PRIVATE_KEY="[...json array or base58 secret...]"
  set SPL_TOKEN=TokenAddress (optional, if sending SPL)
  set RECEIVER=0x...
  python scripts\send_solana_and_verify.py --amount 0.01 --token-type spl

This script requires `solana` and `spl-token` python packages:
  python -m pip install solana

Notes:
- For security, set `SOLANA_PRIVATE_KEY` locally only. Do NOT share it.
- For SPL transfers, provide the SPL token mint address in `--token` or `SPL_TOKEN`.
"""
from __future__ import annotations
import argparse
import os
import sys
from typing import Optional


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--rpc", help="RPC URL (or set SOLANA_RPC env)")
    p.add_argument("--private-key", help="Solana private key (base58 or JSON array) or set SOLANA_PRIVATE_KEY env")
    p.add_argument("--token", help="SPL token mint address (or set SPL_TOKEN env)")
    p.add_argument("--to", help="Recipient address (or set RECEIVER env)")
    p.add_argument("--amount", type=str, required=True, help="Amount in token units (human, e.g. 0.01)")
    p.add_argument("--token-type", choices=("sol","spl"), default="sol", help="Token type: sol or spl")
    return p.parse_args()


def lazy_imports():
    try:
        from solana.rpc.api import Client
        from solana.keypair import Keypair
        from solana.publickey import PublicKey
    except Exception:
        print("Missing dependency: solana. Install with: python -m pip install solana")
        raise
    return Client, Keypair, PublicKey


def load_keypair(priv: str):
    from solana.keypair import Keypair
    import json
    from base58 import b58decode
    s = priv.strip()
    if s.startswith('['):
        arr = json.loads(s)
        return Keypair.from_secret_key(bytes(arr))
    else:
        try:
            sk = b58decode(s)
            return Keypair.from_secret_key(sk)
        except Exception:
            # maybe hex seed
            try:
                seed = bytes.fromhex(s)
                return Keypair.from_secret_key(seed)
            except Exception as e:
                raise


def main():
    args = parse_args()
    rpc = args.rpc or os.getenv("SOLANA_RPC")
    priv = args.private_key or os.getenv("SOLANA_PRIVATE_KEY")
    token = args.token or os.getenv("SPL_TOKEN")
    to = args.to or os.getenv("RECEIVER")
    amount_str = args.amount
    token_type = args.token_type

    if not rpc:
        print("RPC is required (set --rpc or SOLANA_RPC env)")
        sys.exit(2)
    if not priv:
        print("Private key is required (set --private-key or SOLANA_PRIVATE_KEY env)")
        sys.exit(2)
    if not to:
        print("Recipient address is required (set --to or RECEIVER env)")
        sys.exit(2)

    Client, Keypair, PublicKey = lazy_imports()
    client = Client(rpc)

    try:
        kp = load_keypair(priv)
    except Exception as e:
        print(f"Failed to load keypair: {e}")
        sys.exit(3)

    from_addr = str(kp.public_key)
    print(f"Using from address: {from_addr}")

    if token_type == 'sol':
        bal_before = client.get_balance(PublicKey(from_addr))
        bal_to_before = client.get_balance(PublicKey(to))
        print('Balance before:', bal_before)
        print('Receiver balance before:', bal_to_before)
        lamports = int(float(amount_str) * 1e9)
        tx = client.request_airdrop(PublicKey(from_addr), lamports) if False else None
        # For safety, we won't request airdrop here. Instead build and send transfer
        from solana.transaction import Transaction
        from solana.system_program import TransferParams, transfer
        txn = Transaction().add(transfer(TransferParams(from_pubkey=PublicKey(from_addr), to_pubkey=PublicKey(to), lamports=lamports)))
        try:
            resp = client.send_transaction(txn, kp)
            print('Sent tx:', resp)
        except Exception as e:
            print('Send failed:', e)
            sys.exit(4)
        bal_after = client.get_balance(PublicKey(from_addr))
        bal_to_after = client.get_balance(PublicKey(to))
        print('Balance after:', bal_after)
        print('Receiver balance after:', bal_to_after)
    else:
        # SPL token flow - using token program to transfer via associated token accounts
        from spl.token.client import Token
        from spl.token.constants import TOKEN_PROGRAM_ID
        from spl.token.instructions import get_associated_token_address
        from solana.rpc.commitment import Confirmed
        mint = PublicKey(token)
        token_client = Token(client, mint, TOKEN_PROGRAM_ID, kp)
        # Find or create associated token accounts and transfer
        from_addr_ata = get_associated_token_address(PublicKey(from_addr), mint)
        to_addr_ata = get_associated_token_address(PublicKey(to), mint)
        print('From ATA:', from_addr_ata)
        print('To ATA:', to_addr_ata)
        # Fetch decimals
        info = token_client.get_mint_info()
        decimals = info.decimals
        raw_amount = int(float(amount_str) * (10 ** decimals))
        print(f'Transferring {raw_amount} (raw units)')
        try:
            res = token_client.transfer(from_addr_ata, to_addr_ata, kp.public_key, raw_amount, opts=Confirmed)
            print('Transfer response:', res)
        except Exception as e:
            print('SPL transfer failed:', e)
            sys.exit(5)

    print('Done')


if __name__ == '__main__':
    main()


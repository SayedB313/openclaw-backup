#!/usr/bin/env python3
import json
import os
from coinbase_client import CoinbaseClient

def check_balance():
    secrets_path = "/home/openclaw/.secrets/coinbase.json"
    if not os.path.exists(secrets_path):
        print(f"Error: Secrets file not found at {secrets_path}")
        return

    with open(secrets_path) as f:
        secrets = json.load(f)
    
    client = CoinbaseClient(secrets["api_key"], secrets["api_secret"])
    
    print("Fetching account balances from Coinbase...")
    accounts = client.get_accounts()
    
    if "error" in accounts:
        print(f"Error: {accounts['error']}")
        return

    # Filter for accounts with non-zero balances
    found = False
    for acc in accounts:
        balance = float(acc["available_balance"]["value"])
        if balance > 0:
            print(f"- {acc['currency']}: {balance:.8f} (Hold: {acc['hold']['value']})")
            found = True
    
    if not found:
        print("No accounts with positive balances found.")

if __name__ == "__main__":
    check_balance()

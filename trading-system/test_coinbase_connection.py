#!/usr/bin/env python3
"""Test Coinbase API connectivity."""
import json
from coinbase_client import CoinbaseClient

with open("/home/openclaw/.secrets/coinbase.json") as f:
    secrets = json.load(f)

client = CoinbaseClient(secrets["api_key"], secrets["api_secret"])

print("Testing Coinbase API...")
print(f"Key: {secrets['api_key'][:8]}...")

# Test public endpoint
print("\n1. Testing products list...")
products = client.get_products(limit=5)
print(f"Products found: {len(products)}")
for p in products[:3]:
    print(f"  - {p.get('product_id', 'unknown')}")

# Test specific product
print("\n2. Testing BTC-USD ticker...")
btc = client.analyze_ticker("BTC-USD")
print(f"Result: {btc}")

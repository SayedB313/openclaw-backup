import json
from coinbase_client import CoinbaseClient

with open("/home/openclaw/.secrets/coinbase.json") as f:
    secrets = json.load(f)

client = CoinbaseClient(secrets["api_key"], secrets["api_secret"])

print("Testing BTC-USD:")
result = client.analyze_ticker("BTC-USD")
print(json.dumps(result, indent=2))

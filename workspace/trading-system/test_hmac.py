import hmac
import hashlib
import time
import requests
import json

with open("/home/openclaw/.secrets/coinbase.json") as f:
    secrets = json.load(f)

api_key = secrets["api_key"]
api_secret = secrets["api_secret"]

def test_hmac():
    timestamp = str(int(time.time()))
    method = "GET"
    path = "/api/v3/brokerage/products"
    body = ""
    
    message = timestamp + method + path + body
    signature = hmac.new(api_secret.encode('utf-8'), message.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()
    
    headers = {
        "CB-ACCESS-KEY": api_key,
        "CB-ACCESS-SIGN": signature,
        "CB-ACCESS-TIMESTAMP": timestamp,
        "Content-Type": "application/json"
    }
    
    resp = requests.get(f"https://api.coinbase.com{path}", headers=headers, params={"limit": 1})
    print(f"HMAC Result: {resp.status_code}")
    print(resp.text)

test_hmac()

import jwt
import time
import json

with open("/home/openclaw/.secrets/coinbase.json") as f:
    secrets = json.load(f)

key_name = secrets["api_key"]
key_secret = secrets["api_secret"]

def test_key(secret):
    now = int(time.time())
    payload = {
        "iss": "coinbase-cloud",
        "nbf": now,
        "exp": now + 120,
        "sub": key_name,
    }
    headers = {
        "kid": key_name,
        "nonce": str(now)
    }
    
    # Try different formats
    formats = [
        secret,
        f"-----BEGIN PRIVATE KEY-----\n{secret}\n-----END PRIVATE KEY-----",
        f"-----BEGIN EC PRIVATE KEY-----\n{secret}\n-----END EC PRIVATE KEY-----"
    ]
    
    for fmt in formats:
        try:
            token = jwt.encode(payload, fmt, algorithm="ES256", headers=headers)
            print(f"SUCCESS with format: {fmt[:20]}...")
            return True
        except Exception as e:
            print(f"FAILED with format: {fmt[:20]}... | Error: {e}")
    return False

test_key(key_secret)

import json
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import base64
import jwt
import time

with open("/home/openclaw/.secrets/coinbase.json") as f:
    secrets = json.load(f)

key_name = secrets["api_key"]
key_secret = secrets["api_secret"]

def test_raw_key(secret_b64):
    try:
        # Decode base64
        key_bytes = base64.b64decode(secret_b64)
        print(f"Key length: {len(key_bytes)} bytes")
        
        # If it's 64 or 66 bytes, it might be a raw private key (+ public key)
        # ES256 uses NIST P-256 (32 byte private key)
        
        # Try to wrap it in PEM and load
        pem = f"-----BEGIN PRIVATE KEY-----\n{secret_b64}\n-----END PRIVATE KEY-----"
        
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
        
        token = jwt.encode(payload, pem, algorithm="ES256", headers=headers)
        print("SUCCESS with PEM wrapping")
        return True
    except Exception as e:
        print(f"FAILED: {e}")
        
    return False

test_raw_key(key_secret)

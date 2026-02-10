#!/usr/bin/env python3
import json
import time
import requests
import jwt
import base64
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

with open("/home/openclaw/.secrets/coinbase.json") as f:
    secrets = json.load(f)

key_id = "9523a1c6-2c27-44b2-8d9d-d6a5e9c109aa"
project_id = "9edb9746-e25f-4bc5-b424-e3f85c33702b"
raw_secret = secrets["api_secret"]

# Convert raw secret to PEM
key_bytes = base64.b64decode(raw_secret)
d = int.from_bytes(key_bytes[:32], 'big')
key = ec.derive_private_key(d, ec.SECP256R1(), default_backend())
pem_secret = key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
).decode('utf-8')

def try_key_name(name, use_uri=True):
    print(f"Testing Key Name: {name} (use_uri={use_uri})")
    now = int(time.time())
    path = "/api/v3/brokerage/products"
    
    payload = {
        "iss": "coinbase-cloud",
        "nbf": now,
        "exp": now + 120,
        "sub": name,
    }
    
    if use_uri:
        payload["uri"] = f"GET api.coinbase.com{path}"
    
    headers = {
        "kid": name,
        "nonce": str(now),
        "typ": "JWT"
    }
    
    token = jwt.encode(payload, pem_secret, algorithm="ES256", headers=headers)
    
    resp = requests.get(
        f"https://api.coinbase.com{path}",
        headers={"Authorization": f"Bearer {token}"},
        params={"limit": 1}
    )
    
    if resp.status_code == 200:
        print(f"✅ SUCCESS!")
        return True
    else:
        print(f"❌ FAILED ({resp.status_code}): {resp.text}")
        return False

# Candidates for Key Name
names = [
    key_id,
    f"organizations/{project_id}/apiKeys/{key_id}",
]

for name in names:
    for uri_opt in [True, False]:
        if try_key_name(name, uri_opt):
            print(f"\nTHE CORRECT KEY NAME IS: {name}")
            exit(0)

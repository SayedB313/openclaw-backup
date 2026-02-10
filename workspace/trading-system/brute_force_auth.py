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

def test_permutation(name, iss, use_uri):
    now = int(time.time())
    path = "/api/v3/brokerage/products"
    
    payload = {
        "iss": iss,
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
    
    try:
        token = jwt.encode(payload, pem_secret, algorithm="ES256", headers=headers)
        resp = requests.get(
            f"https://api.coinbase.com{path}",
            headers={"Authorization": f"Bearer {token}"},
            params={"limit": 1},
            timeout=5
        )
        if resp.status_code == 200:
            return True, resp.status_code, ""
        return False, resp.status_code, resp.text
    except Exception as e:
        return False, 0, str(e)

# Permutations
names = [
    key_id,
    "sayed@oumafy.com",
    project_id,
    f"projects/{project_id}/apiKeys/{key_id}",
]
issuers = ["cdp", "coinbase-cloud"]

print(f"{'Name':<80} | {'Iss':<15} | {'URI Pattern'} | {'Stat'} | {'Result'}")
print("-" * 140)

for name in names:
    for iss in issuers:
        for uri_pattern in [
            f"GET api.coinbase.com/api/v3/brokerage/products",
            f"GET /api/v3/brokerage/products",
            None
        ]:
            success, status, text = test_permutation(name, iss, uri_pattern is not None)
            res_str = "✅ SUCCESS" if success else f"❌ {text[:50]}"
            print(f"{name[0:77]:<80} | {iss:<15} | {str(uri_pattern):<30} | {status:<4} | {res_str}")
            if success:
                print(f"\nWINNER FOUND!")
                print(f"Name: {name}")
                print(f"Iss: {iss}")
                print(f"URI Pattern: {uri_pattern}")
                exit(0)

import base64
import json
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import jwt
import time

def raw_to_pem(raw_b64):
    # Raw 64-byte key material to PKCS#8 PEM
    key_bytes = base64.b64decode(raw_b64)
    if len(key_bytes) != 64:
        raise ValueError(f"Expected 64 bytes, got {len(key_bytes)}")
    
    # The first 32 bytes are the private key
    priv_bytes = key_bytes[:32]
    
    # Create EC private key object
    d = int.from_bytes(priv_bytes, 'big')
    key = ec.derive_private_key(d, ec.SECP256R1(), default_backend())
    
    # Export to PEM
    pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')
    
    return pem

with open("/home/openclaw/.secrets/coinbase.json") as f:
    secrets = json.load(f)

try:
    pem = raw_to_pem(secrets["api_secret"])
    print("PEM generated successfully")
    
    now = int(time.time())
    payload = {
        "iss": "coinbase-cloud",
        "nbf": now,
        "exp": now + 120,
        "sub": secrets["api_key"],
    }
    headers = {
        "kid": secrets["api_key"],
        "nonce": str(now)
    }
    
    token = jwt.encode(payload, pem, algorithm="ES256", headers=headers)
    print("JWT generated successfully!")
    print(f"Token: {token[:20]}...")
except Exception as e:
    print(f"Error: {e}")

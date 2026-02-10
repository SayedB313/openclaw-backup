#!/usr/bin/env python3
"""
Coinbase Advanced Trade API Integration
Fetches prices, order books, and executes trades.

API Docs: https://docs.cloud.coinbase.com/advanced-trade-api/docs/welcome
"""

import json
import time
import hmac
import hashlib
import requests
import jwt
import secrets
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from cryptography.hazmat.primitives import serialization


class CoinbaseClient:
    """
    Client for Coinbase Advanced Trade API.
    Handles authentication via Cloud API Keys (JWT).
    """

    API_URL = "https://api.coinbase.com/api/v3/brokerage"

    def __init__(self, key_name: str, key_secret: str):
        self.key_name = key_name
        self.key_secret = key_secret
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "ResonanceTradingSystem/4.0"
        })

    def _generate_jwt(self, method: str, path: str) -> str:
        """Generate a JWT for authentication using the CDP SDK logic."""
        now = int(time.time())
        uri_path = path.split('?')[0]
        
        payload = {
            "iss": "cdp",
            "nbf": now,
            "exp": now + 120,
            "sub": self.key_name,
            "uri": f"{method} api.coinbase.com{uri_path}"
        }
        
        headers = {
            "kid": self.key_name,
            "nonce": secrets.token_hex(),
            "typ": "JWT"
        }
        
        private_key = serialization.load_pem_private_key(
            self.key_secret.encode("utf-8"), 
            password=None
        )
        
        token = jwt.encode(
            payload, 
            private_key, 
            algorithm="ES256", 
            headers=headers
        )
        return token

    def _request(self, method: str, path: str, params: Dict = None, data: Dict = None) -> Dict:
        """Make an authenticated request."""
        jwt_token = self._generate_jwt(method, path)
        
        headers = {
            "Authorization": f"Bearer {jwt_token}"
        }
        
        url = f"https://api.coinbase.com{path}"
        
        try:
            if method == "GET":
                resp = self.session.get(url, params=params, headers=headers)
            elif method == "POST":
                resp = self.session.post(url, json=data, headers=headers)
            else:
                return {"error": f"Unsupported method: {method}"}
            
            if resp.status_code != 200:
                return {"error": f"HTTP {resp.status_code}: {resp.text}"}
            
            return resp.json()
        except Exception as e:
            return {"error": str(e)}

    # ─── Public Market Data ───

    def get_product(self, product_id: str) -> Dict:
        """Get information for a single product (e.g., 'BTC-USD')."""
        return self._request("GET", f"/api/v3/brokerage/products/{product_id}")

    def get_products(self, limit: int = 50, product_type: str = "SPOT") -> List[Dict]:
        """Get a list of available products."""
        data = self._request("GET", "/api/v3/brokerage/products", params={"limit": limit, "product_type": product_type})
        return data.get("products", [])

    def get_product_book(self, product_id: str, limit: int = 20) -> Dict:
        """Get the order book for a product."""
        # CDP REST API for V3 uses /api/v3/brokerage/product_book
        data = self._request("GET", "/api/v3/brokerage/product_book", params={"product_id": product_id, "limit": limit})
        
        if "error" in data:
            return data
            
        # The response is nested: {"pricebook": {"product_id": "BTC-USD", "bids": [...], "asks": [...]}}
        # Note: 'pricebook' is lowercase 'b' in V3 CDP API
        price_book = data.get("pricebook", data.get("price_book", {}))
        bids = price_book.get("bids", [])
        asks = price_book.get("asks", [])
        
        # In V3, bids/asks are lists of objects: [{"price": "...", "size": "..."}, ...]
        best_bid = float(bids[0]["price"]) if bids else 0
        best_ask = float(asks[0]["price"]) if asks else 0
        mid_price = (best_bid + best_ask) / 2 if (best_bid + best_ask) > 0 else 0
        spread = best_ask - best_bid
        spread_pct = spread / mid_price if mid_price > 0 else 0
        
        bid_depth = sum(float(b.get("size", 0)) for b in bids[:5])
        ask_depth = sum(float(a.get("size", 0)) for a in asks[:5])
        
        return {
            "best_bid": best_bid,
            "best_ask": best_ask,
            "mid_price": mid_price,
            "spread": spread,
            "spread_pct": spread_pct,
            "bid_depth": bid_depth,
            "ask_depth": ask_depth,
            "raw": price_book
        }

    def get_candles(self, product_id: str, start: str, end: str, granularity: str = "ONE_HOUR") -> List[Dict]:
        """Get historical candles for a product.
        granularity: ONE_MINUTE, FIVE_MINUTE, FIFTEEN_MINUTE, ONE_HOUR, SIX_HOUR, ONE_DAY
        """
        data = self._request(
            "GET", 
            f"/api/v3/brokerage/products/{product_id}/candles",
            params={"start": start, "end": end, "granularity": granularity}
        )
        return data.get("candles", [])

    def get_recent_candles(self, product_id: str, granularity: str = "ONE_HOUR", limit: int = 50) -> List[Dict]:
        """Get recent candles (convenience method). Uses Unix timestamps."""
        import time
        
        granularity_map = {
            "ONE_MINUTE": 60,
            "FIVE_MINUTE": 300,
            "FIFTEEN_MINUTE": 900,
            "ONE_HOUR": 3600,
            "SIX_HOUR": 21600,
            "ONE_DAY": 86400
        }
        
        seconds = granularity_map.get(granularity, 3600)
        end_ts = int(time.time())
        start_ts = end_ts - (seconds * limit)
        
        return self.get_candles(product_id, str(start_ts), str(end_ts), granularity)

    # ─── Trading (Private) ───

    def get_accounts(self) -> List[Dict]:
        """Get a list of accounts."""
        data = self._request("GET", "/api/v3/brokerage/accounts")
        return data.get("accounts", [])

    # ─── Analysis Helpers ───

    def analyze_ticker(self, product_id: str) -> Dict:
        """Format ticker data for the trading engine."""
        product = self.get_product(product_id)
        book = self.get_product_book(product_id)
        
        if "error" in product or "error" in book:
            return {"error": product.get("error", book.get("error", "Unknown"))}
        
        prod_data = product.get("product", product)
        
        return {
            "event_name": product_id,
            "product_id": product_id,
            "category": "crypto",
            "market_price": book["mid_price"],
            "best_bid": book["best_bid"],
            "best_ask": book["best_ask"],
            "spread_pct": book["spread_pct"],
            "bid_depth": book["bid_depth"],
            "ask_depth": book["ask_depth"],
            "volume_24h": float(prod_data.get("volume_24h", 0)),
            "volatility_24h": float(prod_data.get("volume_percentage_change_24h", 0)),
            "price_momentum_1h": 0.0,
            "signals": {}
        }

if __name__ == "__main__":
    print("Coinbase Client Logic Updated")

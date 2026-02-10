#!/usr/bin/env python3
"""
Polymarket API Integration
Fetches markets, prices, order books from Polymarket's CLOB API.

Polymarket API docs: https://docs.polymarket.com/
CLOB API: https://clob.polymarket.com
Gamma API: https://gamma-api.polymarket.com (market metadata)
"""

import json
import time
import requests
from typing import Dict, List, Optional
from datetime import datetime, timezone


class PolymarketClient:
    """
    Client for Polymarket's CLOB (Central Limit Order Book) API.
    Used for reading market data. Trading requires separate auth.
    """

    CLOB_URL = "https://clob.polymarket.com"
    GAMMA_URL = "https://gamma-api.polymarket.com"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "ResonanceTradingSystem/3.0"
        })
        if api_key:
            self.session.headers["Authorization"] = f"Bearer {api_key}"

    # ─── Market Discovery ───

    def get_markets(self, limit: int = 50, active: bool = True, 
                    category: Optional[str] = None) -> List[Dict]:
        """
        Fetch available markets from Gamma API.
        
        Categories: politics, crypto, sports, entertainment, science, etc.
        """
        params = {
            "limit": limit,
            "active": active,
            "closed": False,
        }
        if category:
            params["tag"] = category
        
        try:
            resp = self.session.get(f"{self.GAMMA_URL}/markets", params=params)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return [{"error": str(e)}]

    def get_market(self, condition_id: str) -> Dict:
        """Get detailed info for a specific market."""
        try:
            resp = self.session.get(f"{self.GAMMA_URL}/markets/{condition_id}")
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return {"error": str(e)}

    def search_markets(self, query: str, limit: int = 20) -> List[Dict]:
        """Search markets by keyword."""
        params = {"query": query, "limit": limit}
        try:
            resp = self.session.get(f"{self.GAMMA_URL}/markets", params=params)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return [{"error": str(e)}]

    # ─── Price & Order Book ───

    def get_price(self, token_id: str) -> Dict:
        """Get current price for a token (YES or NO side)."""
        try:
            resp = self.session.get(f"{self.CLOB_URL}/price", params={"token_id": token_id})
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return {"error": str(e)}

    def get_order_book(self, token_id: str) -> Dict:
        """
        Get order book for a token.
        Returns bids and asks with depth.
        """
        try:
            resp = self.session.get(f"{self.CLOB_URL}/book", params={"token_id": token_id})
            resp.raise_for_status()
            book = resp.json()
            
            # Calculate useful metrics
            bids = book.get("bids", [])
            asks = book.get("asks", [])
            
            best_bid = float(bids[0]["price"]) if bids else 0
            best_ask = float(asks[0]["price"]) if asks else 1
            mid_price = (best_bid + best_ask) / 2
            spread = best_ask - best_bid
            spread_pct = spread / mid_price if mid_price > 0 else 1
            
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
                "raw": book
            }
        except Exception as e:
            return {"error": str(e)}

    def get_market_trades(self, condition_id: str, limit: int = 50) -> List[Dict]:
        """Get recent trades for a market."""
        try:
            resp = self.session.get(
                f"{self.CLOB_URL}/trades",
                params={"asset_id": condition_id, "limit": limit}
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return [{"error": str(e)}]

    # ─── Analysis Helpers ───

    def analyze_market(self, condition_id: str, yes_token_id: str, 
                       no_token_id: str) -> Dict:
        """
        Full analysis of a market for the trading engine.
        Returns data formatted for engine.evaluate_opportunity().
        """
        market = self.get_market(condition_id)
        book = self.get_order_book(yes_token_id)
        
        if "error" in market or "error" in book:
            return {"error": market.get("error", book.get("error", "Unknown"))}
        
        # Calculate volume (from market metadata)
        volume_24h = float(market.get("volume", 0))
        
        # Event timing
        end_date = market.get("end_date_iso", "")
        created = market.get("created_at", "")
        
        event_start_ts = None
        event_end_ts = None
        time_fraction = 0.65  # default
        
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
                event_end_ts = end_dt.timestamp()
                
                if created:
                    start_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                    event_start_ts = start_dt.timestamp()
                    
                    now = time.time()
                    duration = event_end_ts - event_start_ts
                    elapsed = now - event_start_ts
                    time_fraction = elapsed / duration if duration > 0 else 0
            except (ValueError, TypeError):
                pass
        
        return {
            "event_name": market.get("question", "Unknown"),
            "condition_id": condition_id,
            "yes_token_id": yes_token_id,
            "no_token_id": no_token_id,
            "category": market.get("tags", [None])[0] if market.get("tags") else "unknown",
            "market_price": book["mid_price"],
            "best_bid": book["best_bid"],
            "best_ask": book["best_ask"],
            "spread_pct": book["spread_pct"],
            "bid_depth": book["bid_depth"],
            "ask_depth": book["ask_depth"],
            "volume_24h": volume_24h,
            "event_start_timestamp": event_start_ts,
            "event_end_timestamp": event_end_ts,
            "time_fraction": time_fraction,
            "end_date": end_date,
            "description": market.get("description", ""),
            "signals": {}  # To be filled by scouts
        }

    def scan_opportunities(self, categories: List[str] = None, 
                          min_volume: float = 1000) -> List[Dict]:
        """
        Scan all active markets for potential trading opportunities.
        This is what the scouts call periodically.
        """
        if categories is None:
            categories = ["politics", "crypto", "sports", "science"]
        
        opportunities = []
        
        for cat in categories:
            markets = self.get_markets(limit=20, category=cat)
            
            for market in markets:
                if isinstance(market, dict) and "error" not in market:
                    volume = float(market.get("volume", 0))
                    if volume >= min_volume:
                        opportunities.append({
                            "condition_id": market.get("condition_id"),
                            "question": market.get("question"),
                            "category": cat,
                            "volume": volume,
                            "end_date": market.get("end_date_iso"),
                            "tokens": market.get("tokens", [])
                        })
        
        return opportunities


if __name__ == "__main__":
    client = PolymarketClient()
    print("Scanning Polymarket...")
    
    markets = client.get_markets(limit=5)
    for m in markets:
        if isinstance(m, dict) and "error" not in m:
            print(f"  • {m.get('question', '?')} | Vol: {m.get('volume', 0)}")
    
    print(f"\nFound {len(markets)} markets")

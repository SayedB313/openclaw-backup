#!/usr/bin/env python3
"""
Scout Module v5.0 — Crypto-Only Pivot
3 Scouts: Momentum, Orderbook, Sentiment

ScoutAlpha: Crypto Momentum (price changes, volume spikes)
ScoutBeta: Crypto Orderbook (Coinbase depth, spread)
ScoutGamma: Sentiment (news/social classification)
"""

import json
import time
import requests
from typing import Dict, List
from datetime import datetime, timezone


class ScoutAlpha:
    """
    Crypto Momentum Scout
    Model: qwen2.5-vl-3b-instruct (LM Studio)
    Job: Track price momentum, volume changes, multi-timeframe analysis.
    """

    def __init__(self, coinbase_client, lm_studio_url: str = "http://100.103.223.74:1234"):
        self.client = coinbase_client
        self.lm_url = lm_studio_url
        self.scout_id = "alpha"
        self.price_history = {}  # {product_id: [prices]}

    def scan_momentum(self, product_ids: List[str]) -> Dict:
        """Track price momentum across products."""
        results = {
            "scout_id": self.scout_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "momentum": {}
        }
        
        for pid in product_ids:
            try:
                ticker = self.client.analyze_ticker(pid)
                if "error" not in ticker:
                    price = ticker["market_price"]
                    vol = ticker.get("volume_24h", 0)
                    
                    # Track price history for momentum
                    if pid not in self.price_history:
                        self.price_history[pid] = []
                    self.price_history[pid].append(price)
                    
                    # Keep last 60 prices (1 hour at 1/min)
                    if len(self.price_history[pid]) > 60:
                        self.price_history[pid] = self.price_history[pid][-60:]
                    
                    history = self.price_history[pid]
                    momentum_1h = 0
                    if len(history) >= 2:
                        momentum_1h = ((price - history[0]) / history[0]) * 100
                    
                    results["momentum"][pid] = {
                        "price": price,
                        "volume_24h": vol,
                        "momentum_1h_pct": round(momentum_1h, 4),
                        "samples": len(history)
                    }
            except Exception as e:
                results["momentum"][pid] = {"error": str(e)}
        
        return results

    def get_crypto_news_summary(self) -> str:
        """Ask LM Studio to summarize recent crypto market conditions."""
        try:
            resp = requests.post(
                f"{self.lm_url}/v1/chat/completions",
                json={
                    "model": "qwen2.5-vl-3b-instruct",
                    "messages": [{"role": "user", "content": 
                        "In 2 sentences, summarize the current crypto market conditions. "
                        "Focus on BTC dominance, overall market trend, and any major events."}],
                    "temperature": 0.3,
                    "max_tokens": 100
                },
                timeout=10
            )
            return resp.json()["choices"][0]["message"]["content"]
        except:
            return "LM Studio unreachable — no news summary"


class ScoutBeta:
    """
    Coinbase Orderbook Scout
    Model: qwen2.5-vl-3b-instruct (LM Studio)
    Job: Scan Coinbase for price action, orderbook depth, spread analysis.
    """

    def __init__(self, coinbase_client, lm_studio_url: str = "http://100.103.223.74:1234"):
        self.client = coinbase_client
        self.lm_url = lm_studio_url
        self.scout_id = "beta"

    def scan_coinbase(self, product_ids: List[str]) -> List[Dict]:
        """Scan specified products for trading opportunities."""
        opportunities = []
        for pid in product_ids:
            try:
                ticker = self.client.analyze_ticker(pid)
                if "error" not in ticker:
                    ticker["rsi_14"] = self._calculate_rsi_stub(pid)
                    ticker["ma_20"] = ticker["market_price"] * 0.98  # stub
                    ticker["std_20"] = ticker["market_price"] * 0.02  # stub
                    opportunities.append(ticker)
            except Exception as e:
                pass
        return opportunities

    def _calculate_rsi_stub(self, product_id: str) -> float:
        """Real RSI needs historical candles — stub for now."""
        return 45.0


class ScoutGamma:
    """
    Sentiment Scout
    Model: gemma-2-2b-it (LM Studio)
    Job: Fast sentiment classification from market context.
    """

    def __init__(self, lm_studio_url: str = "http://100.103.223.74:1234"):
        self.lm_url = lm_studio_url
        self.scout_id = "gamma"

    def classify_sentiment(self, texts: List[str] = None) -> float:
        """Return aggregate sentiment 0-1."""
        if not texts:
            texts = [
                "What is the current crypto market sentiment?",
                "Are traders bullish or bearish on Bitcoin today?"
            ]
        
        prompt = (
            "You are a crypto sentiment classifier. "
            "Based on general market conditions, output a single number between 0.0 (extreme fear) "
            "and 1.0 (extreme greed). Output ONLY the number.\n\n"
            f"Context: {texts[:5]}"
        )
        
        try:
            resp = requests.post(
                f"{self.lm_url}/v1/chat/completions",
                json={
                    "model": "gemma-2-2b-it",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                    "max_tokens": 10
                },
                timeout=10
            )
            content = resp.json()["choices"][0]["message"]["content"]
            import re
            match = re.search(r"(\d+\.?\d*)", content)
            score = float(match.group(1)) if match else 0.5
            return max(0.0, min(1.0, score))
        except:
            return 0.5


class ScoutSwarm:
    def __init__(self, coinbase_client, lm_studio_url: str = "http://100.103.223.74:1234"):
        self.alpha = ScoutAlpha(coinbase_client, lm_studio_url)
        self.beta = ScoutBeta(coinbase_client, lm_studio_url)
        self.gamma = ScoutGamma(lm_studio_url)

    def full_scan(self, product_ids: List[str]) -> Dict:
        return {
            "momentum": self.alpha.scan_momentum(product_ids),
            "news_summary": self.alpha.get_crypto_news_summary(),
            "opportunities": self.beta.scan_coinbase(product_ids),
            "sentiment": self.gamma.classify_sentiment()
        }


if __name__ == "__main__":
    swarm = ScoutSwarm(None)
    print("Scout Swarm v5.0 initialized (Crypto-Only)")

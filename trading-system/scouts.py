#!/usr/bin/env python3
"""
Scout Module v5.1 — Crypto-Only Pivot (LM Studio Timeout Fix)
3 Scouts: Momentum, Orderbook, Sentiment

ScoutAlpha: Crypto Momentum (price changes, volume spikes)
ScoutBeta: Crypto Orderbook (Coinbase depth, spread) - NO LM Studio dependency
ScoutGamma: Sentiment (news/social classification) - LM Studio with circuit breaker
"""

import json
import time
import requests
import threading
from typing import Dict, List, Optional
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout


class CircuitBreaker:
    """Circuit breaker pattern for LM Studio calls."""
    def __init__(self, failure_threshold=3, recovery_timeout=300):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self._lock = threading.Lock()
    
    def can_execute(self) -> bool:
        with self._lock:
            if self.state == "CLOSED":
                return True
            if self.state == "OPEN":
                if time.time() - self.last_failure_time > self.recovery_timeout:
                    self.state = "HALF_OPEN"
                    return True
                return False
            return True  # HALF_OPEN
    
    def record_success(self):
        with self._lock:
            self.failures = 0
            self.state = "CLOSED"
    
    def record_failure(self):
        with self._lock:
            self.failures += 1
            self.last_failure_time = time.time()
            if self.failures >= self.failure_threshold:
                self.state = "OPEN"


class ScoutAlpha:
    """
    Crypto Momentum Scout
    Model: qwen2.5-vl-3b-instruct (LM Studio) - with circuit breaker
    Job: Track price momentum, volume changes, multi-timeframe analysis.
    """

    def __init__(self, coinbase_client, lm_studio_url: str = "http://100.103.223.74:1234"):
        self.client = coinbase_client
        self.lm_url = lm_studio_url
        self.scout_id = "alpha"
        self.price_history = {}
        self.circuit_breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=300)

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
                    
                    if pid not in self.price_history:
                        self.price_history[pid] = []
                    self.price_history[pid].append(price)
                    
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

    def _fetch_news_summary(self) -> Optional[str]:
        """Internal method to fetch news from LM Studio."""
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
                timeout=(2, 4)  # (connect_timeout, read_timeout)
            )
            return resp.json()["choices"][0]["message"]["content"]
        except Exception:
            return None

    def get_crypto_news_summary(self) -> str:
        """Ask LM Studio for news summary with hard timeout via ThreadPoolExecutor."""
        if not self.circuit_breaker.can_execute():
            return "LM Studio circuit open — skipped"
        
        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(self._fetch_news_summary)
                result = future.result(timeout=6)  # Hard 6 second timeout
                
                if result:
                    self.circuit_breaker.record_success()
                    return result
                else:
                    self.circuit_breaker.record_failure()
                    return "LM Studio no response"
                    
        except FutureTimeout:
            self.circuit_breaker.record_failure()
            return "LM Studio timeout (6s)"
        except Exception as e:
            self.circuit_breaker.record_failure()
            return f"LM Studio error: {type(e).__name__}"


class ScoutBeta:
    """
    Coinbase Orderbook Scout
    NO LM Studio dependency — pure Coinbase API calls
    Job: Scan Coinbase for price action, orderbook depth, spread analysis.
    """

    def __init__(self, coinbase_client, lm_studio_url: str = None):
        """Note: lm_studio_url parameter kept for API compatibility but NOT used."""
        self.client = coinbase_client
        self.scout_id = "beta"
        self.price_history = {}

    def scan_coinbase(self, product_ids: List[str]) -> List[Dict]:
        """Scan specified products for trading opportunities."""
        opportunities = []
        for pid in product_ids:
            try:
                ticker = self.client.analyze_ticker(pid)
                if "error" not in ticker:
                    # Get real technical indicators from 15-min candles
                    candles = self.client.get_recent_candles(pid, "FIFTEEN_MINUTE", 50)
                    if candles:
                        ticker["rsi_14"] = self._calculate_rsi(candles, 14)
                        ticker["ma_20"] = self._calculate_ma(candles, 20)
                        ticker["std_20"] = self._calculate_std(candles, 20)
                        ticker["candles"] = candles[-20:]
                    else:
                        ticker["rsi_14"] = 50.0
                        ticker["ma_20"] = ticker["market_price"]
                        ticker["std_20"] = ticker["market_price"] * 0.01
                    
                    opportunities.append(ticker)
            except Exception as e:
                pass
        return opportunities

    def _calculate_rsi(self, candles: List[Dict], period: int = 14) -> float:
        """Calculate RSI from candle data."""
        if len(candles) < period + 1:
            return 50.0
        
        sorted_candles = sorted(candles, key=lambda x: x.get("start", 0))
        closes = [float(c.get("close", 0)) for c in sorted_candles]
        
        if len(closes) < period + 1:
            return 50.0
            
        changes = [closes[i] - closes[i-1] for i in range(1, len(closes))]
        recent_changes = changes[-period:]
        
        gains = [c for c in recent_changes if c > 0]
        losses = [-c for c in recent_changes if c < 0]
        
        avg_gain = sum(gains) / period if gains else 0
        avg_loss = sum(losses) / period if losses else 0
        
        if avg_loss == 0:
            return 100.0 if avg_gain > 0 else 50.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return max(0, min(100, rsi))

    def _calculate_ma(self, candles: List[Dict], period: int = 20) -> float:
        """Calculate Simple Moving Average."""
        if len(candles) < period:
            return float(candles[-1].get("close", 0)) if candles else 0
        
        sorted_candles = sorted(candles, key=lambda x: x.get("start", 0))
        closes = [float(c.get("close", 0)) for c in sorted_candles[-period:]]
        return sum(closes) / len(closes)

    def _calculate_std(self, candles: List[Dict], period: int = 20) -> float:
        """Calculate Standard Deviation."""
        if len(candles) < period:
            return 0.01
        
        sorted_candles = sorted(candles, key=lambda x: x.get("start", 0))
        closes = [float(c.get("close", 0)) for c in sorted_candles[-period:]]
        
        ma = sum(closes) / len(closes)
        variance = sum((c - ma) ** 2 for c in closes) / len(closes)
        return variance ** 0.5


class ScoutGamma:
    """
    Sentiment Scout
    Model: gemma-2-2b-it (LM Studio) - with circuit breaker
    Job: Fast sentiment classification from market context.
    """

    def __init__(self, lm_studio_url: str = "http://100.103.223.74:1234"):
        self.lm_url = lm_studio_url
        self.scout_id = "gamma"
        self.circuit_breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=300)

    def _fetch_sentiment(self, texts: List[str]) -> Optional[float]:
        """Internal method to fetch sentiment from LM Studio."""
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
                timeout=(2, 3)
            )
            content = resp.json()["choices"][0]["message"]["content"]
            import re
            match = re.search(r"(\d+\.?\d*)", content)
            score = float(match.group(1)) if match else 0.5
            return max(0.0, min(1.0, score))
        except Exception:
            return None

    def classify_sentiment(self, texts: List[str] = None) -> float:
        """Return aggregate sentiment 0-1 with hard timeout."""
        if not texts:
            texts = [
                "What is the current crypto market sentiment?",
                "Are traders bullish or bearish on Bitcoin today?"
            ]
        
        if not self.circuit_breaker.can_execute():
            return 0.5  # Neutral when circuit open
        
        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(self._fetch_sentiment, texts)
                result = future.result(timeout=5)  # Hard 5 second timeout
                
                if result is not None:
                    self.circuit_breaker.record_success()
                    return result
                else:
                    self.circuit_breaker.record_failure()
                    return 0.5
                    
        except FutureTimeout:
            self.circuit_breaker.record_failure()
            return 0.5
        except Exception:
            self.circuit_breaker.record_failure()
            return 0.5


class ScoutSwarm:
    def __init__(self, coinbase_client, lm_studio_url: str = "http://100.103.223.74:1234"):
        self.alpha = ScoutAlpha(coinbase_client, lm_studio_url)
        self.beta = ScoutBeta(coinbase_client)  # No LM Studio URL needed
        self.gamma = ScoutGamma(lm_studio_url)

    def full_scan(self, product_ids: List[str]) -> Dict:
        """Run full scout swarm scan with parallel execution where safe."""
        # ScoutBeta runs first - it's fast and reliable (no external deps)
        opportunities = self.beta.scan_coinbase(product_ids)
        
        # ScoutAlpha momentum - also reliable
        momentum = self.alpha.scan_momentum(product_ids)
        
        # These can timeout - run with caution
        news_summary = self.alpha.get_crypto_news_summary()
        sentiment = self.gamma.classify_sentiment()
        
        return {
            "momentum": momentum,
            "news_summary": news_summary,
            "opportunities": opportunities,
            "sentiment": sentiment
        }


if __name__ == "__main__":
    print("Scout Swarm v5.1 initialized (Crypto-Only, LM Studio Timeout Fix)")

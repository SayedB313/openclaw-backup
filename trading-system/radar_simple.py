#!/usr/bin/env python3
"""
Resonance Radar — 24/7 Persistent Scanner (Simplified, No LM Studio)
Loops every 60s. Scans markets. Alerts the Executor on triggers.
"""
import sys
import time
import json
import subprocess
from datetime import datetime, timezone
from typing import Dict, List

# Flush stdout immediately
sys.stdout.reconfigure(line_buffering=True)

PRODUCTS = [
    "BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD",
    "ADA-USD", "AVAX-USD", "LINK-USD", "DOT-USD", "DOGE-USD"
]

CHANNELS = {
    "signals": "1470434240108957969",
    "executor": "1469873664265818115",
}

def send_to_channel(channel_id, message):
    """Send a message to Discord."""
    try:
        # Skip for now - just log to stdout
        print(f"[Would send to {channel_id}]: {message[:50]}...")
    except Exception as e:
        print(f"Failed to send: {e}")

def calculate_rsi(candles: List[Dict], period: int = 14) -> float:
    """Calculate RSI from candles."""
    if len(candles) < period + 1:
        return 50.0
    
    sorted_candles = sorted(candles, key=lambda x: x.get("start", 0))
    closes = [float(c.get("close", 0)) for c in sorted_candles]
    
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

def calculate_ma(candles: List[Dict], period: int = 20) -> float:
    """Calculate Simple Moving Average."""
    if len(candles) < period:
        return float(candles[-1].get("close", 0)) if candles else 0
    
    sorted_candles = sorted(candles, key=lambda x: x.get("start", 0))
    closes = [float(c.get("close", 0)) for c in sorted_candles[-period:]]
    return sum(closes) / len(closes)

def calculate_std(candles: List[Dict], period: int = 20) -> float:
    """Calculate Standard Deviation."""
    if len(candles) < period:
        return 0.01
    
    sorted_candles = sorted(candles, key=lambda x: x.get("start", 0))
    closes = [float(c.get("close", 0)) for c in sorted_candles[-period:]]
    
    ma = sum(closes) / len(closes)
    variance = sum((c - ma) ** 2 for c in closes) / len(closes)
    return variance ** 0.5

def scan_product(client, product_id: str) -> Dict:
    """Scan a single product for trading signals."""
    from coinbase_client import CoinbaseClient
    
    ticker = client.analyze_ticker(product_id)
    if "error" in ticker:
        return None
    
    # Get candles for technical indicators
    candles = client.get_recent_candles(product_id, "FIFTEEN_MINUTE", 50)
    
    if candles:
        ticker["rsi_14"] = calculate_rsi(candles, 14)
        ticker["ma_20"] = calculate_ma(candles, 20)
        ticker["std_20"] = calculate_std(candles, 20)
    else:
        ticker["rsi_14"] = 50.0
        ticker["ma_20"] = ticker["market_price"]
        ticker["std_20"] = ticker["market_price"] * 0.01
    
    # Calculate Z-score
    price = ticker["market_price"]
    ma = ticker["ma_20"]
    std = ticker["std_20"]
    z_score = (price - ma) / std if std > 0 else 0
    ticker["z_score"] = z_score
    
    # Check triggers
    if z_score < -2.0 and ticker["rsi_14"] < 35:
        ticker["trigger"] = {"type": "MEAN_REVERSION_BUY", "strength": abs(z_score)}
    elif z_score > 2.0 and ticker["rsi_14"] > 65:
        ticker["trigger"] = {"type": "TREND_EXHAUSTION_SELL", "strength": ticker["rsi_14"]}
    else:
        ticker["trigger"] = None
    
    return ticker

def run_radar():
    print("📡 Resonance Radar v2.1 — 24/7 ACTIVE (Simplified)")
    print(f"Scanning {len(PRODUCTS)} products every 60s")
    
    from coinbase_client import CoinbaseClient
    from engine import TradingEngine
    
    with open("/home/openclaw/.secrets/coinbase.json") as f:
        secrets = json.load(f)
    
    client = CoinbaseClient(secrets["api_key"], secrets["api_secret"])
    engine = TradingEngine()
    
    scan_count = 0
    
    while True:
        try:
            scan_count += 1
            loop_start = time.time()
            
            opportunities = []
            triggered = []
            
            for pid in PRODUCTS:
                try:
                    opp = scan_product(client, pid)
                    if opp:
                        opportunities.append(opp)
                        
                        # Check if trigger fired
                        if opp.get("trigger"):
                            success, details = engine.evaluate_opportunity(opp)
                            if success:
                                triggered.append((opp, details))
                                
                                # Send alerts
                                signal_msg = (
                                    f"📡 **SIGNAL TRIGGERED**\n"
                                    f"**{pid}** @ ${opp['market_price']:,.2f}\n"
                                    f"Side: {details.get('side', 'N/A')}\n"
                                    f"Z-Score: {opp['z_score']:.2f}\n"
                                    f"RSI: {opp['rsi_14']:.1f}\n"
                                    f"Target: ${details.get('target', 0):,.2f}\n"
                                    f"Stop: ${details.get('stop', 0):,.2f}"
                                )
                                send_to_channel(CHANNELS["signals"], signal_msg)
                                
                                exec_msg = (
                                    f"🚨 **TRADE TRIGGERED**\n"
                                    f"Market: {pid} @ ${opp['market_price']:,.2f}\n"
                                    f"Side: {details.get('side', 'N/A')}\n"
                                    f"Z={opp['z_score']:.2f}, RSI={opp['rsi_14']:.1f}"
                                )
                                send_to_channel(CHANNELS["executor"], exec_msg)
                                
                                print(f"🔥 ALERT: {details.get('side', '?')} {pid} @ ${opp['market_price']:,.2f}")
                
                except Exception as e:
                    print(f"  Error scanning {pid}: {e}")
            
            # Status output
            btc_price = next((o["market_price"] for o in opportunities if o["product_id"] == "BTC-USD"), 0)
            eth_price = next((o["market_price"] for o in opportunities if o["product_id"] == "ETH-USD"), 0)
            
            print(f"[Scan #{scan_count}] BTC=${btc_price:,.0f} ETH=${eth_price:,.0f} | Scanned: {len(opportunities)} | Triggers: {len(triggered)} | Time: {time.time()-loop_start:.1f}s")
            
            # Sleep until next scan
            elapsed = time.time() - loop_start
            sleep_time = max(5, 60 - elapsed)
            print(f"[DEBUG] Scan complete. Elapsed: {elapsed:.1f}s, Sleeping: {sleep_time:.1f}s")
            sys.stdout.flush()
            time.sleep(sleep_time)
            print(f"[DEBUG] Woke up, starting scan #{scan_count + 1}")
            sys.stdout.flush()
            
        except Exception as e:
            print(f"Radar Error: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(10)

if __name__ == "__main__":
    run_radar()

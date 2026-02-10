#!/usr/bin/env python3
"""
Resonance Radar v2.3 — 24/7 Persistent Scanner
NO LM Studio dependencies — pure Coinbase API for reliability
Discord alerts integrated
"""
import sys
import time
import json
import subprocess
import signal
from datetime import datetime, timezone
from typing import Dict, List

sys.stdout.reconfigure(line_buffering=True)

PRODUCTS = [
    "BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD",
    "ADA-USD", "AVAX-USD", "LINK-USD", "DOT-USD", "DOGE-USD"
]

CHANNELS = {
    "signals": "1470434240108957969",
    "executor": "1469873664265818115",
}

running = True

def signal_handler(signum, frame):
    global running
    print(f"\n📡 Radar received signal {signum}, shutting down...")
    running = False

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

def send_to_channel(channel_id, message):
    """Send a message to Discord."""
    try:
        subprocess.run(
            ["openclaw", "message", "send", "--channel", "discord",
             "--target", f"channel:{channel_id}", "--message", message],
            timeout=15, capture_output=True
        )
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
    ticker = client.analyze_ticker(product_id)
    if "error" in ticker:
        return None
    
    candles = client.get_recent_candles(product_id, "FIFTEEN_MINUTE", 50)
    
    if candles:
        ticker["rsi_14"] = calculate_rsi(candles, 14)
        ticker["ma_20"] = calculate_ma(candles, 20)
        ticker["std_20"] = calculate_std(candles, 20)
    else:
        ticker["rsi_14"] = 50.0
        ticker["ma_20"] = ticker["market_price"]
        ticker["std_20"] = ticker["market_price"] * 0.01
    
    price = ticker["market_price"]
    ma = ticker["ma_20"]
    std = ticker["std_20"]
    z_score = (price - ma) / std if std > 0 else 0
    ticker["z_score"] = z_score
    
    # Check triggers
    if z_score < -2.0 and ticker["rsi_14"] < 35:
        ticker["signal"] = "BUY"
        ticker["strength"] = abs(z_score)
    elif z_score > 2.0 and ticker["rsi_14"] > 65:
        ticker["signal"] = "SELL"
        ticker["strength"] = z_score
    else:
        ticker["signal"] = None
        ticker["strength"] = 0
    
    return ticker

def run_radar():
    print("📡 Resonance Radar v2.3 — ACTIVE (No LM Studio)", flush=True)
    print(f"Products: {', '.join(PRODUCTS)}", flush=True)
    
    from coinbase_client import CoinbaseClient
    from engine import TradingEngine
    
    with open("/home/openclaw/.secrets/coinbase.json") as f:
        secrets = json.load(f)
    
    client = CoinbaseClient(secrets["api_key"], secrets["api_secret"])
    engine = TradingEngine()
    
    scan_count = 0
    
    while running:
        scan_count += 1
        loop_start = time.time()
        
        print(f"\n--- Scan #{scan_count} @ {datetime.now().strftime('%H:%M:%S')} ---", flush=True)
        
        try:
            opportunities = []
            triggered = []
            
            for pid in PRODUCTS:
                if not running:
                    break
                try:
                    opp = scan_product(client, pid)
                    if opp:
                        opportunities.append(opp)
                        
                        if opp.get("signal"):
                            success, details = engine.evaluate_opportunity(opp)
                            if success:
                                triggered.append((opp, details))
                                
                                # Discord alerts
                                signal_msg = (
                                    f"📡 **SIGNAL: {opp['signal']} {pid}**\n"
                                    f"Price: ${opp['market_price']:,.2f}\n"
                                    f"Z-Score: {opp['z_score']:.2f} | RSI: {opp['rsi_14']:.1f}\n"
                                    f"Target: ${details.get('target', 0):,.2f} | Stop: ${details.get('stop', 0):,.2f}"
                                )
                                send_to_channel(CHANNELS["signals"], signal_msg)
                                
                                exec_msg = (
                                    f"🚨 **TRADE: {details.get('side', '?')} {pid}** @ ${opp['market_price']:,.2f}\n"
                                    f"Math: Z={opp['z_score']:.2f}, RSI={opp['rsi_14']:.1f}\n"
                                    f"Target: ${details.get('target', 0):,.2f} | Stop: ${details.get('stop', 0):,.2f}"
                                )
                                send_to_channel(CHANNELS["executor"], exec_msg)
                                
                                print(f"🔥 ALERT: {details.get('side', '?')} {pid} @ ${opp['market_price']:,.2f}", flush=True)
                
                except Exception as e:
                    print(f"  Error scanning {pid}: {e}", flush=True)
            
            # Summary
            btc = next((o for o in opportunities if o["product_id"] == "BTC-USD"), None)
            eth = next((o for o in opportunities if o["product_id"] == "ETH-USD"), None)
            
            btc_str = f"${btc['market_price']:,.0f}" if btc else "N/A"
            eth_str = f"${eth['market_price']:,.0f}" if eth else "N/A"
            scan_time = time.time() - loop_start
            
            print(f"BTC: {btc_str} | ETH: {eth_str} | Scanned: {len(opportunities)} | Triggers: {len(triggered)} | Time: {scan_time:.1f}s", flush=True)
            
            # Adaptive sleep
            elapsed = time.time() - loop_start
            sleep_time = max(5, 60 - elapsed)
            
            # Sleep in small increments to respect shutdown signal
            slept = 0
            while running and slept < sleep_time:
                time.sleep(0.5)
                slept += 0.5
                
        except Exception as e:
            print(f"Scan error: {e}", flush=True)
            import traceback
            traceback.print_exc()
            time.sleep(10)
    
    print("\n📡 Radar shutdown complete.", flush=True)

if __name__ == "__main__":
    run_radar()

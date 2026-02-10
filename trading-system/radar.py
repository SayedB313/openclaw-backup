#!/usr/bin/env python3
"""
Resonance Radar — 24/7 Persistent Scanner v2.2
Loops every 60s. Scans markets. Alerts the Executor on triggers.
LM Studio timeout fixes applied - uses ThreadPoolExecutor for hard timeouts.
"""
import sys
import time
import json
import signal
import subprocess
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout

# Flush stdout immediately
sys.stdout.reconfigure(line_buffering=True)

PRODUCTS = [
    "BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD",
    "ADA-USD", "AVAX-USD", "LINK-USD", "DOT-USD", "DOGE-USD"
]

CHANNELS = {
    "signals": "1470434240108957969",
    "executor": "1469873664265818115",
    "live_trades": "1470434241723502770",
    "journal": "1470434243304751148"
}

# Global flag for graceful shutdown
running = True

def signal_handler(signum, frame):
    global running
    print(f"\n📡 Radar received signal {signum}, shutting down gracefully...")
    running = False

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

def send_to_channel(channel_id, message):
    """Send a message to a Discord channel via openclaw CLI."""
    try:
        subprocess.run(
            ["openclaw", "message", "send", "--channel", "discord",
             "--target", f"channel:{channel_id}", "--message", message],
            timeout=15, capture_output=True
        )
    except Exception as e:
        print(f"Failed to send to channel {channel_id}: {e}")

def run_scan_with_timeout(swarm, product_ids, timeout_sec=45):
    """Run the scout scan with a hard timeout to prevent hanging."""
    try:
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(swarm.full_scan, product_ids)
            return future.result(timeout=timeout_sec)
    except FutureTimeout:
        print(f"⚠️ SCAN TIMEOUT: Scout swarm exceeded {timeout_sec}s - forcing continuation")
        return {
            "momentum": {"scout_id": "alpha", "momentum": {}},
            "news_summary": "SCAN TIMEOUT",
            "opportunities": [],
            "sentiment": 0.5,
            "timeout": True
        }
    except Exception as e:
        print(f"⚠️ SCAN ERROR: {e}")
        return {
            "momentum": {"scout_id": "alpha", "momentum": {}},
            "news_summary": f"ERROR: {e}",
            "opportunities": [],
            "sentiment": 0.5,
            "error": True
        }

def run_radar():
    print("📡 Resonance Radar v2.2 — 24/7 ACTIVE (LM Studio Timeout Fix)")
    print(f"Scanning {len(PRODUCTS)} products: {', '.join(PRODUCTS)}")
    
    from engine import TradingEngine
    from scouts import ScoutSwarm
    from coinbase_client import CoinbaseClient
    
    with open("config.json") as f:
        config = json.load(f)
    with open("/home/openclaw/.secrets/coinbase.json") as f:
        secrets = json.load(f)
        
    client = CoinbaseClient(secrets["api_key"], secrets["api_secret"])
    engine = TradingEngine()
    swarm = ScoutSwarm(client)
    
    scan_count = 0
    consecutive_timeouts = 0
    
    while running:
        loop_start = time.time()
        try:
            scan_count += 1
            
            # Run scan with hard timeout to prevent hanging
            results = run_scan_with_timeout(swarm, PRODUCTS, timeout_sec=45)
            
            # Track consecutive timeouts for circuit breaker logic
            if results.get("timeout"):
                consecutive_timeouts += 1
                if consecutive_timeouts >= 3:
                    print(f"⚠️ {consecutive_timeouts} consecutive timeouts - LM Studio may be down")
            else:
                consecutive_timeouts = 0
            
            triggered = []
            for opp in results.get("opportunities", []):
                try:
                    success, details = engine.evaluate_opportunity(opp)
                    
                    if success:
                        triggered.append(opp)
                        product = opp["product_id"]
                        price = opp["market_price"]
                        
                        # Send signal to #signals channel
                        signal_msg = (
                            f"📡 **SIGNAL TRIGGERED**\n"
                            f"**{product}** @ ${price:,.2f}\n"
                            f"Side: {details.get('side', 'N/A')}\n"
                            f"Z-Score: {details.get('trigger', {}).get('strength', 'N/A')}\n"
                            f"RSI: {opp.get('rsi_14', 'N/A')}\n"
                            f"Confidence: {details.get('confidence', 'N/A')}\n"
                            f"Target: ${details.get('target', 0):,.2f}\n"
                            f"Stop: ${details.get('stop', 0):,.2f}"
                        )
                        send_to_channel(CHANNELS["signals"], signal_msg)
                        
                        # Alert executor for decision
                        exec_msg = (
                            f"🚨 **TRADE TRIGGERED — DECISION NEEDED**\n"
                            f"Market: {product} @ ${price:,.2f}\n"
                            f"Side: {details.get('side', 'N/A')}\n"
                            f"Math: Z={details.get('trigger', {}).get('strength', 0):.2f}, "
                            f"RSI={opp.get('rsi_14', 0):.1f}\n"
                            f"Target: ${details.get('target', 0):,.2f}\n"
                            f"Stop: ${details.get('stop', 0):,.2f}\n"
                            f"Mode: {config['system']['mode']}"
                        )
                        send_to_channel(CHANNELS["executor"], exec_msg)
                        
                        print(f"🔥 ALERT: {details.get('side', '?')} {product} @ ${price:,.2f}")
                except Exception as e:
                    print(f"  Error evaluating {opp.get('product_id', 'unknown')}: {e}")
            
            # Status log
            prices = {o["product_id"]: o["market_price"] for o in results.get("opportunities", [])}
            sentiment = results.get("sentiment", 0.5)
            loop_time = time.time() - loop_start
            
            btc_price = prices.get("BTC-USD", 0)
            eth_price = prices.get("ETH-USD", 0)
            
            status = f"[Scan #{scan_count}] BTC=${btc_price:,.0f} ETH=${eth_price:,.0f} | Sentiment: {sentiment:.2f} | Triggers: {len(triggered)} | Time: {loop_time:.1f}s"
            if results.get("timeout"):
                status += " ⚠️TIMEOUT"
            print(status)
            
            # Post scan summary to #executor every 10 scans (every ~10 min)
            if scan_count % 10 == 0:
                summary_msg = (
                    f"📡 **Radar Status** (Scan #{scan_count})\n"
                    f"BTC: ${btc_price:,.0f} | ETH: ${eth_price:,.0f}\n"
                    f"Sentiment: {sentiment:.2f} | Triggers (last 10): {len(triggered)}\n"
                    f"Scan time: {loop_time:.1f}s | Status: {'⚠️ Timeout' if results.get('timeout') else '✅ OK'}"
                )
                send_to_channel(CHANNELS["executor"], summary_msg)
            
            # Adaptive sleep - maintain 60s loop even if scan was slow
            elapsed = time.time() - loop_start
            sleep_time = max(5, 60 - elapsed)
            
            # If we had timeouts, add a small extra delay to let LM Studio recover
            if consecutive_timeouts > 0:
                sleep_time += min(consecutive_timeouts * 5, 30)  # Max +30s
            
            time.sleep(sleep_time)
            
        except Exception as e:
            print(f"Radar Error: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(10)
    
    print("📡 Radar shutdown complete.")

if __name__ == "__main__":
    run_radar()

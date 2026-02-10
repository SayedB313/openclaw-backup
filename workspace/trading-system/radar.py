#!/usr/bin/env python3
"""
Resonance Radar — 24/7 Persistent Scanner
Loops every 60s. Scans markets. Alerts the Executor on triggers.
"""
import sys
import time
import json
import subprocess
from engine import TradingEngine
from scouts import ScoutSwarm
from coinbase_client import CoinbaseClient

# Flush stdout immediately (fix buffering issue)
sys.stdout.reconfigure(line_buffering=True)

PRODUCTS = [
    "BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD",
    "ADA-USD", "AVAX-USD", "LINK-USD", "DOT-USD", "DOGE-USD"
]

# Channel IDs for routing
CHANNELS = {
    "signals": "1470434240108957969",
    "executor": "1469873664265818115",
    "live_trades": "1470434241723502770",
    "journal": "1470434243304751148"
}

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

def run_radar():
    print("📡 Resonance Radar v2.0 — 24/7 ACTIVE")
    print(f"Scanning {len(PRODUCTS)} products: {', '.join(PRODUCTS)}")
    
    with open("config.json") as f:
        config = json.load(f)
    with open("/home/openclaw/.secrets/coinbase.json") as f:
        secrets = json.load(f)
        
    client = CoinbaseClient(secrets["api_key"], secrets["api_secret"])
    engine = TradingEngine()
    swarm = ScoutSwarm(client)
    
    scan_count = 0
    
    while True:
        try:
            scan_count += 1
            results = swarm.full_scan(PRODUCTS)
            
            triggered = []
            for opp in results["opportunities"]:
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
            
            # Periodic status log (every 10 scans = ~10 min)
            if scan_count % 10 == 0:
                prices = {o["product_id"]: o["market_price"] for o in results["opportunities"]}
                macro = results.get("macro", {})
                sentiment = results.get("sentiment", 0.5)
                print(f"[Scan #{scan_count}] Prices: {json.dumps({k: f'${v:,.2f}' for k,v in prices.items()})} | Gold: ${macro.get('gold', 0):,.0f} | Sentiment: {sentiment:.2f} | Triggers: {len(triggered)}")
            
            time.sleep(60)
            
        except Exception as e:
            print(f"Radar Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    run_radar()

#!/usr/bin/env python3
import json
from engine import TradingEngine
from scouts import ScoutSwarm
from coinbase_client import CoinbaseClient

def run_dry_run():
    print("🚀 Starting Resonance Trading System v4.0 Dry Run...")
    
    # Load config and secrets
    with open("config.json") as f:
        config = json.load(f)
    with open("/home/openclaw/.secrets/coinbase.json") as f:
        secrets = json.load(f)
        
    client = CoinbaseClient(secrets["api_key"], secrets["api_secret"])
    engine = TradingEngine()
    swarm = ScoutSwarm(client)
    
    # 1. Macro Scan
    macro = swarm.alpha.get_macro_data()
    print(f"\n📊 MACRO VIEW:")
    print(f"  Gold: ${macro.get('gold')} | Silver: ${macro.get('silver')} | Ratio: {macro.get('ratio')}")
    
    # 2. Market Opportunity Scan
    products = ["BTC-USD", "ETH-USD", "SOL-USD"]
    print(f"\n📡 SCANNING MARKETS: {products}")
    scan_results = swarm.full_scan(products)
    
    if not scan_results.get("opportunities"):
        print("  ⚠️ No opportunities found. Check API connectivity.")
        print(f"  Debug: {scan_results}")
    
    # 3. Evaluation
    for opp in scan_results["opportunities"]:
        print(f"\n🔍 EVALUATING: {opp['product_id']}")
        print(f"  Price: ${opp['market_price']:.2f} | RSI: {opp['rsi_14']:.1f} | Spread: {opp['spread_pct']:.4%}")
        
        success, details = engine.evaluate_opportunity(opp)
        
        if success:
            print(f"  ✅ RECOMMENDATION: {details['recommendation']} {details['side']}")
            print(f"  💰 Position Size: ${details['position']['size_usd']:.2f}")
            print(f"  🎯 Target: ${details['target']:.2f} | 🛑 Stop: ${details['stop']:.2f}")
        else:
            print(f"  ❌ SKIP: {details['gates_failed'][-1] if details['gates_failed'] else 'Unknown'}")
            if "trigger" in details:
                print(f"     (Z-Score: {details['trigger'].get('strength', 0):.2f})")

if __name__ == "__main__":
    run_dry_run()

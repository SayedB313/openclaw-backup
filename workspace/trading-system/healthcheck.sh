#!/bin/bash
# Trading System Health Check
# Called by Arki (main-agent) to verify all components are operational

STATUS="✅"
ISSUES=""

# 1. Check radar.py is running
if pgrep -f "radar.py" > /dev/null 2>&1; then
    RADAR="✅ Running (PID $(pgrep -f 'radar.py' | head -1))"
else
    RADAR="❌ NOT RUNNING"
    STATUS="⚠️"
    ISSUES="$ISSUES\n- Radar is down"
fi

# 2. Check LM Studio on Mac (Tailscale)
LM_RESPONSE=$(curl -s --connect-timeout 5 http://100.103.223.74:1234/v1/models 2>&1)
if echo "$LM_RESPONSE" | grep -q "gemma-2-2b-it"; then
    LM_STUDIO="✅ Live (gemma-2-2b-it, qwen2.5-vl-3b)"
else
    LM_STUDIO="❌ Unreachable"
    STATUS="⚠️"
    ISSUES="$ISSUES\n- LM Studio on Mac is down (sleep? LM Studio closed?)"
fi

# 3. Check Coinbase API
CB_RESPONSE=$(cd /home/openclaw/.openclaw/workspace/trading-system && python3 -c "
from coinbase_client import CoinbaseClient
import json
with open('/home/openclaw/.secrets/coinbase.json') as f:
    s = json.load(f)
c = CoinbaseClient(s['api_key'], s['api_secret'])
t = c.analyze_ticker('BTC-USD')
print(f'BTC: \${t[\"market_price\"]:,.2f}')
" 2>&1)
if echo "$CB_RESPONSE" | grep -q "BTC:"; then
    COINBASE="✅ $CB_RESPONSE"
else
    COINBASE="❌ API Error"
    STATUS="⚠️"
    ISSUES="$ISSUES\n- Coinbase API failed"
fi

# 4. Check DeepSeek API
DS_RESPONSE=$(curl -s --connect-timeout 5 -X POST https://api.deepseek.com/v1/chat/completions \
    -H "Authorization: Bearer $(cat /home/openclaw/.secrets/deepseek.json | python3 -c 'import json,sys; print(json.load(sys.stdin)["api_key"])')" \
    -H "Content-Type: application/json" \
    -d '{"model":"deepseek-reasoner","messages":[{"role":"user","content":"ping"}],"max_tokens":5}' 2>&1)
if echo "$DS_RESPONSE" | grep -q "choices"; then
    DEEPSEEK="✅ Operational"
else
    DEEPSEEK="❌ API Error"
    STATUS="⚠️"
    ISSUES="$ISSUES\n- DeepSeek API failed"
fi

# Output
echo "$STATUS TRADING SYSTEM HEALTH"
echo "========================="
echo "Radar: $RADAR"
echo "LM Studio: $LM_STUDIO"
echo "Coinbase: $COINBASE"
echo "DeepSeek: $DEEPSEEK"
if [ -n "$ISSUES" ]; then
    echo ""
    echo "ISSUES:"
    echo -e "$ISSUES"
fi

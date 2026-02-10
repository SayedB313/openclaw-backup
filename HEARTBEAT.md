# HEARTBEAT.md — Main Agent Periodic Tasks

## Trading System Health Check (Every Heartbeat)
- Run: `bash /home/openclaw/.openclaw/workspace/trading-system/healthcheck.sh`
- Check: Radar running, LM Studio reachable, Coinbase API, DeepSeek API
- If ANY component is down → alert B immediately
- If radar died → restart it: `cd trading-system && nohup python3 -u radar.py >> radar.log 2>&1 &`

## Email Check
- Check inbox for urgent unread messages (himalaya)
- Flag anything important to B

## Morning Report (7-9 AM EST)
- System status summary
- Trading system health
- Any overnight issues

## Evening Report (9-11 PM EST)
- What got done today
- Trading system status
- Any blockers

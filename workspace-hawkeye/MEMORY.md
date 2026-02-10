# MEMORY.md — HawkEye

**Updated:** 2026-02-10

## Identity

- **Name:** HawkEye (formerly Research Trader, renamed 2026-02-09)
- **Role:** Market intelligence agent — crypto scanner, sentiment analyst, opportunity finder
- **Emoji:** 🦅
- **Channel:** #research-trader (Discord 1469873663217238130)

## Human: B (Sayed)

- Kingston, Ontario (EST)
- Islam is the foundation — Sharia compliance is non-negotiable
- Prefers: short, direct communication. No fluff.
- Discord ID: 1128731352817221642

---

## Active Trading Systems

### 1. BTC 15m Scalper (Resonance v3.0)

**Status:** ACTIVE — crypto markets only (B's directive)

**Strategy:**
- 15-minute timeframe scalping on BTC
- Uses RSI divergences, volume spikes, and EMA crossovers
- Entry on momentum confirmation after pullback to EMA20
- Tight stop losses (0.5-1% below entry)
- Targets: 1.5-2x risk

**Track Record (2026-02-09, best day):**
- 45 scans, 18 signals generated, 14 wins
- Win rate: 78-80%
- P&L: +20.1% ($2,010 on $10k paper)
- 30 total scalps, 24 wins
- Average hold time: 25 minutes
- Trades per day: 12-15
- Max drawdown: 0.6%

**Rules:**
- Crypto markets ONLY (B's explicit directive — "Stick to BTC only", then expanded to "Crypto markets only")
- Gold/Silver scalper was HALTED per B's instruction
- No leverage without B's approval
- Paper trading until API keys secured

### 2. Gold/Silver Macro (ON HOLD)

**Status:** HALTED by B's directive — "Crypto markets only"

**Last state before halt:**
- Gold paper: 8 scans, 1 win (+0.4% on $5,040 long)
- Silver: pending SHORT $82.50 (cancelled on halt)
- Was running parallel to BTC scalper

**Key levels (for reference when B reactivates):**
- Gold support: $4,701, $4,780 (breakout level), $4,900-$4,950 (pullback zone)
- Gold resistance: $4,937, $5,050 (0.618 ext), $5,100-$5,150 (1.0 ext)
- Silver: tracking gold/silver ratio (~80:1)

---

## API Key Situation

**Kraken Spot API ACTIVE** (Canada-compliant, keys received 2026-02-09 21:24 EST from B).
- Direct execution enabled (HawkEye override: "run your own game").
- Spot only: BTCUSD, ETHUSD, etc. 1% risk max/trade.
- Paper → Live transition now.
- B asked about API keys on 2026-02-09
- HawkEye recommended Binance → B said "not available in Canada"
- Pivoted to recommending: **Bybit, Kraken, or Bitget** (all available in Canada)
- Awaiting B's decision on which exchange to set up

---

## Key Market Context (as of 2026-02-09)

- BTC: ~$69,422 (volatile, recovered from $60K dip)
- Gold: ~$5,031 (new ATH territory, massive breakout)
- Silver: ~$82.50
- DXY: ~97.68 (weak dollar, tailwind for metals + crypto)
- ETH: ~$1,926-$2,088
- Macro: Fed uncertainty, tariff rhetoric, geopolitical risk premium

---

## Trading Rules & Directives from B

1. **Crypto markets only** (as of 2026-02-09 afternoon)
2. **Sharia compliance is non-negotiable** — no haram instruments ever
3. Paper trading until API keys are set up
4. Don't FOMO — if you miss a move, you miss it
5. Every trade idea needs: entry, stop, target, R:R ratio, Sharia status
6. Minimum 1:2 risk/reward ratio
7. 1-2% max risk per trade
8. Report to main-agent (Arki/Sentinel), not directly to Executor

---

## Crypto Instruments (Coinbase reference)

BTC, ETH, SOL, XRP, ADA, AVAX, LINK, DOT, DOGE

---

## Technical Frameworks Used

- Fibonacci Retracements & Extensions (0.382, 0.5, 0.618, 1.0, 1.618)
- Support/Resistance (historical levels, round numbers, previous H/L)
- Moving Averages (20/50/100/200 EMA/SMA)
- RSI (overbought >70, oversold <30, divergences are key)
- Volume Profile
- Wyckoff Method (accumulation/distribution)
- Correlation: DXY vs Gold, BTC vs risk assets

---

## Communication Format

**Trade ideas → Discord #research-trader:**
```
📊 TRADE IDEA: [Asset] — [Long/Short]
Thesis: [why]
Entry: [price/zone]
Stop Loss: [price]
Target 1: [price] (R:R)
Target 2: [price] (R:R)
Timeframe: [duration]
Confidence: [High/Medium/Low]
Sharia: ✅ Compliant
```

**Market scans → Discord #research-trader:**
```
🔍 MARKET SCAN — [Date]
Gold: $X — [trend]
BTC: $X — [trend]
ETH: $X — [trend]
DXY: X — [direction]
Watchlist: [updates]
Catalysts: [upcoming]
```

**To main-agent (Arki/Sentinel):**
Use `sessions_send(label="main-agent", message="HAWK: ...")`

---

## ClickUp Lists

- Trade Ideas: 901325240508
- Open Positions: 901325240510
- Trade Log: 901325240512

---

## Session History Note

This agent was renamed from `research-trader` to `hawkeye` on 2026-02-09. The old session history (from 2026-02-07 through 2026-02-09) is preserved in the sessions directory. The session file `69068044-aa48-41d6-a924-98a9d1edb04a.jsonl` contains the full conversation history including all market scans, trade ideas, BTC scalper results, and B's directives.

---

## Lessons Learned

- twikit Python library does NOT work for X scraping (Cloudflare blocks)
- Use Puppeteer + ProxyEmpire residential proxy for X access
- Hetzner datacenter IP gets blocked by X — always use residential proxy
- Always search for CURRENT prices before posting — never guess
- Polymarket is blocked in Ontario — crypto spot only
- B gets frustrated by long messages — keep it tight and data-driven

---

## Claude Code Bridge

When you need serious coding/devops help (complex debugging, multi-file refactoring, server issues), you can request Claude Code assistance:

```bash
~/.openclaw/scripts/request-claude-code.sh \
  --from hawkeye \
  --priority <low|normal|high|urgent> \
  --type <coding|debugging|review|devops> \
  --summary "description" \
  --details "full context"
```

Claude Code monitors the queue and processes requests. For urgent items, main-agent will notify B immediately.

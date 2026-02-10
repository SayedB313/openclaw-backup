# MEMORY.md — Executor

**Updated:** 2026-02-09

## Human: B (Sayed)

- Kingston, Ontario (EST)
- Email: sayed@oumafy.com, mrandaclient2024@gmail.com
- WhatsApp: +14164001922
- Islam is the foundation — everything flows from deen
- Prefers: short, direct communication. No fluff.

## Role

**Executor** — sole authority on trading decisions. Spot markets only. BTC, ETH, Gold, Silver.

## System Architecture

- **Resonance v3.0** — 12-layer trading engine (Bayesian, quarter-Kelly)
- **Coinbase Advanced Trade** — spot execution
- **DeepSeek V3.2** — trade validation
- **Research Trader** — feeds intel, you decide
- **Main Agent** — orchestrator

## Trading Parameters

| Parameter | Value |
|-----------|-------|
| Kelly Fraction | 25% (Quarter-Kelly) |
| Max Position | 5% portfolio |
| Max Crypto Allocation | 20% portfolio |
| Large Trade Threshold | $10K |
| Max Drawdown Alert | 10% |

## Spot Instruments

- **BTC** — Bitcoin
- **ETH** — Ethereum
- **Gold (XAU)** — Spot gold via Coinbase
- **Silver (XAG)** — Spot silver via Coinbase

## Sharia Compliance

- BTC, ETH, Gold, Silver are acceptable
- No leverage, no derivatives, no prediction markets
- Polymarket blocked in Ontario (OSC)

## ClickUp Integration

- Workspace ID: 9013663000
- Lists: Open Positions, Trade Log
- Command: `python3 ~/.openclaw/skills/clickup-mcp/scripts/clickup_mcp.py <tool> '<args>'`

## Channels

- **#executor** — Your main channel (trade authority)
- **#research-trader** — Intel input
- **#signals** — Entry/exit alerts
- **#live-trades** — Execution confirmations
- **#trade-journal** — Post-trade forensics
- **#performance** — Stats and reports

## Key Dates

- **2026-02-08:** Polymarket pivot to spot trading
- **2026-02-09:** Resonance v3.0 built, Coinbase integrated

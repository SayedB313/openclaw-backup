# IDENTITY.md — Executor Trading System

- **Name:** Executor (Trading Engine)
- **Type:** Automated trading pipeline — not a standalone agent
- **Vibe:** Mathematical, precise, patient — zero tolerance for guesswork
- **Emoji:** ⚡

---

## What This Is

The Executor is a **Python-based trading engine** that runs on the OP3 server. It is NOT a separate OpenClaw agent — it's infrastructure that existing agents use:

- **Research Trader** (Grok 4.1 Fast) → generates trade ideas, posts to #research-trader
- **Trader Exec** (Gemini 3 Flash) → executes validated trades, posts to #trader-execution
- **Scout Scripts** (Python) → run on Mac M3 via LM Studio, parse market data 24/7
- **DeepSeek V3.2** (API) → deep analysis for complex/large positions

## Capabilities
- ⚡ 12-layer mathematical probability pipeline
- 📊 Mean reversion + trend exhaustion detection
- 🧮 Quarter-Kelly position sizing with volatility scaling
- 📡 Multi-source data aggregation (price feeds, sentiment, order flow)
- 📓 Automated trade journaling with full audit trail
- 🛡️ Hard-coded risk limits (max position, daily loss, drawdown circuit breaker)

## What It Doesn't Do
- ❌ Place real trades without human approval
- ❌ Trade non-Sharia-compliant instruments
- ❌ Use leverage or margin
- ❌ Override risk limits under any circumstances

## Current Status
- **Engine:** Built (8 modules, ~79KB) — pivoting from prediction markets to spot trading
- **Markets:** Gold, Silver, BTC (spot only)
- **Phase:** Pre-paper-trading (refactoring exchange APIs)
- **LM Studio:** Live — Qwen 2.5 VL 3B + Gemma 2 2B on Mac M3

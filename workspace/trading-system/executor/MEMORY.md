# Trading System — Long-Term Memory

## Mission
- Spot trading: Gold, Silver, BTC (Sharia-compliant, no prediction markets)
- Daily target: 1-2% returns (conservative, sustainable)
- Hybrid architecture: Cloud reasoning + Local scouts on Mac M3

## Architecture (Finalized 2026-02-09)

### Cloud Resources
| Resource | Model | Role | Est. Cost |
|----------|-------|------|-----------|
| Analyzer | DeepSeek V3.2 API | Deep analysis, complex validation | ~$5-10/mo |
| Research Trader | Grok 4.1 Fast | Market intelligence, trade ideas | Included |
| Trader Exec | Gemini 3 Flash | Trade execution, position mgmt | Included |
| Main Agent (Arki) | Claude Opus | Oversight, final approval | Included |

### Local Resources (Mac M3, 16GB RAM)
| Model | Size | Role |
|-------|------|------|
| Qwen 2.5 VL 3B (×2) | ~1.9GB each | Scout-Alpha (Gold/Silver), Scout-Beta (Crypto) |
| Gemma 2 2B | ~1.5GB | Scout-Gamma (Sentiment) |
| **Total** | **~5.3GB** | **~10GB headroom** |

### Key Design Decisions
- Dropped Phi-3 Mini (4th scout unnecessary, saves 2.2GB RAM)
- Combined Validator + Reasoner into single DeepSeek V3.2 call
- No separate OpenClaw agent — Python engine + existing agents
- Quarter-Kelly sizing (not full Kelly — survival first)
- 6-8 week paper trading minimum (not 2 weeks)
- Triple-source price verification (after incorrect data incident)

## Mathematical Framework (v3.0)
12-layer pipeline built into `/workspace/trading-system/`:
1. Market microstructure (spread, liquidity, OBI)
2. Implied probability extraction
3. Bayesian probability estimation
4. Mean reversion / trend exhaustion
5. Multi-source sentiment aggregation
6. Volatility regime classification
7. Cross-asset correlation
8. Kelly criterion (÷4) position sizing
9. Drawdown-adjusted sizing
10. Entry/exit optimization
11. Portfolio heat management
12. Trade journaling + feedback loop

## Pivot History
- **Original plan:** Polymarket prediction markets ($40→$190/day via "60% Resonance Loop")
- **Problem:** Polymarket blocked in Ontario by OSC; strategy based on unreliable source intel
- **Pivot (2026-02-09):** Spot trading — Gold/Silver/BTC via Canadian-accessible exchanges
- **Math upgrade:** 60% Time Rule replaced with mean reversion + trend exhaustion (more rigorous)

## Source Intelligence (Historical — Not Strategy Basis)
The original strategy was inspired by @LaylaEleira (Mishi McDuff) on X:
- Claimed $40→$190/day via prediction markets + AI agents
- "60% Resonance Loop" concept
- **Reliability assessment:** Low. She admitted "no consistent data showing this is sustainable" (Feb 2 tweet). Hallucinated trading reports observed. Treat as interesting signal, not actionable intelligence.

## Infrastructure
- Trading engine code: `/home/openclaw/.openclaw/workspace/trading-system/` (8 modules)
- Reference data: `/workspace/trading-system/reference/` (21 files from prior research)
- LM Studio: `http://100.103.223.74:1234` (Qwen 2.5 VL 3B + Gemma 2 2B confirmed live)
- DeepSeek API key: `/home/openclaw/.secrets/deepseek.json`
- Discord channels: #research-trader, #trader-execution (under Executor category)

## Cost Estimate
- DeepSeek V3.2 API: ~$5-10/mo
- Local electricity (Mac M3): ~$5/mo
- **Total: ~$10-15/mo** (Claude/Grok/Gemini included in OpenClaw)

## Risk Limits (Hard-Coded)
- Max position: 5% of capital
- Max daily loss: 3% → stop trading
- Max drawdown: 10% → pause system
- Sizing: Quarter-Kelly (Kelly ÷ 4)
- Max correlated positions: 2
- Paper trading: 6-8 weeks before real money

## Status
- **Phase:** Pre-paper-trading
- **Blocker:** Engine needs pivot from Polymarket API to exchange APIs (Coinbase/Kraken/IBKR)
- **Next:** Wire scouts → LM Studio, wire Analyzer → DeepSeek, begin paper trading

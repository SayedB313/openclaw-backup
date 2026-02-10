# MEMORY.md — Long-Term Memory

## System Architecture (as of 2026-02-08)

### Agent Roster (8 agents) — Updated 2026-02-09 evening
| Agent | Model | Channel | Role |
|-------|-------|---------|------|
| main-agent / **Sentinel** | kimi-k2.5 (default) / opus | Discord DM with B | Orchestrator + personal assistant + eye in the sky |
| **hawkeye** | grok-4-1-fast | #research-trader | Market intelligence, crypto scanning |
| executor | opus | #executor + signals/live-trades/journal | Sole trade authority — crypto spot |
| engineer | opus | #engineering | PRD specialist → Claude Code pipeline |
| research-assistant | gemini-3-flash | #research-assistant | Quick research, fact-checking |
| deep-research | deepseek-reasoner | #deep-research | Deep analysis, multi-source synthesis |
| marketing | claude-4.5-sonnet | #marketing | Marketing strategy, content |
| arki-whatsapp | minimax-m2.1 | WhatsApp | B's daily companion |

### Conductor Retirement (2026-02-08)
- Conductor agent removed from config
- #conductor Discord channel deleted
- All orchestration/dispatch duties absorbed by Main Agent (me)
- All agent SOULs updated to route to `main-agent` instead of `conductor`
- Conductor's ORCHESTRATION.md saved to my workspace for reference
- Dispatch format: `ORCH: [Agent] — [Task Title]` with Context/Objective/Constraints/Output

### Skills (all 8 agents have all 3)
- `clickup-mcp` — ClickUp task management
- `twitter-x` — X/Twitter scraping via Puppeteer + residential proxy
- `email-himalaya` — Gmail via Himalaya CLI

### Infrastructure
- Server: OP3 (Hetzner), Tailscale, passwordless sudo
- GitHub backup: daily 11 PM EST cron → SayedB313/openclaw-backup
- Residential proxy: ProxyEmpire ($3.50/GB)
- X auth: manual cookie extraction from B's Mac Chrome (automated login unreliable)

## Key Decisions Log

### 2026-02-08
- Orphan branch approach for git backup (purged leaked secrets)
- Per-agent skill assignment (defaults schema doesn't support skills)
- Research Trader heartbeat every 4h, active 7AM-11PM EST
- MiniMax banned from cron jobs (OAuth issue in isolated sessions)
- Puppeteer over twikit for X scraping (Cloudflare blocks twikit's TLS fingerprint)
- Conductor merged into Main Agent — simpler, one less middleman
- Self-fix policy: I fix everything myself, only escalate for third-party requirements

### 2026-02-09
- **Morning Scan:** Gold $5,031 (ATH), BTC $70,200.
- **Executor-500 Review:** Critiqued v2.0 (Kimi 2.5); rejected 6% daily return claims. B greenlit full rebuild.
- **Resonance v3.0:** Built 12-layer Python engine (Bayesian updating, quarter-Kelly sizing, risk journal).
- **Pivot:** Polymarket blocked in Ontario (OSC). Shifted entire system to Spot Trading (BTC/ETH/Gold/Silver) on legal exchanges.
- **Structure:** `trader-exec` renamed to **Executor**; now holds sole trade authority. `research-trader` subservient (intel only).
- **Coinbase:** Integrated API (Operational).
- **DeepSeek:** API key integrated for trade validation.

## B's Patterns & Preferences
- Morning = peak energy. Don't bother late night (23:00-08:00) unless urgent
- Analysis paralysis is real — bias every interaction toward ACTION
- Systems collapse after ~1 week — keep tasks small, wins visible, friction low
- Hates fluff, loves results
- Islam is the lens for everything — Sharia compliance non-negotiable

## Fleet Upgrades (2026-02-08/09)
- **Executor System (Resonance v3.0):** 8-module Python engine, 12-layer strategy, DeepSeek V3.2 validator.
- **X/Twitter v2.0:** Native API v2 (oumafy account) + Puppeteer scraper (@Arki_OP3) both integrated
- **Local Node:** MacBook Air M3 running Ollama (DeepSeek-R1 8B, Llama 3.2 3B) + LM Studio (port 1234)
- **ACP/MCP Bridge:** Claude Desktop App connected to OpenClaw ecosystem
- **Email:** Himalaya CLI integration live system-wide

## Discord Channel Structure (Updated 2026-02-09 evening)

### Executor Category (5 channels)
- #executor (1469873664265818115) — Command center, Go/No-Go decisions
- #signals (1470434240108957969) — Radar alerts, Z-score/RSI triggers
- #live-trades (1470434241723502770) — Order confirmations
- #trade-journal (1470434243304751148) — Post-trade forensics + P&L
- #research-trader (1469873663217238130) — Market intel feed

### Head Quarters (4 channels)
- #engineering, #marketing, #research-assistant, #deep-research

### Deleted channels
- #performance, #formula-lab, #market-intel, #risk-monitor, #daily-brief, #conductor, #logs

## Trading System Status (as of 2026-02-09)
- **Radar v2.0:** Running 24/7, scanning 9 crypto (BTC/ETH/SOL/XRP/ADA/AVAX/LINK/DOT/DOGE)
- **Mode:** Paper trading
- **Bot swarm:** 2x Qwen 2.5 + 1x Gemma 2 2B (LM Studio on Mac) + DeepSeek V3.2 API
- **Health check:** `trading-system/healthcheck.sh` runs every heartbeat
- **Executor SOUL:** Trimmed to 2.5KB with channel routing

## Research Trader Notes
- First scan posted successfully: Gold $4,961 (ATH), Silver $78.02, BTC ~$68.5K
- Grok model has native X access for market queries
- Hallucinated a fake @LaylaEleira trading report — noted and corrected
- Profile actually returned empty data from scraper (private/low-follower account)

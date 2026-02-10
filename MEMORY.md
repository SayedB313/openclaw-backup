# MEMORY.md — Shared Fleet Memory

## Fleet Architecture (Updated 2026-02-10)

| Agent | Model | Channel | Role |
|-------|-------|---------|------|
| arki-whatsapp | claude-opus-4-6 | WhatsApp | Orchestrator + personal assistant |
| main-agent | MiniMax-M2.1 | Discord DM | Systems Watchdog (backups, health) |
| hawkeye | grok-4-1-fast | Discord #research-trader | Market intelligence, BTC scalping |
| executor | claude-opus-4-6 | Discord #executor | Trade execution (crypto spot) |
| engineer | claude-opus-4-6 | Discord #engineering | Code, architecture, PRDs |
| research-assistant | moonshot/kimi-k2.5 | Discord #research-assistant | Quick research, fact-checking |
| deep-research | deepseek-reasoner | Discord #deep-research | Deep analysis, synthesis |
| marketing | claude-sonnet-4-5 | Discord #marketing | Content, social media, copywriting |

## Key Changes (2026-02-10 Restructure)
- arki-whatsapp promoted to orchestrator (was daily companion only)
- main-agent demoted to systems watchdog (was orchestrator/Sentinel)
- Direct routing: B → arki → specialists (no middleman)
- All agents report to arki-whatsapp, not main-agent

## Security Incident (2026-02-10)
- Kraken API credentials exposed in git backup (commit 76ea38e)
- File: `workspace-hawkeye/scripts/kraken_balance.py` committed with real keys
- **ACTION REQUIRED:** Delete old repo: https://github.com/SayedB313/openclaw-backup/settings
- Fresh repo created: https://github.com/SayedB313/openclaw-backup-v2

## Infrastructure
- Server: 100.76.178.67 (Hetzner, Tailscale)
- Gateway: 127.0.0.1:18789 (systemd user service)
- Skills: clickup-mcp, twitter-x, email-himalaya (all agents)
- Session rotation: 3am daily (archives >1MB or >300 msgs)
- **Backups now push to: openclaw-backup-v2**

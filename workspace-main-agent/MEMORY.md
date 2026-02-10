# MEMORY.md — Long-Term Memory

## About B (My Human)
- Discord: sbw313 (ID: 1128731352817221642)
- WhatsApp: +14164001922
- Timezone: America/Toronto (EST)
- Values: Sharia compliance in trading, efficiency, self-sufficiency from AI
- Style: Direct, expects things done without asking, moves fast
- Projects: OpenClaw multi-agent system, trading (gold/silver/crypto), Oumafy, Arki, ILM

## System Architecture
- 9 agents across Discord + WhatsApp
- ClickUp workspace ID: 9013663000 (Spaces: ILM, Oumafy, Arki, Mind/Health, Health & Everything Else)
- GitHub backup: SayedB313/openclaw-backup (daily 11PM EST)
- Server: OP3 (Hetzner), Tailscale 100.76.178.67, passwordless sudo

## Model Strategy (Feb 8, 2026)
- **Paid (Codex)**: main-agent, conductor, engineer
- **Free**: research-trader (Grok), deep-research (Gem3Pro), research-assistant/marketing/trader-exec (Gem3Flash), arki (MiniMax)
- **Opus**: removed from all agents and fallback chain
- **Fallbacks**: Gemini Flash → MiniMax → Grok

## Credentials & Services
- Email: mrandaclient2024@gmail.com (Himalaya CLI, app password)
- Twitter/X: @Arki_OP3 (same email)
- ProxyEmpire: residential proxy for X scraping (100MB trial)
- All creds in /home/openclaw/.secrets/

## Key Lessons
- MiniMax OAuth doesn't work in isolated cron sessions — use other models
- X/Twitter blocks: datacenter IPs, twikit library, headless shell. Only puppeteer+stealth+residential proxy works
- `agents.defaults` schema doesn't include `skills` — must set per-agent
- `sessions_send` needs full session key, not label
- Cron jobs run under creating agent — use heartbeat for agent-specific proactive behavior
- Never ask B to run commands — fix everything yourself
- Don't push secrets to git — .gitignore covers .secrets/, openclaw.json, models.json

## Watchlist
- @LaylaEleira (Mishi McDuff) — OpenClaw power user, trading content, competitive intel

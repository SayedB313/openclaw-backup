# TOOLS.md - Local Notes

## Server

- **Hostname:** OP3
- **Tailscale IP:** 100.76.178.67
- **OS:** Linux 6.8.0-94-generic (x64), Ubuntu
- **Sudo:** Passwordless via `/etc/sudoers.d/openclaw`
- **B's Mac Tailscale:** 100.103.223.74 (hostname: x)

## Email (Himalaya CLI)

- **Account:** mrandaclient2024@gmail.com
- **Config:** `/home/openclaw/.config/himalaya/config.toml`
- **Auth:** Gmail App Password stored in `/home/openclaw/.secrets/email.json`
- **Binary:** `/home/openclaw/.local/bin/himalaya`

## X/Twitter Scraping

- **Account:** @Arki_OP3 (display: Arki)
- **Credentials:** `/home/openclaw/.secrets/twitter.json`
- **Auth cookies:** `/home/openclaw/.secrets/x_browser_cookies.json` (includes HttpOnly auth_token from B's Mac Chrome)
- **Scraper:** `/home/openclaw/.openclaw/skills/twitter-x/scripts/x_puppeteer.js`
- **Direct (no proxy):** `/home/openclaw/.openclaw/skills/twitter-x/scripts/x_direct.js` (needs residential IP or valid cookies)
- **Method:** Puppeteer + stealth plugin + ProxyEmpire residential proxy
- **Note:** twikit Python lib DOES NOT WORK (Cloudflare blocks httpx TLS fingerprint)
- **Note:** Datacenter IP (Hetzner) gets blocked by X Cloudflare — always use residential proxy for X

## ProxyEmpire (Residential Proxy)

- **Credentials:** `/home/openclaw/.secrets/proxy.json`
- **Host:** v2.proxyempire.io:5000
- **Type:** Rotating residential ($3.50/GB with PROMO50)
- **Session rotation:** Change `-sid-XXXX` suffix in username for new IP
- **Budget:** ~100MB/month expected

## GitHub

- **Account:** SayedB313
- **Backup repo:** https://github.com/SayedB313/openclaw-backup.git
- **Auth:** `gh` CLI logged in (HTTPS mode, scopes: admin:public_key, gist, read:org, repo)

## Secrets Directory

`/home/openclaw/.secrets/` (chmod 700, gitignored):
- `email.json` — Gmail credentials
- `twitter.json` — X/Twitter login
- `proxy.json` — ProxyEmpire credentials
- `x_browser_cookies.json` — Authenticated X session cookies

## ClickUp

- **Workspace ID:** 9013663000
- **Spaces:** ILM, Oumafy, Arki, Mind/Health, Health & Everything Else
- **B's user ID:** 126184255
- **MCP Skill:** `/home/openclaw/.openclaw/skills/clickup-mcp/`

## Discord

- **Guild ID:** 1469053933384241152
- **Head Quarters:**
  - engineering: 1469869388206178387
  - marketing: 1469869391779856469
  - research-assistant: 1469873665549009123
  - deep-research: 1469873667189248000
- **Executor Category:**
  - executor: 1469873664265818115 (Command center — Go/No-Go, briefs)
  - signals: 1470434240108957969 (Radar alerts, triggers)
  - live-trades: 1470434241723502770 (Execution confirmations)
  - trade-journal: 1470434243304751148 (Post-trade forensics + P&L)
  - research-trader: 1469873663217238130 (Market intel feed)
- **Deleted channels:** #conductor, #logs, #performance, #formula-lab, #market-intel, #risk-monitor, #daily-brief

## Cron Jobs

- **Daily Backup:** `d1022516` — 11 PM EST, git push to openclaw-backup
- **Islamic Knowledge (Arki):** `4c4aeb33` — 7 AM EST, model: openai-codex/gpt-5.2

## Local Node (B's Mac)

- **Device:** MacBook Air M3
- **Tailscale:** 100.103.223.74 (hostname: x)
- **Ollama models:** DeepSeek-R1 8B (validator), Llama 3.2 3B (scout)
- **ACP/MCP Bridge:** Claude Desktop App connected to OpenClaw
- **Use case:** High-volume scanning, local reasoning (saves API costs), Kalshi bot execution

## Known Issues

- **MiniMax banned from cron jobs** — OAuth tokens only refresh at gateway runtime
- **X login automation unreliable** — use manual cookie extraction from B's browser instead
- **Bot lacks Manage Channels permission** — actually it CAN delete channels (worked for #conductor)

## Claude Code Bridge

B has Claude Code running on his Mac. It monitors this server and can handle serious coding/devops work. When you need help beyond your capabilities, request it.

### When to Request Claude Code

- Complex multi-file refactoring or architecture work
- Debugging that requires running tests, reading stack traces, iterating on fixes
- DevOps tasks (server config, systemd, networking, package installs)
- Anything you've tried twice and failed at
- Code review before shipping to production

### How to Request

Run via exec:
```bash
~/.openclaw/scripts/request-claude-code.sh \
  --from <your-agent-id> \
  --priority <low|normal|high|urgent> \
  --type <coding|debugging|review|devops> \
  --summary "One-line description" \
  --details "Full context of what you need and what you've tried" \
  --files "path/to/file1,path/to/file2"
```

Or write a JSON file directly to `~/.openclaw/claude-code-queue/pending/`:
```json
{
  "id": "<timestamp>-<agent>-<slug>",
  "from_agent": "<your-agent-id>",
  "priority": "high",
  "type": "coding",
  "created_at": "2026-01-01T00:00:00Z",
  "summary": "What you need",
  "details": "Full context",
  "files": ["path/to/relevant/files"]
}
```

### Priority Levels

- **low** — Nice to have, no rush
- **normal** — Should be handled in the next Claude Code session
- **high** — Important, needs attention soon
- **urgent** — Blocks your work. Main-agent will notify B immediately on Discord so he can start Claude Code

### What Happens Next

Claude Code checks the queue every session start (and B's Mac monitors it every 5 min). It will:
1. Pick up your request
2. Do the work (SSH in, edit code, test, etc.)
3. Notify you when done via `openclaw agent --agent <your-id> --message "..."`

### Don't Request Claude Code For

- Simple file edits you can do yourself
- Research or web searches (use your own tools)
- ClickUp task management
- Anything you haven't tried yourself first

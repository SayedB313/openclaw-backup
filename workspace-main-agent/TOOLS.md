# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

### Email
- Provider: Gmail via Himalaya CLI
- Account: mrandaclient2024@gmail.com
- Binary: /home/openclaw/.local/bin/himalaya
- Config: /home/openclaw/.config/himalaya/config.toml
- **Status: Needs Gmail App Password** — regular password blocked by Google. Generate at https://myaccount.google.com/apppasswords

### Twitter/X
- Account: @Arki_OP3
- Email: mrandaclient2024@gmail.com
- Credentials: /home/openclaw/.secrets/twitter.json
- **Access method: xAI Grok API** (native X search) — no browser/scraping needed
- Use `web_search("site:x.com <query>")` or route to Grok model

### Secrets
- All credentials stored in `/home/openclaw/.secrets/` (chmod 700, gitignored)
- Never commit secrets to git

Add whatever helps you do your job. This is your cheat sheet.

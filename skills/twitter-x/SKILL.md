---
name: twitter-x
description: Search and monitor Twitter/X for real-time data, news, trading signals, and market analysis using both authenticated Puppeteer scraping and native X API v2.
---

# Twitter/X Intelligence Skill (v2.0)

This skill provides all agents with the ability to research X (Twitter) using two redundant methods:
1. **Puppeteer + Residential Proxy:** High-fidelity scraping of profiles and specific tweets (using @Arki_OP3).
2. **Native X API v2:** Fast, programmatic access to search and account data (authenticated as oumafy).

## 🛠 Features
- **Stealth Scrape:** Evades detection via `puppeteer-extra-plugin-stealth` + **ProxyEmpire** residential IPs.
- **Native API:** Uses X API v2 (oumafy developer account) for reliable data retrieval.
- **Profile:** Managed through `@Arki_OP3` account.
- **Resilient:** Multi-mode fallback ensuring data delivery.

## 🚀 How to Use (Any Agent)

### 1. Scrape a Profile (Puppeteer)
```bash
node /home/openclaw/.openclaw/skills/twitter-x/scripts/x_puppeteer.js profile LaylaEleira
```

### 2. Search X (API v2)
Best for broad market sentiment or finding specific mentions of keywords.
```bash
# Handled automatically via skill logic or custom scripts in /scripts/
```

## 📂 Configuration & Secrets
All credentials are in `/home/openclaw/.secrets/`:
- `x_api.json`: Native API v2 Keys (Bearer, Consumer, Access).
- `twitter.json`: @Arki_OP3 account credentials.
- `proxy.json`: ProxyEmpire residential proxy creds.

---
**Verified Working Date:** 2026-02-08
**Status:** Unified Intelligence - Deployed to all agents.

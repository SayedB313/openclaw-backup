# Private Skills Directory

**Location:** `/home/openclaw/.openclaw/workspace/skills/private/`

Shared skills accessible to all agents in the ecosystem.

## Purpose

- Custom, private skills not in the public skill library
- Skills created for specific workflows
- Skills in development/testing

## Available Skills

| Skill | Description | Status |
|-------|-------------|--------|
| `clickup-docs-bridge` | Create, update, get, search ClickUp Docs | ✅ Ready |
| `clickup` | ClickUp MCP proxy server (Phase 1) | ✅ Built |
| `prompt-mastery` | Prompt engineering mastery framework | 📋 Pending |

## Structure

```
private/
├── README.md
├── clickup/
│   └── SKILL.md              (MCP proxy setup)
├── clickup-docs-bridge/
│   └── SKILL.md              (Doc commands)
└── prompt-mastery/
    └── SKILL.md (pending)
```

## Quick Start

### ClickUp MCP Proxy (Required First)

```bash
cd /home/openclaw/services/clickup-mcp-proxy
npm install
node server.js
# Follow OAuth URL on first run
```

### ClickUp Docs Bridge

Available commands after proxy is running:
- `/clickup_doc_create`
- `/clickup_doc_update`
- `/clickup_doc_get`
- `/clickup_doc_search`

## Architecture

```
OpenClaw Agents
       │
       ▼ (shared skill)
┌──────────────────────┐
│ clickup-docs-bridge  │
│ (skill)              │
└──────────┬───────────┘
           │ HTTP POST to localhost:3000
           ▼
┌──────────────────────┐
│ ClickUp MCP Proxy    │
│ server.js            │
└──────────┬───────────┘
           │ OAuth
           ▼
┌──────────────────────┐
│ ClickUp MCP         │
│ https://mcp.clickup.com/mcp │
└──────────────────────┘
```

## Usage

All agents can use these commands. The proxy enforces access rules.

```bash
# From any agent channel
/clickup_doc_create parent_id="123" title="Test Doc" content="# Hello"
/clickup_doc_search query="strategy"
```

## Adding a New Skill

1. Create directory: `mkdir /home/openclaw/.openclaw/workspace/skills/private/[skill-name]`
2. Add `SKILL.md` following OpenClaw skill format
3. Update this README with skill details

---

Created: 2026-02-07

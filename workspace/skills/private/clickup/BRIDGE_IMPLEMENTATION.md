# ClickUp MCP Bridge Implementation Plan

**Status:** Planning
**Date:** 2026-02-07

---

## Architecture

```
OP3 (local server)
├── clickup-mcp-proxy (HTTP server on 127.0.0.1)
│   ├── OAuth flow with ClickUp MCP
│   └── Expose MCP tools to OpenClaw agents
│
├── OpenClaw agents
│   ├── Operator (Main Agent)
│   ├── Conductor (Orchestrator)
│   ├── Builder
│   ├── Research
│   └── Marketing
│
└── ClickUp (cloud)
    └── MCP Server (OAuth protected)
```

---

## Components to Build

### 1. clickup-mcp-proxy

**Location:** `/home/openclaw/.openclaw/services/clickup-mcp-proxy/`

**Files:**
- `server.js` - HTTP server
- `config.json` - Settings
- `package.json` - Dependencies
- `systemd/clickup-mcp-proxy.service` - Auto-start

**Capabilities:**
- Connect to ClickUp MCP via OAuth
- Expose HTTP endpoints for OpenClaw agents
- Handle authentication/refresh tokens
- Rate limiting

### 2. OpenClaw Bridge Skill

**Location:** `/home/openclaw/.openclaw/workspace/skills/private/clickup/SKILL.md`

**Tools:**
- `clickup_bridge_create_task()`
- `clickup_bridge_get_tasks()`
- `clickup_bridge_update_task()`
- `clickup_bridge_search_docs()`
- `clickup_bridge_create_doc()`

---

## Access Rules

### Who Can Access

| Agent | Access Level |
|-------|-------------|
| Operator (Main) | Full (Read/Write) |
| Conductor | Full (Read/Write) |
| Builder | Tasks only |
| Research | Read only |
| Marketing | Read/Write (Marketing lists) |

### Security

- Local-only (127.0.0.1)
- No external network access
- Token stored in OpenClaw credentials

---

## Implementation Phases

### Phase 1: Build the Proxy Server
- Set up Node.js HTTP server
- Implement OAuth flow with ClickUp MCP
- Expose REST API endpoints

### Phase 2: Create OpenClaw Bridge Skill
- Write skill definition
- Implement tool wrappers
- Test with Operator agent

### Phase 3: Deploy & Configure
- Create systemd service
- Configure auto-start
- Test end-to-end

---

## Next Steps

1. User approves this plan
2. I build the proxy server
3. Set up OAuth authentication
4. Create OpenClaw bridge skill
5. Deploy and test

---

**Awaiting user approval to proceed.**

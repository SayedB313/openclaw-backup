---
name: clickup-docs-bridge
description: Create, update, get, and search ClickUp Docs via local MCP proxy.
---

# ClickUp Docs Bridge Skill

**Shared skill** — available to all OpenClaw agents.

## Quick Start

```bash
# Ensure MCP proxy is running
cd /home/openclaw/services/clickup-mcp-proxy
node server.js
```

## Commands

| Command | Description |
|---------|-------------|
| `/clickup_doc_create` | Create a new doc |
| `/clickup_doc_update` | Update existing doc content |
| `/clickup_doc_get` | Get doc content by ID |
| `/clickup_doc_search` | Search docs by query |

## Usage

### /clickup_doc_create

Create a new document in ClickUp.

**Arguments:**
- `parent_id` (optional): Folder or doc ID to parent under
- `title` (required): Document title
- `content` (optional): Initial markdown content

**Example:**
```
/clickup_doc_create parent_id="123" title="90-Day Plan" content="# Goals\n\n- Goal 1\n- Goal 2"
```

### /clickup_doc_update

Update an existing document (append or replace).

**Arguments:**
- `doc_id` (required): Document ID
- `content` (required): New content to add
- `append` (optional, default: false): true = add to end, false = replace

**Example:**
```
/clickup_doc_update doc_id="456" content="\n\n## Updated section" append=true
```

### /clickup_doc_get

Get the full content of a document.

**Arguments:**
- `doc_id` (required): Document ID

**Example:**
```
/clickup_doc_get doc_id="456"
```

### /clickup_doc_search

Search documents by query string.

**Arguments:**
- `query` (required): Search terms
- `limit` (optional, default: 10): Max results

**Example:**
```
/clickup_doc_search query="risk rules"
```

## Implementation

Under the hood, these commands HTTP POST to the local MCP proxy:

```javascript
const PROXY_URL = 'http://127.0.0.1:3000';

// Create doc
fetch(`${PROXY_URL}/docs/create`, {
    method: 'POST',
    body: JSON.stringify({ parent_id, title, content })
});

// Update doc
fetch(`${PROXY_URL}/docs/update`, {
    method: 'POST',
    body: JSON.stringify({ doc_id, content, append })
});

// Get doc
fetch(`${PROXY_URL}/docs/get`, {
    method: 'POST',
    body: JSON.stringify({ doc_id })
});

// Search docs
fetch(`${PROXY_URL}/docs/search`, {
    method: 'POST',
    body: JSON.stringify({ query })
});
```

## Access Rules

| Agent | Access |
|-------|--------|
| Operator | Full (Read/Write) |
| Strategist | Full (Read/Write) |
| Coding | Write (Docs) |
| Marketing | Write (Docs) |
| Systems | Full (Read/Write) |
| Research | Read-only |
| Others | Read-only |

## Error Handling

- **401 Unauthorized**: Re-run OAuth setup
- **404 Not Found**: Check doc_id/folder_id exists
- **429 Rate Limited**: Wait 30s and retry
- **500 Error**: Check MCP proxy is running

## Examples

### Create a strategy doc

```
/clickup_doc_create parent_id="hq-folder" title="Q1 2026 Strategy" content="# Q1 Objectives\n\n## Month 1\n- [ ] Launch MCP proxy\n- [ ] Wire skills\n\n## Month 2\n- [ ] Test end-to-end\n- [ ] Document learnings"
```

### Search for existing docs

```
/clickup_doc_search query="outbound system"
```

### Update with findings

```
/clickup_doc_update doc_id="789" content="\n## Research Findings\n\n- Competitor X uses..." append=true
```

---

Created: 2026-02-07

---
name: clickup
description: Interact with ClickUp workspace via MCP. Create tasks, lists, docs, update statuses, and manage projects.
---

# ClickUp Skill

Interact with ClickUp via the local MCP proxy server.

## Quick Start

```bash
# Start the proxy server
cd /home/openclaw/services/clickup-mcp-proxy
npm install
node server.js

# Follow OAuth URL on first run
```

## Architecture

```
OpenClaw Agents → localhost:3000 → ClickUp MCP → ClickUp API
```

## Capabilities

### Via Local Proxy (port 3000)

| Capability | Endpoint | Method |
|------------|----------|--------|
| List tools | `/tools` | GET |
| Create doc | `/docs/create` | POST |
| Update doc | `/docs/update` | POST |
| Get doc | `/docs/get` | POST |
| Search docs | `/docs/search` | POST |
| Create task | `/tasks/create` | POST |
| Update task | `/tasks/update` | POST |
| Generic MCP call | `/mcp/call` | POST |

## Configuration

### For OpenClaw Agents

Add to your skill or tool wrapper:

```javascript
const CLICKUP_PROXY = 'http://127.0.0.1:3000';

// Example: Create a task
async function createTask(listId, name, priority = '1') {
    const response = await fetch(`${CLICKUP_PROXY}/tasks/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ list_id: listId, name, priority })
    });
    return response.json();
}
```

### Authentication (First Run)

1. Start: `node server.js`
2. Server outputs OAuth URL
3. Open URL in browser
4. Authorize
5. Restart server (tokens auto-saved)

## Usage Patterns

### Task Creation Template

```markdown
When creating tasks:
1. Include clear objective (what)
2. Define deliverables (checklist items)
3. Set assignee (agent name or human)
4. Add due date when relevant
5. Link to related docs/tasks
6. Set appropriate priority
```

### Status Workflow

```markdown
Common status flow:
→ New → In Progress → Review → Done
Or: Backlog → This Week → Blockers → Done
```

### Best Practices

- Use docs for canonical content (strategies, PRDs)
- Use tasks for execution units
- Link tasks to docs (not copy content)
- Keep checklists actionable
- Use consistent naming (Project-Number format)

## ARKI Space Structure

As configured for B's system:

```
ARKI (Space)
├── HQ (Folder)
│   ├── Backlog
│   ├── This Week
│   ├── Decisions
│   └── Blockers
├── Marketing Engine (Folder)
│   ├── Outbound
│   ├── UGC Content
│   └── Creative Pipeline
├── Product & Engineering (Folder)
│   ├── Product
│   ├── Engineering
│   └── Bugs
└── TheMuslimTake (Folder)
    ├── Guests
    ├── Episodes
    └── Production
```

## Example Commands

```markdown
# Create a task
"Create task: Build landing page in Marketing/Outbound, due Friday, priority high"

# Update status
"Move task GROWTH-123 to Done"

# Get pending tasks
"Show me all tasks in This Week list"

# Create doc section
"Add 'Niche Strategy' section to Marketing/Outbound doc"
```

## Error Handling

- 401: Re-authenticate (token expired)
- 403: Check workspace permissions
- 404: Verify list/task IDs exist
- Rate limits: Wait and retry

---
name: clickup-mcp
description: Interact with ClickUp via MCP server. Search tasks, create/update tasks, manage lists/folders/docs, track time, send chat messages, and browse workspace hierarchy. Use when the user asks about ClickUp tasks, projects, to-dos, time tracking, ClickUp docs, or workspace organization. Triggers on mentions of ClickUp, tasks, project management, to-do lists, sprints, or any reference to spaces/lists/folders in the project management context.
---

# ClickUp MCP Skill

## How It Works

Call the wrapper script to execute any ClickUp MCP tool:

```bash
python3 SKILL_DIR/scripts/clickup_mcp.py <tool_name> '<json_arguments>'
```

The script handles OAuth token discovery, MCP protocol, and response parsing automatically.

## Quick Examples

```bash
# Search for anything
python3 SKILL_DIR/scripts/clickup_mcp.py clickup_search '{"keywords":"oumafy"}'

# Get workspace tree
python3 SKILL_DIR/scripts/clickup_mcp.py clickup_get_workspace_hierarchy

# Create a task
python3 SKILL_DIR/scripts/clickup_mcp.py clickup_create_task '{"name":"New task","list_id":"901325203728"}'

# Get task details (supports custom IDs like DEV-1234)
python3 SKILL_DIR/scripts/clickup_mcp.py clickup_get_task '{"task_id":"abc123"}'

# Update task status
python3 SKILL_DIR/scripts/clickup_mcp.py clickup_update_task '{"task_id":"abc123","status":"in progress"}'
```

## Tool Reference

For complete tool catalog (27 tools), parameters, and workspace IDs:
→ Read `references/tools.md`

## Common Workflows

### Find then act
1. `clickup_search` with keywords to find task IDs
2. `clickup_get_task` for details
3. `clickup_update_task` / `clickup_create_task_comment` to modify

### Create task in known list
1. `clickup_create_task` with `name` + `list_id` (see references/tools.md for key IDs)

### Browse workspace structure
1. `clickup_get_workspace_hierarchy` — returns full space→folder→list tree

## Auth

Token auto-discovered from `~/.mcp-auth/`. If missing, user must run:
```bash
npx mcp-remote https://mcp.clickup.com/mcp
```
and complete OAuth in browser.

## Notes

- `workspace_id` is auto-populated on all calls — omit it unless overriding
- Date format: `YYYY-MM-DD` or `YYYY-MM-DD HH:MM` (user timezone)
- Custom task IDs (e.g. `DEV-1234`) work wherever `task_id` is accepted
- Search returns paginated results — use `cursor` for next page
- Resolve `SKILL_DIR` to the absolute path of this skill's directory

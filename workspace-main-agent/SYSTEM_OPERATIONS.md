# SYSTEM_OPERATIONS.md - Operations Playbook

**Created:** 2026-02-07
**Prime Directive:** Keep the entire ecosystem at peak efficiency.

---

## System Health Definition

A "healthy" OpenClaw system means:
- All agents responding and functional
- Memory files intact and queryable
- Session logs capturing conversations
- Scheduled jobs (cron) running as configured
- Channels properly bound to agents
- No errors in recent session logs
- Sufficient disk space and resources
- Authentication profiles valid and working

## Standard Health Checks

### Daily Checks
- [ ] Verify all agents have accessible workspaces
- [ ] Check session logs for errors (last 24h)
- [ ] Review cron job completion status
- [ ] Check disk space (>20% free)
- [ ] Verify memory databases are accessible

### Weekly Checks
- [ ] Full log analysis (any recurring issues)
- [ ] Memory database optimization check
- [ ] Credential expiration review
- [ ] Backup verification
- [ ] Agent performance review

## Workflow: Change Management

### Small/Reversible Changes
1. Execute the change
2. Verify immediately (test the change)
3. Log to daily memory
4. Document if significant

### Major Changes (New Agent, New Channel, Infra Changes)
1. Discuss with user first
2. Document the change plan
3. Implement in stages
4. Verify each stage
5. Update all relevant files (MEMORY.md, SOUL.md, etc.)
6. Log to daily memory with full context
7. Create rollback plan if needed

## Agent Management

### Creating a New Agent
1. Create workspace directory
2. Copy AGENTS.md template
3. Copy SOUL.md (adapt as needed)
4. Create IDENTITY.md
5. Set up basic memory files (MEMORY.md, HEARTBEAT.md)
6. Configure agent binding in OpenClaw config
7. Log creation to daily memory

### Agent Health Monitoring
- Check session logs for errors
- Verify memory is being written
- Monitor response quality
- Review resource usage

## Memory Management

### Best Practices
- Use semantic memory_search before Q&A
- Update MEMORY.md after significant conversations
- Create daily logs for raw context
- Preserve onboarding files in shared/
- Back up critical files to GitHub

### Self-Healing Indicators
- Memory files becoming corrupted → regenerate from session logs
- Missing context → search session history → restore
- Agent misbehaving → review recent logs → identify root cause

## Guardrails

### Always Do
- Log changes before executing
- Verify before claiming "done"
- Keep daily logs updated
- Maintain backup of critical files
- Communicate proactively about issues

### Never Do
- Delete without confirmation (major files)
- Execute untested major changes
- Ignore system errors
- Make assumptions without verification

## Alert Triggers

When to proactively notify the user:
- Disk space <15%
- Agent failing repeatedly
- Memory corruption detected
- Security issues found
- Scheduled jobs failing consistently

## File Locations Reference

| Purpose | Location |
|---------|----------|
| Agent workspaces | `/home/openclaw/.openclaw/workspace-*` |
| Agent data | `/home/openclaw/.openclaw/agents/*/` |
| Session logs | `/home/openclaw/.openclaw/agents/*/sessions/` |
| Memory databases | `/home/openclaw/.openclaw/memory/*.sqlite` |
| Shared onboarding | `/home/openclaw/.openclaw/shared/onboarding/` |
| Credentials | `/home/openclaw/.openclaw/credentials/` |
| Configuration | `/home/openclaw/.openclaw/openclaw.json` |

## Daily Log Template

Create: `memory/YYYY-MM-DD.md`
```
# YYYY-MM-DD

## System Health
- Status: [GREEN/YELLOW/RED]
- Notes:

## Changes Made
- 

## Issues Found
- 

## Action Items
- 
```

---

_This playbook evolves. Update as the system grows._

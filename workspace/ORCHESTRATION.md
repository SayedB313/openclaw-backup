# ORCHESTRATION.md — Multi-Agent Workflow & ClickUp Integration

**Last Updated:** 2026-02-07
**Owner:** Main Agent (System Operator)

---

## The Flow (End to End)

```
B (WhatsApp)
  → Arki (WhatsApp assistant — daily companion)
    → "I have an idea / need something done"
      → Arki sends to Conductor via sessions_send

Conductor receives intake:
  1. Analyzes scope → breaks into tasks
  2. Creates ClickUp task(s) in the right folder/list
  3. Dispatches to specialist(s) via sessions_send
  4. Tracks progress across agents

Specialist receives dispatch:
  1. Updates ClickUp task → "in progress"
  2. Does the work (code, research, analysis, strategy)
  3. Updates ClickUp task → "done" + attaches deliverables
  4. Reports back to Conductor via sessions_send (with prefix)

Conductor receives completion:
  1. Reviews deliverable quality
  2. If more work needed → dispatches next task
  3. If multi-step → chains next specialist
  4. When ALL done → notifies B via WhatsApp (done or blocked only)
```

---

## What ClickUp Is For

**ClickUp is the single source of truth.** It serves three purposes:

1. **Task Registry** — If it's not in ClickUp, it doesn't exist. Every dispatched task gets a ClickUp task with clear title, description, and assignee.

2. **Status Dashboard** — B can open ClickUp anytime and see: what's active, what's done, what's blocked. No need to ask any agent "what are you doing?"

3. **Audit Trail** — Every task has history: who created it, who worked on it, what comments were made, what the outcome was. This prevents work from getting lost in Discord messages.

**ClickUp is NOT for:**
- Real-time chat between agents (that's Discord/sessions_send)
- Storing code (that's GitHub)
- Personal reminders for B (that's Arki/Main Agent)

---

## ClickUp Structure

```
ARKI Space (901313151685)
├── Conductor Folder (901316981511)
│   ├── Strategic Priorities (901325240513)  ← high-level goals from B
│   └── Agent Operations (901325240514)      ← system health, agent issues
│
├── Engineering Folder (901316981508)        ← (CORRECTION: verify ID)
│   ├── Active Sprints (901325240499)        ← current sprint tasks
│   └── Backlog (901325240501)               ← future engineering work
│
├── Research Folder (901316981508)           ← (CORRECTION: verify ID)
│   ├── Active Research (901325240502)       ← in-flight research
│   └── Research Backlog (901325240503)      ← queued research topics
│
├── Marketing Folder (901316981509)
│   ├── Campaigns (901325240505)             ← active campaigns
│   └── Content Calendar (901325240507)      ← planned content
│
└── Trading Folder (901316981510)
    ├── Trade Ideas (901325240508)           ← research trader ideas
    ├── Open Positions (901325240510)        ← active trades
    └── Trade Log (901325240512)             ← closed trade history
```

---

## Conductor Routing Logic

When Conductor receives a task, it decides WHO does it based on the domain:

| Signal | Route To | Prefix |
|--------|----------|--------|
| Build, code, fix, deploy, repo, API, debug | **Engineer** | ENG: |
| Quick lookup, data, fact-check, brainstorm | **Research Assistant** | RES: |
| Deep analysis, multi-source, synthesis, report | **Deep Research** | RES: (DEEP) |
| Marketing, content, campaign, brand, growth, B2C | **Marketing** | MKT: |
| Market scan, trade idea, opportunity, macro | **Research Trader** | TRADE-R: |
| Execute trade, portfolio, position mgmt, stop loss | **Trader Execution** | TRADE-X: |

**Multi-domain tasks:** Conductor breaks them into sub-tasks and dispatches in parallel or sequence:
- Example: "Build a landing page for Oumafy launch"
  1. MKT: Marketing writes the copy and specs the page
  2. ENG: Engineer builds it from Marketing's spec
  3. RES: Research provides competitor examples (parallel with step 1)

**Escalation:** If a specialist is blocked, they report to Conductor. Conductor either:
- Resolves it (reassigns, provides info)
- Escalates to B (only if B's input is truly needed)

---

## How Agents Communicate

### Primary: `sessions_send`

Agents communicate via OpenClaw's `sessions_send` tool:

```
sessions_send(label="conductor", message="ENG: Landing Page — DONE\n\nDeliverable: ...")
sessions_send(label="engineer", message="ORCH: Build landing page\n\nContext: ...")
```

- **Conductor → Specialist:** Uses `sessions_send(label="<agent-id>", message="ORCH: ...")`
- **Specialist → Conductor:** Uses `sessions_send(label="conductor", message="<PREFIX>: ...")`
- **Arki → Conductor:** Uses `sessions_send(label="conductor", message="...")`
- **Conductor → B (WhatsApp):** Uses `sessions_send(label="main-agent", message="...")` or message tool

### Secondary: Discord channels

Each agent has a Discord channel where messages are also visible. This gives B a readable log. But the primary dispatch mechanism is `sessions_send`.

### Message Prefixes

| Agent | Prefix | Example |
|-------|--------|---------|
| Conductor | ORCH: | ORCH: [Agent] — [Task] |
| Engineer | ENG: | ENG: Landing Page — DONE |
| Research Assistant | RES: | RES: Competitor Analysis — DONE |
| Deep Research | RES: (DEEP) | RES: Market Sizing — DEEP ANALYSIS COMPLETE |
| Marketing | MKT: | MKT: Launch Campaign — DONE |
| Research Trader | TRADE-R: | TRADE-R: Gold Opportunity — IDEA |
| Trader Execution | TRADE-X: | TRADE-X: Buy Gold — EXECUTED |

---

## ClickUp Task Lifecycle

Every task follows this lifecycle:

```
[Conductor creates task]
     ↓
  STATUS: "to do"
     ↓
[Specialist picks up]
     ↓
  STATUS: "in progress"
     ↓
[Specialist completes work]
     ↓
  STATUS: "complete" (+ comment with deliverable)
     ↓
[Conductor reviews]
     ↓
  STATUS: "closed" (or back to "in progress" if revisions needed)
```

### ClickUp Task Format (Created by Conductor)

```
Name: [Clear, actionable title]
List: [Appropriate list ID]
Description:
  Dispatched by: Conductor
  Assigned to: [Agent name]
  Priority: [1-Urgent / 2-High / 3-Normal / 4-Low]
  
  ## Context
  [Why this task exists]
  
  ## Objective
  [What needs to be done]
  
  ## Acceptance Criteria
  [How we know it's done]
  
  ## Dependencies
  [Other tasks this depends on, or that depend on this]
Tags: [agent name, project name]
```

### How Agents Use ClickUp (The Commands)

All agents use the ClickUp MCP skill:

```bash
# Create a task (Conductor does this)
python3 ~/.openclaw/skills/clickup-mcp/scripts/clickup_mcp.py clickup_create_task \
  '{"name":"Build Oumafy landing page","list_id":"901325240499","description":"...","priority":2,"tags":["engineer","oumafy"]}'

# Update task status (any agent working on it)
python3 ~/.openclaw/skills/clickup-mcp/scripts/clickup_mcp.py clickup_update_task \
  '{"task_id":"TASK_ID","status":"in progress"}'

# Add a comment (deliverable, blocker, update)
python3 ~/.openclaw/skills/clickup-mcp/scripts/clickup_mcp.py clickup_create_task_comment \
  '{"task_id":"TASK_ID","comment_text":"ENG: Done. Code pushed to github.com/repo. PR #42."}'

# Search for tasks
python3 ~/.openclaw/skills/clickup-mcp/scripts/clickup_mcp.py clickup_search \
  '{"keywords":"landing page"}'

# Mark complete
python3 ~/.openclaw/skills/clickup-mcp/scripts/clickup_mcp.py clickup_update_task \
  '{"task_id":"TASK_ID","status":"complete"}'
```

---

## Engineer: Claude Code Integration

The Engineer agent uses **Claude Code** (already installed on server) for coding tasks:

```bash
# Engineer runs Claude Code for coding tasks
claude -p "Build a landing page with Next.js based on this spec: ..." --output-format stream-json

# Then pushes to GitHub
cd /path/to/repo
git add .
git commit -m "feat: Oumafy landing page"
git push origin main
```

All code lives in GitHub repos. Engineer commits, pushes, and reports the commit/PR link back to Conductor via ClickUp comment and sessions_send.

---

## Example: Full Orchestration Flow

**B on WhatsApp:** "I want a landing page for TheMuslimTake podcast — something that captures emails and shows episode highlights"

**Arki (WhatsApp):** Acknowledges, sends to Conductor:
```
sessions_send(label="conductor", message="B wants a landing page for TheMuslimTake podcast — email capture + episode highlights")
```

**Conductor:**
1. Creates ClickUp tasks:
   - `MKT: TheMuslimTake landing page copy & spec` → Campaigns list
   - `RES: Top 5 podcast landing page examples` → Active Research list
   - `ENG: Build TheMuslimTake landing page` → Active Sprints list (blocked on MKT)

2. Dispatches in parallel:
   ```
   sessions_send(label="research-assistant", message="ORCH: Research — Top 5 podcast landing pages\n\nFind 5 best podcast landing pages (especially Islamic/community content). For each: URL, what works, email capture approach. Deliver to #conductor with RES: prefix.")
   
   sessions_send(label="marketing", message="ORCH: Marketing — TheMuslimTake landing page spec\n\nWrite the copy and spec for a landing page: email capture + episode highlights. Research will provide examples. Deliver copy + wireframe spec to #conductor with MKT: prefix.")
   ```

3. Waits for both to complete.

**Research Assistant:** Searches, finds examples, reports back:
```
sessions_send(label="conductor", message="RES: Podcast Landing Pages — DONE\n\nTop 5 examples:\n1. ...\n2. ...\nClickUp task updated.")
```

**Marketing:** Writes copy and spec:
```
sessions_send(label="conductor", message="MKT: TheMuslimTake Landing Page — DONE\n\nCopy and wireframe spec attached to ClickUp task. Ready for Engineer.")
```

**Conductor:** Both done. Unblocks Engineer:
```
sessions_send(label="engineer", message="ORCH: Engineer — Build TheMuslimTake landing page\n\nSpec: [MKT deliverable]\nExamples: [RES deliverable]\nRepo: github.com/SayedB313/themuslimtake\nUse Claude Code. Push to repo. Report when done.")
```

**Engineer:** Builds it, pushes to GitHub:
```
sessions_send(label="conductor", message="ENG: TheMuslimTake Landing Page — DONE\n\nRepo: github.com/SayedB313/themuslimtake\nPR: #12\nLive preview: localhost:3000\nClickUp task updated.")
```

**Conductor:** Reviews, closes tasks, notifies B:
```
sessions_send(label="main-agent", message="Tell B on WhatsApp: TheMuslimTake landing page is done. Code is at github.com/SayedB313/themuslimtake PR #12. Marketing copy, research examples, and build all complete. ClickUp tasks closed.")
```

---

## Key Principles

1. **ClickUp is the paper trail.** Discord messages scroll away. ClickUp persists.
2. **Conductor is the brain.** No specialist talks directly to another specialist — everything routes through Conductor.
3. **B sees only outcomes.** Unless he asks for status or is needed for approval, he gets notified only when work is done or blocked.
4. **Small tasks, fast cycles.** Break big ideas into tasks that can be done in hours, not days. Ship early, iterate.
5. **Every task has an owner.** Every ClickUp task is tagged with the agent responsible.
6. **Prefixes are mandatory.** They make Discord channels scannable and let Conductor parse responses quickly.

# AGENTS.md — How AI Works For You

**Last Updated:** 2026-02-07

---

## Core Want

**A single orchestrator.** Not a tool zoo. One agent that coordinates everything A-Z. Talk to one, it handles the rest.

---

## Current Architecture

| Agent | Platform | Purpose | Model |
|-------|----------|---------|-------|
| systems-arki | Discord | Primary interface, orchestration | Codex 5.2 (default) |
| operator | Discord | Operator channel | Codex 5.2 |
| arki-whatsapp (Soul) | WhatsApp | Mobile-first assistant | MiniMax M2.1 |

---

## Task Routing

| Domain/Task | Assigned Model | Why | Fallback |
|-------------|----------------|-----|----------|
| Complex reasoning | Opus 4.5 | Best reasoning | Gemini 3 Pro |
| Fast iteration | Gemini 2.5 Flash Lite | Speed + cost | MiniMax M2.1 |
| Coding | Codex 5.2 | Best code generation | Opus 4.5 |
| Quick tasks | MiniMax M2.1 | Fast, cheap | Gemini Flash |
| Research | Perplexity | Web search built-in | Web search tools |

---

## Cost Routing

| Task Complexity | Routes To | Est. Cost/Use | Budget Guard |
|-----------------|-----------|---------------|--------------|
| Simple Q&A | MiniMax / Flash Lite | <$0.01 | None |
| Medium tasks | Codex / Gemini Pro | $0.05-0.20 | None |
| Complex reasoning | Opus 4.5 | $0.50-2.00 | Alert if >10/day |
| Heavy coding sessions | Codex | $1-5/session | Alert if >$20/day |

---

## Autonomy Levels

### Fully Automated (No Approval)

- File operations (read, write, edit)
- Code generation and debugging
- Research and information gathering
- ClickUp task creation and updates
- Calendar queries
- Web searches
- System maintenance
- Background organization
- Idea capture
- Project tracking updates

### Needs Approval

- **Any communication to humans** (emails, messages, posts, DMs)
- Publishing content publicly
- Financial transactions
- Account changes

### Never Without Explicit Instruction

- Outbound messages to people
- Deleting major files, repos, accounts
- Public posts on any platform
- Anything involving money

---

## Coordination Architecture

1. **Primary entry:** systems-arki (Discord) or Soul (WhatsApp)
2. **Sub-agents:** Spawn for long-running or parallel tasks
3. **Handoff:** If one model fails, fall back to next in chain
4. **Memory:** Shared workspace, memory files persist across sessions
5. **ClickUp:** Central hub for project state, accessible to all agents

---

## Future State (What B Wants)

One master orchestrator that:
- Receives high-level intent
- Breaks it into tasks
- Routes to appropriate models/tools
- Executes without hand-holding
- Reports back with results
- Proactively does things that impress

**Current gap:** Still requires manual bridging between systems. Not fully agentic yet.

---

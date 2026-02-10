# ORCHESTRATION.md — Fleet Dispatch Reference

**Updated:** 2026-02-10

## Flow

```
B (WhatsApp) → Arki (orchestrator) → Specialist → Arki → B
```

Arki receives requests, breaks them into tasks, creates ClickUp tasks, dispatches to the right specialist, and delivers results back to B.

## Dispatch Format

```
sessions_send(label="<agent-id>", message="ORCH: [Agent] — [Task Title]\n\nContext: ...\nObjective: ...\nConstraints: ...\nOutput: ...")
```

## Routing Table

| Request Type | Route To |
|-------------|----------|
| Build / code / fix / deploy | engineer |
| Quick lookup / fact check | research-assistant |
| Deep analysis / multi-source | deep-research |
| Marketing / content / social | marketing |
| Market scan / crypto analysis | hawkeye |
| Trade execution / orders | executor |

## Message Prefixes

- ORCH: — orchestration dispatch
- ENG: — engineering response
- RES: — research response
- MKT: — marketing response
- TRADE-R: — trading research
- TRADE-X: — trade execution

## Escalation

All agents escalate to arki-whatsapp. Systems issues go to main-agent (watchdog).

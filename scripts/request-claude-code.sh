#!/bin/bash
# request-claude-code.sh — Drop a help request for Claude Code
# Usage: request-claude-code.sh --from <agent> --priority <low|normal|high|urgent>
#        --type <coding|debugging|review|devops> --summary "..." [--details "..."] [--files "f1,f2"]

set -euo pipefail

FROM=""
PRIORITY="normal"
TYPE="coding"
SUMMARY=""
DETAILS=""
FILES=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --from) FROM="$2"; shift 2 ;;
    --priority) PRIORITY="$2"; shift 2 ;;
    --type) TYPE="$2"; shift 2 ;;
    --summary) SUMMARY="$2"; shift 2 ;;
    --details) DETAILS="$2"; shift 2 ;;
    --files) FILES="$2"; shift 2 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

if [ -z "$FROM" ] || [ -z "$SUMMARY" ]; then
  echo "Error: --from and --summary are required"
  echo "Usage: request-claude-code.sh --from <agent-id> --summary \"description\""
  exit 1
fi

TIMESTAMP=$(date +%s)
SLUG=$(echo "$SUMMARY" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd 'a-z0-9-' | head -c 40)
FILENAME="${TIMESTAMP}-${FROM}-${SLUG}.json"
QUEUE_DIR="$HOME/.openclaw/claude-code-queue/pending"

# Build files array
FILES_JSON="[]"
if [ -n "$FILES" ]; then
  FILES_JSON=$(echo "$FILES" | tr ',' '\n' | python3 -c "import sys,json; print(json.dumps([l.strip() for l in sys.stdin if l.strip()]))")
fi

cat > "${QUEUE_DIR}/${FILENAME}" << REQEOF
{
  "id": "${TIMESTAMP}-${FROM}-${SLUG}",
  "from_agent": "${FROM}",
  "priority": "${PRIORITY}",
  "type": "${TYPE}",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "summary": $(python3 -c "import json; print(json.dumps('''${SUMMARY}'''))"),
  "details": $(python3 -c "import json; print(json.dumps('''${DETAILS}'''))"),
  "files": ${FILES_JSON}
}
REQEOF

echo "Request queued: ${QUEUE_DIR}/${FILENAME}"

# If urgent, notify main-agent to alert B
if [ "$PRIORITY" = "urgent" ]; then
  openclaw agent --agent main-agent \
    --message "URGENT: Claude Code help requested by ${FROM}: ${SUMMARY}. Tell B on Discord immediately." \
    --json > /dev/null 2>&1 &
  echo "Urgent notification sent to main-agent"
fi

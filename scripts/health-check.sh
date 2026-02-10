#!/bin/bash
# health-check.sh — Write server health snapshot to JSON
# Runs via cron every 5 minutes

export XDG_RUNTIME_DIR="/run/user/$(id -u)"

OUT="$HOME/.openclaw/server-health.json"
QUEUE_DIR="$HOME/.openclaw/claude-code-queue/pending"
LOG_FILE="/tmp/openclaw/openclaw-$(date +%Y-%m-%d).log"

# Gather metrics
gateway_status=$(systemctl --user is-active openclaw-gateway 2>/dev/null || echo "unknown")
disk_pct=$(df / --output=pcent 2>/dev/null | tail -1 | tr -d ' %' || echo "0")
mem_total=$(free -m 2>/dev/null | awk '/Mem:/{print $2}' || echo "0")
mem_available=$(free -m 2>/dev/null | awk '/Mem:/{print $7}' || echo "0")
load=$(cat /proc/loadavg 2>/dev/null | awk '{print $1, $2, $3}' || echo "0 0 0")
uptime_s=$(awk '{print int($1)}' /proc/uptime 2>/dev/null || echo "0")
pending_requests=$(ls "$QUEUE_DIR" 2>/dev/null | wc -l)
log_errors=$(grep -cE 'ERROR|FATAL|error.*fatal|Unhandled' "$LOG_FILE" 2>/dev/null || echo "0")

# Check gateway port
gateway_port=$(ss -tlnp 2>/dev/null | grep -c ':18789' || echo "0")

# Build issues array
issues=""
[ "$gateway_status" != "active" ] && issues="${issues}\"gateway is ${gateway_status}\","
[ "$gateway_port" -eq 0 ] 2>/dev/null && issues="${issues}\"gateway port 18789 not listening\","
[ "${disk_pct:-0}" -gt 85 ] 2>/dev/null && issues="${issues}\"disk usage at ${disk_pct}%\","
[ "${mem_available:-0}" -lt 500 ] 2>/dev/null && issues="${issues}\"low memory: ${mem_available}MB available\","
[ "${log_errors:-0}" -gt 500 ] 2>/dev/null && issues="${issues}\"${log_errors} errors in today's log\","
[ "$pending_requests" -gt 0 ] && issues="${issues}\"${pending_requests} pending Claude Code request(s)\","

# Remove trailing comma
issues=$(echo "$issues" | sed 's/,$//')

cat > "$OUT" << EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "gateway": "$gateway_status",
  "gateway_port_listening": $([ "$gateway_port" -gt 0 ] && echo "true" || echo "false"),
  "disk_percent": ${disk_pct:-0},
  "mem_total_mb": ${mem_total:-0},
  "mem_available_mb": ${mem_available:-0},
  "load": "$load",
  "uptime_seconds": $uptime_s,
  "pending_claude_code_requests": $pending_requests,
  "log_errors_today": ${log_errors:-0},
  "issues": [${issues}]
}
EOF

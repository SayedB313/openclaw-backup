#!/usr/bin/env python3
"""ClickUp MCP wrapper — calls ClickUp's MCP server via StreamableHTTP.
Usage: clickup_mcp.py <tool_name> [json_arguments]
Example: clickup_mcp.py clickup_search '{"keywords":"oumafy"}'
"""
import json, os, sys, subprocess, glob

def get_token():
    token = os.environ.get("CLICKUP_MCP_TOKEN")
    if token:
        return token
    pattern = os.path.expanduser("~/.mcp-auth/**/*_tokens.json")
    files = glob.glob(pattern, recursive=True)
    if not files:
        print(json.dumps({"error": "No ClickUp MCP token. Run: npx mcp-remote https://mcp.clickup.com/mcp"}), file=sys.stderr)
        sys.exit(1)
    with open(files[0]) as f:
        return json.load(f)["access_token"]

def main():
    if len(sys.argv) < 2:
        print("Usage: clickup_mcp.py <tool_name> [json_arguments]")
        sys.exit(1)

    tool_name = sys.argv[1]
    arguments = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    token = get_token()
    url = os.environ.get("CLICKUP_MCP_URL", "https://mcp.clickup.com/mcp")

    payload = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": tool_name, "arguments": arguments}
    })

    result = subprocess.run([
        "curl", "-sf", "-X", "POST", url,
        "-H", "Content-Type: application/json",
        "-H", "Accept: application/json, text/event-stream",
        "-H", f"Authorization: Bearer {token}",
        "-d", payload
    ], capture_output=True, text=True, timeout=30)

    raw = result.stdout.strip()
    if not raw:
        print(json.dumps({"error": "Empty response from MCP server", "stderr": result.stderr[:200]}))
        sys.exit(1)

    # Parse SSE: find last "data: " line
    data_json = None
    for line in raw.split("\n"):
        line = line.strip()
        if line.startswith("data: "):
            data_json = line[6:]

    if not data_json:
        print(json.dumps({"error": "No data line", "raw": raw[:300]}))
        sys.exit(1)

    resp = json.loads(data_json)
    result_obj = resp.get("result", {})

    if result_obj.get("isError"):
        texts = [c.get("text", "") for c in result_obj.get("content", []) if c.get("type") == "text"]
        print(json.dumps({"error": " ".join(texts)}, indent=2))
        sys.exit(1)

    sc = result_obj.get("structuredContent")
    if sc:
        print(json.dumps(sc, indent=2))
    else:
        for item in result_obj.get("content", []):
            if item.get("type") == "text":
                try:
                    print(json.dumps(json.loads(item["text"]), indent=2))
                except (json.JSONDecodeError, ValueError):
                    print(item["text"])

if __name__ == "__main__":
    main()

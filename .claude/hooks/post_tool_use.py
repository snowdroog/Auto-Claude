#!/usr/bin/env python3
"""
PostToolUse Hook - Log tool usage and extract simple insights

This hook runs after each tool execution to:
- Log tool usage to audit file for analytics
- Extract simple insights (e.g., files modified, commands run)
- Provide contextual feedback for next steps

Note: Full insight extraction happens at session level in analysis/insight_extractor.py.
This hook provides lightweight, per-tool logging.

Exit codes:
  0 - Always (this is informational only)
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent))
from utils.logging import log_hook_execution, log_hook_result

def log_tool_execution(hook_input: dict, log_file: Path) -> None:
    """Log tool execution to audit file."""
    try:
        tool_name = hook_input.get("tool_name", "unknown")
        tool_input = hook_input.get("tool_input", {})
        tool_response = hook_input.get("tool_response", "")

        # Create log entry
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "tool_name": tool_name,
            "session_id": hook_input.get("session_id", "unknown"),
        }

        # Add relevant context based on tool type
        if tool_name == "Write":
            log_entry["file_path"] = tool_input.get("file_path", "")
            log_entry["action"] = "file_write"
        elif tool_name == "Edit":
            log_entry["file_path"] = tool_input.get("file_path", "")
            log_entry["action"] = "file_edit"
        elif tool_name == "Read":
            log_entry["file_path"] = tool_input.get("file_path", "")
            log_entry["action"] = "file_read"
        elif tool_name == "Bash":
            command = tool_input.get("command", "")
            # Truncate long commands
            log_entry["command"] = command[:200] if len(command) > 200 else command
            log_entry["action"] = "bash_command"
        elif tool_name.startswith("mcp__"):
            log_entry["action"] = "mcp_tool"
            log_entry["mcp_server"] = tool_name.split("__")[1] if "__" in tool_name else "unknown"
        else:
            log_entry["action"] = "other"

        # Append to log file
        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

    except Exception as e:
        # Don't fail the hook on logging errors
        pass

def extract_simple_insight(hook_input: dict) -> str:
    """Extract simple insight from tool execution for feedback."""
    tool_name = hook_input.get("tool_name", "unknown")
    tool_input = hook_input.get("tool_input", {})

    # Provide contextual feedback based on tool
    if tool_name == "Write":
        file_path = tool_input.get("file_path", "")
        return f"File created: {file_path}"
    elif tool_name == "Edit":
        file_path = tool_input.get("file_path", "")
        return f"File modified: {file_path}"
    elif tool_name == "Bash":
        command = tool_input.get("command", "")
        # Provide feedback for common commands
        if "pytest" in command or "npm test" in command:
            return "Tests executed - check results"
        elif "git commit" in command:
            return "Git commit created"
        elif "npm install" in command or "pip install" in command:
            return "Dependencies installed"
        else:
            return f"Command executed: {command[:50]}"
    elif tool_name.startswith("mcp__"):
        return f"MCP tool executed: {tool_name}"

    return ""

def main():
    """Main hook entry point."""
    # Read stdin for tool result
    try:
        hook_input = json.loads(sys.stdin.read())
    except json.JSONDecodeError:
        # Silently fail on parse errors
        sys.exit(0)
    except Exception:
        # Silently fail on any other errors
        sys.exit(0)

    # Log execution (using hook utils)
    logger = log_hook_execution("post_tool_use", hook_input)

    # Log to audit file
    cwd = hook_input.get("cwd", ".")
    log_file = Path(cwd) / ".auto-claude" / "tool-usage.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    log_tool_execution(hook_input, log_file)

    # Extract simple insight
    insight = extract_simple_insight(hook_input)

    # Build result
    result = {
        "tool_name": hook_input.get("tool_name", "unknown"),
        "success": True,
        "insight": insight
    }

    # Log result (using hook utils)
    log_hook_result(logger, result, exit_code=0)

    # Output feedback if we have an insight
    if insight:
        output = {
            "systemMessage": f"Tool logged: {insight}"
        }
        print(json.dumps(output))

    # Successfully processed (always exit 0 - non-blocking)
    sys.exit(0)

if __name__ == "__main__":
    main()

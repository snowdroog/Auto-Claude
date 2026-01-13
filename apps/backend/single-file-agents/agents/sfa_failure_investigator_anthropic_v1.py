#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "anthropic>=0.45.2",
#   "rich>=13.7.0",
#   "duckdb>=1.1.0",
# ]
# ///

"""
Failure Investigator SFA - Root cause analysis for failed Auto-Claude sessions.

This single-file agent constructs a timeline of events leading to session
failure, analyzes error patterns, and provides recovery recommendations.

/// Example Usage
# Investigate specific failed session
uv run sfa_failure_investigator_anthropic_v1.py \
  --db .auto-claude/events.db \
  --session-id abc123

# Find recent failures
uv run sfa_failure_investigator_anthropic_v1.py \
  --db .auto-claude/events.db \
  --days 7 \
  --status failed

# Analyze failures by agent type
uv run sfa_failure_investigator_anthropic_v1.py \
  --db .auto-claude/events.db \
  --days 7 \
  --agent-type coder

# JSON output
uv run sfa_failure_investigator_anthropic_v1.py \
  --db .auto-claude/events.db \
  --session-id abc123 \
  --json
///
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import duckdb
from anthropic import Anthropic
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree


def get_session_info(db_path: Path, session_id: str) -> Optional[Dict[str, Any]]:
    """Get session metadata."""
    conn = duckdb.connect(str(db_path), read_only=True)

    try:
        result = conn.execute(
            """
            SELECT
                session_id,
                agent_type,
                spec_id,
                status,
                error_message,
                input_tokens,
                output_tokens,
                created_at,
                completed_at
            FROM sessions
            WHERE session_id = ?
            """,
            [session_id],
        ).fetchone()

        if not result:
            return None

        columns = [desc[0] for desc in conn.description]
        return dict(zip(columns, result))

    finally:
        conn.close()


def get_failed_sessions(
    db_path: Path,
    days: Optional[int] = None,
    agent_type: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Get list of failed sessions."""
    conn = duckdb.connect(str(db_path), read_only=True)

    try:
        query = """
            SELECT
                session_id,
                agent_type,
                spec_id,
                status,
                error_message,
                created_at,
                completed_at
            FROM sessions
            WHERE status = 'failed'
        """

        params = []

        if days:
            cutoff = datetime.now() - timedelta(days=days)
            query += " AND created_at >= ?"
            params.append(cutoff)

        if agent_type:
            query += " AND agent_type = ?"
            params.append(agent_type)

        query += " ORDER BY created_at DESC"

        result = conn.execute(query, params).fetchall()
        columns = [desc[0] for desc in conn.description]

        return [dict(zip(columns, row)) for row in result]

    finally:
        conn.close()


def get_session_timeline(db_path: Path, session_id: str) -> List[Dict[str, Any]]:
    """Construct timeline of events for a session."""
    conn = duckdb.connect(str(db_path), read_only=True)

    try:
        # Get tool calls
        tool_calls = conn.execute(
            """
            SELECT
                'tool_call' as event_type,
                tool_call_id as event_id,
                tool_name,
                tool_args,
                result,
                timestamp
            FROM tool_calls
            WHERE session_id = ?
            ORDER BY timestamp
            """,
            [session_id],
        ).fetchall()

        tool_columns = [desc[0] for desc in conn.description]
        tool_events = [dict(zip(tool_columns, row)) for row in tool_calls]

        # Get other events if available
        try:
            other_events = conn.execute(
                """
                SELECT
                    'event' as event_type,
                    event_id,
                    event_type as event_name,
                    event_data,
                    timestamp
                FROM events
                WHERE session_id = ?
                ORDER BY timestamp
                """,
                [session_id],
            ).fetchall()

            event_columns = [desc[0] for desc in conn.description]
            other_events = [dict(zip(event_columns, row)) for row in other_events]

            # Combine and sort by timestamp
            all_events = tool_events + other_events
            all_events.sort(key=lambda x: x["timestamp"])

            return all_events
        except:
            # events table might not exist
            return tool_events

    finally:
        conn.close()


def investigate_failure(
    session_info: Dict[str, Any],
    timeline: List[Dict[str, Any]],
    api_key: str,
) -> Dict[str, Any]:
    """Use Claude to analyze failure and provide root cause analysis."""
    client = Anthropic(api_key=api_key)

    # Prepare timeline summary (last 20 events before failure)
    recent_events = timeline[-20:] if len(timeline) > 20 else timeline
    timeline_text = json.dumps(recent_events, indent=2, default=str)

    session_text = json.dumps(session_info, indent=2, default=str)

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=3000,
        messages=[
            {
                "role": "user",
                "content": f"""Investigate this failed Auto-Claude session and provide root cause analysis.

# Session Info
{session_text}

# Timeline (last 20 events)
{timeline_text}

Provide a structured analysis:

## Failure Summary
- What failed and when
- Which agent was involved
- Which spec was being worked on

## Timeline Analysis
- Key events leading to failure
- Pattern of tool calls before failure
- Any warning signs or anomalies

## Root Cause Hypothesis
- Most likely cause of failure
- Supporting evidence from timeline
- Why this pattern led to failure

## Similar Failures
- Have similar patterns been seen before?
- Common failure modes for this agent type

## Recovery Steps
1. Immediate actions to resolve
2. How to prevent recurrence
3. Monitoring to add

## Impact Assessment
- Time lost
- Cost impact
- Scope of issue (isolated vs systemic)

Keep analysis concise but thorough. Focus on actionable insights.""",
            }
        ],
    )

    return {"analysis": message.content[0].text}


def format_timeline_tree(timeline: List[Dict[str, Any]], max_events: int = 15) -> Tree:
    """Format timeline as a Rich tree."""
    tree = Tree("[bold]Session Timeline")

    # Show last N events
    events_to_show = timeline[-max_events:] if len(timeline) > max_events else timeline

    if len(timeline) > max_events:
        tree.add(f"[dim]... ({len(timeline) - max_events} earlier events)[/dim]")

    for event in events_to_show:
        timestamp = event.get("timestamp", "Unknown")
        if isinstance(timestamp, datetime):
            timestamp = timestamp.strftime("%H:%M:%S")

        event_type = event.get("event_type", "unknown")

        if event_type == "tool_call":
            tool_name = event.get("tool_name", "Unknown")
            args_str = ""
            try:
                args = json.loads(event.get("tool_args", "{}"))
                if "file_path" in args:
                    args_str = f": {Path(args['file_path']).name}"
            except:
                pass

            node = tree.add(f"[cyan]{timestamp}[/cyan] Tool: [yellow]{tool_name}[/yellow]{args_str}")

            # Add result if it's an error
            result = event.get("result", "")
            if result and ("error" in result.lower() or "failed" in result.lower()):
                node.add(f"[red]Error: {result[:100]}...[/red]")

        else:
            event_name = event.get("event_name", "Unknown")
            tree.add(f"[cyan]{timestamp}[/cyan] Event: [green]{event_name}[/green]")

    return tree


def format_output(
    session_info: Dict[str, Any],
    timeline: List[Dict[str, Any]],
    investigation: Dict[str, Any],
    json_output: bool,
) -> None:
    """Format and display the output."""
    if json_output:
        output = {
            "session": session_info,
            "timeline_length": len(timeline),
            "investigation": investigation,
        }
        print(json.dumps(output, indent=2, default=str))
        return

    console = Console()

    # Display header
    session_id = session_info.get("session_id", "Unknown")
    agent_type = session_info.get("agent_type", "Unknown")
    spec_id = session_info.get("spec_id", "Unknown")

    console.print(
        Panel(
            f"[cyan]Session:[/cyan] {session_id}\n"
            f"[cyan]Agent:[/cyan] {agent_type}\n"
            f"[cyan]Spec:[/cyan] {spec_id}\n"
            f"[red]Status:[/red] [bold]FAILED[/bold]",
            title="[bold]Failure Investigation",
            border_style="red",
        )
    )

    # Display error message if available
    error_msg = session_info.get("error_message")
    if error_msg:
        console.print("\n[bold red]Error Message:[/bold red]")
        console.print(Panel(error_msg, border_style="red"))

    # Display timeline
    console.print("\n[bold yellow]Timeline:[/bold yellow]")
    console.print(format_timeline_tree(timeline, max_events=15))

    # Display investigation
    if investigation:
        console.print("\n[bold magenta]Root Cause Analysis:[/bold magenta]")
        console.print(Markdown(investigation["analysis"]))


def format_failed_sessions_table(sessions: List[Dict[str, Any]]) -> Table:
    """Format list of failed sessions as a table."""
    table = Table(title=f"Failed Sessions ({len(sessions)} found)")

    table.add_column("Session", style="cyan", no_wrap=True)
    table.add_column("Agent", style="yellow")
    table.add_column("Spec", style="green")
    table.add_column("Time", style="dim")
    table.add_column("Error", overflow="fold")

    for session in sessions[:20]:  # Show first 20
        created = session.get("created_at", "Unknown")
        if isinstance(created, datetime):
            created = created.strftime("%Y-%m-%d %H:%M")

        error = session.get("error_message", "Unknown")
        if len(error) > 50:
            error = error[:47] + "..."

        table.add_row(
            session.get("session_id", "")[:8],
            session.get("agent_type", ""),
            session.get("spec_id", ""),
            created,
            error,
        )

    if len(sessions) > 20:
        table.add_row("...", "...", "...", "...", f"({len(sessions) - 20} more)")

    return table


def main():
    parser = argparse.ArgumentParser(
        description="Investigate failed Auto-Claude sessions and provide root cause analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Investigate specific session
  %(prog)s --db .auto-claude/events.db --session-id abc123

  # Find recent failures
  %(prog)s --db .auto-claude/events.db --days 7 --status failed

  # Failures by agent type
  %(prog)s --db .auto-claude/events.db --days 7 --agent-type coder

  # JSON output
  %(prog)s --db .auto-claude/events.db --session-id abc123 --json
        """,
    )

    parser.add_argument(
        "--db",
        type=Path,
        default=".auto-claude/events.db",
        help="Path to events database (default: .auto-claude/events.db)",
    )
    parser.add_argument(
        "--session-id",
        type=str,
        help="Specific session ID to investigate",
    )
    parser.add_argument(
        "--days",
        type=int,
        help="Find failures from last N days",
    )
    parser.add_argument(
        "--agent-type",
        type=str,
        choices=["planner", "coder", "qa_reviewer", "qa_fixer", "spec_gatherer", "spec_writer"],
        help="Filter by agent type",
    )
    parser.add_argument(
        "--status",
        type=str,
        default="failed",
        help="Session status to investigate (default: failed)",
    )
    parser.add_argument(
        "--json", action="store_true", help="Output in JSON format"
    )

    args = parser.parse_args()

    # Get API key
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        console = Console()
        console.print(
            "[red]Error:[/red] ANTHROPIC_API_KEY environment variable not set",
            style="bold",
        )
        sys.exit(1)

    # Validate database
    if not args.db.exists():
        console = Console()
        console.print(
            f"[red]Error:[/red] Database not found: {args.db}",
            style="bold",
        )
        sys.exit(1)

    try:
        if args.session_id:
            # Investigate specific session
            session_info = get_session_info(args.db, args.session_id)

            if not session_info:
                console = Console()
                console.print(
                    f"[red]Error:[/red] Session not found: {args.session_id}",
                    style="bold",
                )
                sys.exit(1)

            # Get timeline
            timeline = get_session_timeline(args.db, args.session_id)

            # Investigate failure
            investigation = investigate_failure(session_info, timeline, api_key)

            # Display results
            format_output(session_info, timeline, investigation, args.json)

        else:
            # List failed sessions
            failed_sessions = get_failed_sessions(args.db, args.days, args.agent_type)

            if not failed_sessions:
                console = Console()
                console.print("[green]No failed sessions found[/green]")
                sys.exit(0)

            if args.json:
                print(json.dumps({"failed_sessions": failed_sessions}, indent=2, default=str))
            else:
                console = Console()
                console.print("\n[bold red]Failed Sessions:[/bold red]")
                console.print(format_failed_sessions_table(failed_sessions))
                console.print(
                    f"\n[dim]Use --session-id <id> to investigate a specific failure[/dim]"
                )

    except Exception as e:
        console = Console()
        console.print(f"[red]Error:[/red] {e}", style="bold")
        if not args.json:
            console.print_exception()
        sys.exit(1)


if __name__ == "__main__":
    main()

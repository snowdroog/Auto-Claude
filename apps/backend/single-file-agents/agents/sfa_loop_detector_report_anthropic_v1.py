#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "anthropic>=0.45.2",
#   "rich>=13.7.0",
#   "duckdb>=1.1.0",
# ]
# ///

"""
Loop Detector SFA - Detect infinite loops and stuck states in Auto-Claude sessions.

This single-file agent analyzes tool call patterns to identify:
- Repeated tool sequences (potential loops)
- Excessive file read/edit cycles on same files
- Long-running sessions without progress
- Stuck agent behaviors

/// Example Usage
# Detect loops in recent sessions
uv run sfa_loop_detector_report_anthropic_v1.py \
  --db .auto-claude/events.db \
  --days 7

# Analyze specific session
uv run sfa_loop_detector_report_anthropic_v1.py \
  --db .auto-claude/events.db \
  --session-id abc123

# High severity only
uv run sfa_loop_detector_report_anthropic_v1.py \
  --db .auto-claude/events.db \
  --days 7 \
  --severity high

# JSON output
uv run sfa_loop_detector_report_anthropic_v1.py \
  --db .auto-claude/events.db \
  --days 7 \
  --json
///
"""

import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import duckdb
from anthropic import Anthropic
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table


def get_tool_calls(
    db_path: Path,
    days: Optional[int] = None,
    session_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Query tool call data from events database."""
    conn = duckdb.connect(str(db_path), read_only=True)

    try:
        query = """
            SELECT
                tc.tool_call_id,
                tc.session_id,
                tc.tool_name,
                tc.tool_args,
                tc.result,
                tc.timestamp,
                s.agent_type,
                s.spec_id
            FROM tool_calls tc
            JOIN sessions s ON tc.session_id = s.session_id
            WHERE 1=1
        """

        params = []

        if days:
            cutoff = datetime.now() - timedelta(days=days)
            query += " AND tc.timestamp >= ?"
            params.append(cutoff)

        if session_id:
            query += " AND tc.session_id = ?"
            params.append(session_id)

        query += " ORDER BY tc.session_id, tc.timestamp"

        result = conn.execute(query, params).fetchall()
        columns = [desc[0] for desc in conn.description]

        return [dict(zip(columns, row)) for row in result]

    finally:
        conn.close()


def detect_loop_patterns(tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Detect loop patterns in tool calls."""
    loops = []

    # Group by session
    by_session = defaultdict(list)
    for call in tool_calls:
        by_session[call["session_id"]].append(call)

    # Analyze each session
    for session_id, calls in by_session.items():
        if len(calls) < 5:
            continue  # Need at least 5 calls to detect a pattern

        # Detect repeated tool sequences
        sequence_length = 3  # Look for sequences of 3 tools
        sequences = []

        for i in range(len(calls) - sequence_length + 1):
            seq = tuple(call["tool_name"] for call in calls[i : i + sequence_length])
            sequences.append((seq, i))

        # Find repeated sequences
        sequence_counts = defaultdict(list)
        for seq, idx in sequences:
            sequence_counts[seq].append(idx)

        for seq, indices in sequence_counts.items():
            if len(indices) >= 3:  # Repeated 3+ times
                # Check if it's a real loop (indices close together)
                if max(indices) - min(indices) < len(calls) * 0.8:
                    loops.append(
                        {
                            "session_id": session_id,
                            "type": "repeated_sequence",
                            "pattern": " → ".join(seq),
                            "occurrences": len(indices),
                            "tools_involved": list(seq),
                            "severity": "high" if len(indices) >= 5 else "medium",
                        }
                    )

        # Detect repeated file operations on same files
        file_ops = defaultdict(list)
        for call in calls:
            if call["tool_name"] in ["Read", "Edit", "Write"]:
                try:
                    args = json.loads(call.get("tool_args", "{}"))
                    file_path = args.get("file_path", "")
                    if file_path:
                        file_ops[file_path].append(call["tool_name"])
                except:
                    pass

        for file_path, ops in file_ops.items():
            if len(ops) >= 5:  # 5+ operations on same file
                # Check for edit/read cycles
                read_edit_count = sum(
                    1 for op in ops if op in ["Read", "Edit"]
                )
                if read_edit_count >= 4:
                    loops.append(
                        {
                            "session_id": session_id,
                            "type": "file_operation_loop",
                            "pattern": f"Repeated Read/Edit on {Path(file_path).name}",
                            "occurrences": len(ops),
                            "file": file_path,
                            "operations": ops,
                            "severity": "high" if len(ops) >= 8 else "medium",
                        }
                    )

        # Detect long-running sessions (potential stuck state)
        if len(calls) > 50:  # More than 50 tool calls
            duration_minutes = (
                calls[-1]["timestamp"] - calls[0]["timestamp"]
            ).total_seconds() / 60

            if duration_minutes > 30:  # Longer than 30 minutes
                loops.append(
                    {
                        "session_id": session_id,
                        "type": "long_running_session",
                        "pattern": f"{len(calls)} tool calls in {duration_minutes:.1f} minutes",
                        "occurrences": len(calls),
                        "duration_minutes": duration_minutes,
                        "severity": "medium" if duration_minutes < 60 else "high",
                    }
                )

    return loops


def analyze_loops(loops: List[Dict[str, Any]], api_key: str) -> str:
    """Use Claude to analyze detected loops and provide recommendations."""
    if not loops:
        return "No loops detected. Sessions completed efficiently."

    client = Anthropic(api_key=api_key)

    loops_text = json.dumps(loops, indent=2, default=str)

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[
            {
                "role": "user",
                "content": f"""Analyze these detected loop patterns in Auto-Claude sessions.

{loops_text}

Provide:
1. Summary of detected loops (by type and severity)
2. Root cause analysis for each loop type
3. Impact assessment (time wasted, cost impact)
4. Prevention strategies and recommendations
5. Specific actions to resolve these patterns

Keep the analysis actionable and focused on preventing future loops.""",
            }
        ],
    )

    return message.content[0].text


def format_loops_table(loops: List[Dict[str, Any]], severity_filter: Optional[str] = None) -> Table:
    """Format detected loops as a Rich table."""
    # Filter by severity if specified
    if severity_filter:
        loops = [loop for loop in loops if loop.get("severity") == severity_filter]

    if not loops:
        table = Table(title="Loop Detection Results")
        table.add_column("Status")
        table.add_row("No loops detected")
        return table

    table = Table(title=f"Detected Loops ({len(loops)} found)")

    table.add_column("Session", style="cyan", no_wrap=True)
    table.add_column("Type", style="yellow")
    table.add_column("Pattern", overflow="fold")
    table.add_column("Count", justify="right")
    table.add_column("Severity", justify="center")

    for loop in loops:
        severity_style = "red bold" if loop["severity"] == "high" else "yellow"
        table.add_row(
            loop["session_id"][:8],
            loop["type"].replace("_", " ").title(),
            loop["pattern"],
            str(loop["occurrences"]),
            f"[{severity_style}]{loop['severity'].upper()}[/{severity_style}]",
        )

    return table


def format_output(
    loops: List[Dict[str, Any]],
    analysis: str,
    days: Optional[int],
    session_id: Optional[str],
    severity_filter: Optional[str],
    json_output: bool,
) -> None:
    """Format and display the output."""
    if json_output:
        output = {
            "loops": loops,
            "analysis": analysis,
            "total_loops": len(loops),
            "by_severity": {
                "high": sum(1 for l in loops if l.get("severity") == "high"),
                "medium": sum(1 for l in loops if l.get("severity") == "medium"),
                "low": sum(1 for l in loops if l.get("severity") == "low"),
            },
        }
        print(json.dumps(output, indent=2, default=str))
        return

    console = Console()

    # Display header
    header_text = "Loop Detection Report"
    if days:
        header_text += f" (Last {days} days)"
    if session_id:
        header_text += f" (Session: {session_id[:8]})"
    if severity_filter:
        header_text += f" (Severity: {severity_filter.upper()})"

    console.print(Panel(header_text, title="[bold]Loop Detector", border_style="blue"))

    # Display summary
    console.print("\n[bold green]Summary:[/bold green]")
    summary_table = Table()
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Value", justify="right")

    summary_table.add_row("Total Loops Detected", str(len(loops)))
    summary_table.add_row(
        "High Severity",
        str(sum(1 for l in loops if l.get("severity") == "high")),
        style="red bold",
    )
    summary_table.add_row(
        "Medium Severity",
        str(sum(1 for l in loops if l.get("severity") == "medium")),
        style="yellow",
    )
    summary_table.add_row(
        "Low Severity",
        str(sum(1 for l in loops if l.get("severity") == "low")),
    )

    console.print(summary_table)

    # Display loops table
    console.print("\n[bold yellow]Detected Loops:[/bold yellow]")
    console.print(format_loops_table(loops, severity_filter))

    # Display analysis
    if analysis:
        console.print("\n[bold magenta]Analysis & Recommendations:[/bold magenta]")
        console.print(Markdown(analysis))


def main():
    parser = argparse.ArgumentParser(
        description="Detect loops and stuck states in Auto-Claude sessions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Detect loops in last 7 days
  %(prog)s --db .auto-claude/events.db --days 7

  # Analyze specific session
  %(prog)s --db .auto-claude/events.db --session-id abc123

  # High severity only
  %(prog)s --db .auto-claude/events.db --days 7 --severity high

  # JSON output
  %(prog)s --db .auto-claude/events.db --days 7 --json
        """,
    )

    parser.add_argument(
        "--db",
        type=Path,
        default=".auto-claude/events.db",
        help="Path to events database (default: .auto-claude/events.db)",
    )
    parser.add_argument(
        "--days",
        type=int,
        help="Number of days to analyze (default: all time)",
    )
    parser.add_argument(
        "--session-id",
        type=str,
        help="Specific session ID to analyze",
    )
    parser.add_argument(
        "--severity",
        type=str,
        choices=["low", "medium", "high"],
        help="Filter by severity level",
    )
    parser.add_argument(
        "--json", action="store_true", help="Output in JSON format"
    )
    parser.add_argument(
        "--no-analysis",
        action="store_true",
        help="Skip AI analysis (faster)",
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
        # Get tool call data
        tool_calls = get_tool_calls(args.db, args.days, args.session_id)

        if not tool_calls:
            console = Console()
            console.print("[yellow]No tool calls found matching criteria[/yellow]")
            sys.exit(0)

        # Detect loops
        loops = detect_loop_patterns(tool_calls)

        # Analyze loops (unless skipped)
        analysis = ""
        if not args.no_analysis and loops:
            analysis = analyze_loops(loops, api_key)

        # Display results
        format_output(
            loops, analysis, args.days, args.session_id, args.severity, args.json
        )

    except Exception as e:
        console = Console()
        console.print(f"[red]Error:[/red] {e}", style="bold")
        if not args.json:
            console.print_exception()
        sys.exit(1)


if __name__ == "__main__":
    main()

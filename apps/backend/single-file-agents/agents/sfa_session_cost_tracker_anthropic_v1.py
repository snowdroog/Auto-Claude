#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "anthropic>=0.45.2",
#   "rich>=13.7.0",
#   "duckdb>=1.1.0",
# ]
# ///

"""
Session Cost Tracker SFA - Analyze token usage and API costs for Auto-Claude sessions.

This single-file agent tracks token usage (input, output, thinking) and calculates
API costs across sessions, providing breakdowns by model, phase, and spec.

/// Example Usage
# Last 7 days costs
uv run sfa_session_cost_tracker_anthropic_v1.py \
  --db .auto-claude/events.db \
  --days 7

# Specific spec costs
uv run sfa_session_cost_tracker_anthropic_v1.py \
  --db .auto-claude/events.db \
  --spec-id 001

# Compare multiple specs
uv run sfa_session_cost_tracker_anthropic_v1.py \
  --db .auto-claude/events.db \
  --spec-id 001,002,003 \
  --compare

# JSON output
uv run sfa_session_cost_tracker_anthropic_v1.py \
  --db .auto-claude/events.db \
  --days 7 \
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


# Pricing per 1M tokens (as of 2026-01)
PRICING = {
    "claude-opus-4-20250514": {"input": 15.00, "output": 75.00},
    "claude-sonnet-4-20250514": {"input": 3.00, "output": 15.00},
    "claude-sonnet-4-5-20250929": {"input": 3.00, "output": 15.00},
    "claude-haiku-4-20250514": {"input": 0.80, "output": 4.00},
}


def calculate_cost(
    model: str, input_tokens: int, output_tokens: int, thinking_tokens: int = 0
) -> float:
    """Calculate cost for given token usage."""
    pricing = PRICING.get(model, {"input": 3.00, "output": 15.00})  # Default to Sonnet

    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    thinking_cost = (thinking_tokens / 1_000_000) * pricing["input"]  # Same as input

    return input_cost + output_cost + thinking_cost


def get_session_costs(
    db_path: Path,
    days: Optional[int] = None,
    spec_id: Optional[str] = None,
    session_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Query session cost data from events database."""
    conn = duckdb.connect(str(db_path), read_only=True)

    try:
        # Build query
        query = """
            SELECT
                session_id,
                agent_type,
                spec_id,
                model,
                status,
                input_tokens,
                output_tokens,
                thinking_tokens,
                created_at,
                completed_at
            FROM sessions
            WHERE 1=1
        """

        params = []

        if days:
            cutoff = datetime.now() - timedelta(days=days)
            query += " AND created_at >= ?"
            params.append(cutoff)

        if spec_id:
            query += " AND spec_id = ?"
            params.append(spec_id)

        if session_id:
            query += " AND session_id = ?"
            params.append(session_id)

        query += " ORDER BY created_at DESC"

        result = conn.execute(query, params).fetchall()
        columns = [desc[0] for desc in conn.description]

        return [dict(zip(columns, row)) for row in result]

    finally:
        conn.close()


def analyze_costs(sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze costs and generate statistics."""
    if not sessions:
        return {
            "total_sessions": 0,
            "total_cost": 0,
            "total_tokens": 0,
            "by_agent": {},
            "by_model": {},
            "by_spec": {},
        }

    total_cost = 0
    total_input = 0
    total_output = 0
    total_thinking = 0

    by_agent = {}
    by_model = {}
    by_spec = {}

    for session in sessions:
        model = session.get("model", "unknown")
        agent = session.get("agent_type", "unknown")
        spec = session.get("spec_id", "unknown")

        input_tokens = session.get("input_tokens", 0) or 0
        output_tokens = session.get("output_tokens", 0) or 0
        thinking_tokens = session.get("thinking_tokens", 0) or 0

        cost = calculate_cost(model, input_tokens, output_tokens, thinking_tokens)

        total_cost += cost
        total_input += input_tokens
        total_output += output_tokens
        total_thinking += thinking_tokens

        # By agent
        if agent not in by_agent:
            by_agent[agent] = {
                "sessions": 0,
                "cost": 0,
                "input_tokens": 0,
                "output_tokens": 0,
            }
        by_agent[agent]["sessions"] += 1
        by_agent[agent]["cost"] += cost
        by_agent[agent]["input_tokens"] += input_tokens
        by_agent[agent]["output_tokens"] += output_tokens

        # By model
        if model not in by_model:
            by_model[model] = {
                "sessions": 0,
                "cost": 0,
                "input_tokens": 0,
                "output_tokens": 0,
            }
        by_model[model]["sessions"] += 1
        by_model[model]["cost"] += cost
        by_model[model]["input_tokens"] += input_tokens
        by_model[model]["output_tokens"] += output_tokens

        # By spec
        if spec not in by_spec:
            by_spec[spec] = {
                "sessions": 0,
                "cost": 0,
                "input_tokens": 0,
                "output_tokens": 0,
            }
        by_spec[spec]["sessions"] += 1
        by_spec[spec]["cost"] += cost
        by_spec[spec]["input_tokens"] += input_tokens
        by_spec[spec]["output_tokens"] += output_tokens

    return {
        "total_sessions": len(sessions),
        "total_cost": total_cost,
        "total_input_tokens": total_input,
        "total_output_tokens": total_output,
        "total_thinking_tokens": total_thinking,
        "total_tokens": total_input + total_output + total_thinking,
        "by_agent": by_agent,
        "by_model": by_model,
        "by_spec": by_spec,
    }


def generate_insights(analysis: Dict[str, Any], api_key: str) -> str:
    """Use Claude to generate insights from cost analysis."""
    client = Anthropic(api_key=api_key)

    analysis_text = json.dumps(analysis, indent=2, default=str)

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        messages=[
            {
                "role": "user",
                "content": f"""Analyze these Auto-Claude session cost metrics and provide insights.

{analysis_text}

Provide:
1. Key cost findings (total, averages, trends)
2. Cost distribution analysis (by agent, model, spec)
3. Efficiency observations (tokens per session, cost per spec)
4. Actionable recommendations to reduce costs
5. Any concerning patterns or anomalies

Keep the analysis concise and actionable.""",
            }
        ],
    )

    return message.content[0].text


def format_cost_table(data: Dict[str, Any], title: str) -> Table:
    """Format cost data as a Rich table."""
    table = Table(title=title)

    table.add_column("Item", style="cyan")
    table.add_column("Sessions", justify="right")
    table.add_column("Input Tokens", justify="right")
    table.add_column("Output Tokens", justify="right")
    table.add_column("Cost", justify="right", style="green")

    for item, stats in data.items():
        table.add_row(
            item,
            str(stats["sessions"]),
            f"{stats['input_tokens']:,}",
            f"{stats['output_tokens']:,}",
            f"${stats['cost']:.2f}",
        )

    return table


def format_output(
    analysis: Dict[str, Any],
    insights: str,
    days: Optional[int],
    spec_id: Optional[str],
    json_output: bool,
) -> None:
    """Format and display the output."""
    if json_output:
        output = {"analysis": analysis, "insights": insights}
        print(json.dumps(output, indent=2, default=str))
        return

    console = Console()

    # Display header
    header_text = "Cost Analysis"
    if days:
        header_text += f" (Last {days} days)"
    if spec_id:
        header_text += f" (Spec: {spec_id})"

    console.print(Panel(header_text, title="[bold]Session Cost Tracker", border_style="blue"))

    # Display summary
    console.print("\n[bold green]Summary:[/bold green]")
    summary_table = Table()
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Value", justify="right")

    summary_table.add_row("Total Sessions", str(analysis["total_sessions"]))
    summary_table.add_row("Total Tokens", f"{analysis['total_tokens']:,}")
    summary_table.add_row("Input Tokens", f"{analysis['total_input_tokens']:,}")
    summary_table.add_row("Output Tokens", f"{analysis['total_output_tokens']:,}")
    if analysis.get("total_thinking_tokens", 0) > 0:
        summary_table.add_row(
            "Thinking Tokens", f"{analysis['total_thinking_tokens']:,}"
        )
    summary_table.add_row("Total Cost", f"${analysis['total_cost']:.2f}", style="bold green")

    console.print(summary_table)

    # Display by agent
    if analysis["by_agent"]:
        console.print("\n[bold yellow]Cost by Agent:[/bold yellow]")
        console.print(format_cost_table(analysis["by_agent"], "Agent Costs"))

    # Display by model
    if analysis["by_model"]:
        console.print("\n[bold magenta]Cost by Model:[/bold magenta]")
        console.print(format_cost_table(analysis["by_model"], "Model Costs"))

    # Display by spec
    if analysis["by_spec"] and len(analysis["by_spec"]) > 1:
        console.print("\n[bold cyan]Cost by Spec:[/bold cyan]")
        console.print(format_cost_table(analysis["by_spec"], "Spec Costs"))

    # Display insights
    if insights:
        console.print("\n[bold blue]Insights & Recommendations:[/bold blue]")
        console.print(Markdown(insights))


def main():
    parser = argparse.ArgumentParser(
        description="Track Auto-Claude session costs and token usage",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Last 7 days
  %(prog)s --db .auto-claude/events.db --days 7

  # Specific spec
  %(prog)s --db .auto-claude/events.db --spec-id 001

  # Specific session
  %(prog)s --db .auto-claude/events.db --session-id abc123

  # JSON output
  %(prog)s --db .auto-claude/events.db --days 30 --json
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
        "--spec-id",
        type=str,
        help="Specific spec ID to analyze",
    )
    parser.add_argument(
        "--session-id",
        type=str,
        help="Specific session ID to analyze",
    )
    parser.add_argument(
        "--json", action="store_true", help="Output in JSON format"
    )
    parser.add_argument(
        "--no-insights",
        action="store_true",
        help="Skip AI insights generation (faster)",
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
        # Get session data
        sessions = get_session_costs(
            args.db, args.days, args.spec_id, args.session_id
        )

        if not sessions:
            console = Console()
            console.print("[yellow]No sessions found matching criteria[/yellow]")
            sys.exit(0)

        # Analyze costs
        analysis = analyze_costs(sessions)

        # Generate insights (unless skipped)
        insights = ""
        if not args.no_insights:
            insights = generate_insights(analysis, api_key)

        # Display results
        format_output(analysis, insights, args.days, args.spec_id, args.json)

    except Exception as e:
        console = Console()
        console.print(f"[red]Error:[/red] {e}", style="bold")
        if not args.json:
            console.print_exception()
        sys.exit(1)


if __name__ == "__main__":
    main()

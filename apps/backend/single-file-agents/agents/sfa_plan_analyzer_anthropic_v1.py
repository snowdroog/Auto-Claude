#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "anthropic>=0.45.2",
#   "rich>=13.7.0",
# ]
# ///

"""
Plan Analyzer SFA - Analyze Auto-Claude implementation plans.

This single-file agent analyzes implementation_plan.json files to provide
insights about subtask breakdown, dependencies, progress, and potential issues.

/// Example Usage
# Analyze a plan
uv run sfa_plan_analyzer_anthropic_v1.py \
  --plan-file .auto-claude/specs/001-auth/implementation_plan.json

# Check progress
uv run sfa_plan_analyzer_anthropic_v1.py \
  --plan-file .auto-claude/specs/001-auth/implementation_plan.json \
  --show-progress

# Identify blockers
uv run sfa_plan_analyzer_anthropic_v1.py \
  --plan-file .auto-claude/specs/001-auth/implementation_plan.json \
  --find-blockers

# JSON output
uv run sfa_plan_analyzer_anthropic_v1.py \
  --plan-file .auto-claude/specs/001-auth/implementation_plan.json \
  --json
///
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from anthropic import Anthropic
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table


def load_plan(plan_file: Path) -> Dict[str, Any]:
    """Load implementation plan from JSON file."""
    if not plan_file.exists():
        raise FileNotFoundError(f"Plan file not found: {plan_file}")

    try:
        return json.loads(plan_file.read_text())
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in plan file: {e}")


def calculate_progress(plan: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate progress statistics from plan."""
    subtasks = plan.get("subtasks", [])

    if not subtasks:
        return {
            "total": 0,
            "pending": 0,
            "in_progress": 0,
            "completed": 0,
            "failed": 0,
            "percentage": 0
        }

    total = len(subtasks)
    completed = sum(1 for s in subtasks if s.get("status") == "completed")
    in_progress = sum(1 for s in subtasks if s.get("status") == "in_progress")
    failed = sum(1 for s in subtasks if s.get("status") == "failed")
    pending = total - completed - in_progress - failed

    return {
        "total": total,
        "pending": pending,
        "in_progress": in_progress,
        "completed": completed,
        "failed": failed,
        "percentage": int((completed / total) * 100) if total > 0 else 0
    }


def analyze_plan_with_claude(
    plan: Dict[str, Any],
    api_key: str,
    focus: Optional[str] = None
) -> str:
    """Use Claude to analyze the implementation plan."""
    client = Anthropic(api_key=api_key)

    focus_instructions = {
        "blockers": "Focus on identifying blockers, dependencies, and potential issues.",
        "quality": "Focus on plan quality, subtask breakdown, and completeness.",
        "progress": "Focus on progress tracking and estimation."
    }

    instruction = focus_instructions.get(focus, "Provide a comprehensive analysis.")

    prompt = f"""Analyze this Auto-Claude implementation plan:

```json
{json.dumps(plan, indent=2)}
```

{instruction}

Provide:
1. **Overview**: Plan structure and approach
2. **Subtask Analysis**: Quality of breakdown
3. **Dependencies**: Potential bottlenecks or ordering issues
4. **Risk Assessment**: What could go wrong
5. **Recommendations**: Improvements or considerations

Be specific and actionable."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2500,
        messages=[{"role": "user", "content": prompt}]
    )

    return message.content[0].text


def identify_blockers(plan: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Identify potential blockers in the plan."""
    blockers = []
    subtasks = plan.get("subtasks", [])

    for i, subtask in enumerate(subtasks):
        # Failed subtasks are blockers
        if subtask.get("status") == "failed":
            blockers.append({
                "subtask_id": i + 1,
                "title": subtask.get("title", "Unknown"),
                "reason": "Failed execution",
                "severity": "high"
            })

        # Long in-progress subtasks might be stuck
        if subtask.get("status") == "in_progress":
            blockers.append({
                "subtask_id": i + 1,
                "title": subtask.get("title", "Unknown"),
                "reason": "Long running (possibly stuck)",
                "severity": "medium"
            })

        # Subtasks with unmet dependencies
        dependencies = subtask.get("dependencies", [])
        if dependencies:
            for dep in dependencies:
                dep_idx = dep - 1 if isinstance(dep, int) else None
                if dep_idx is not None and dep_idx < len(subtasks):
                    dep_subtask = subtasks[dep_idx]
                    if dep_subtask.get("status") != "completed":
                        blockers.append({
                            "subtask_id": i + 1,
                            "title": subtask.get("title", "Unknown"),
                            "reason": f"Waiting on subtask {dep}",
                            "severity": "low"
                        })

    return blockers


def format_output(
    plan: Dict[str, Any],
    progress: Dict[str, Any],
    analysis: Optional[str],
    blockers: Optional[List[Dict[str, Any]]],
    json_output: bool
) -> None:
    """Format and display the analysis results."""
    if json_output:
        output = {
            "plan_summary": {
                "total_subtasks": plan.get("total_subtasks", 0),
                "description": plan.get("description", "")
            },
            "progress": progress,
            "analysis": analysis,
            "blockers": blockers
        }
        print(json.dumps(output, indent=2))
        return

    console = Console()

    # Header
    console.print(Panel(
        f"[cyan]Total Subtasks:[/cyan] {progress['total']}\n"
        f"[cyan]Progress:[/cyan] {progress['percentage']}% ({progress['completed']}/{progress['total']})",
        title="[bold]Implementation Plan Analysis",
        border_style="blue"
    ))

    # Progress breakdown
    console.print("\n[bold green]Progress Breakdown[/bold green]")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Status", style="cyan")
    table.add_column("Count", justify="right", style="yellow")
    table.add_column("Percentage", justify="right", style="dim")

    for status in ["completed", "in_progress", "pending", "failed"]:
        count = progress[status]
        pct = int((count / progress['total']) * 100) if progress['total'] > 0 else 0
        status_style = {
            "completed": "green",
            "in_progress": "yellow",
            "pending": "dim",
            "failed": "red"
        }.get(status, "white")

        table.add_row(
            f"[{status_style}]{status.replace('_', ' ').title()}[/{status_style}]",
            str(count),
            f"{pct}%"
        )

    console.print(table)

    # Blockers
    if blockers:
        console.print(f"\n[bold yellow]Potential Blockers ({len(blockers)})[/bold yellow]")
        blocker_table = Table(show_header=True, header_style="bold magenta")
        blocker_table.add_column("Subtask", style="cyan")
        blocker_table.add_column("Title", style="yellow")
        blocker_table.add_column("Reason", style="white")
        blocker_table.add_column("Severity", justify="center")

        for blocker in blockers:
            severity_style = {
                "high": "red",
                "medium": "yellow",
                "low": "dim"
            }.get(blocker["severity"], "white")

            blocker_table.add_row(
                f"#{blocker['subtask_id']}",
                blocker['title'][:40],
                blocker['reason'],
                f"[{severity_style}]{blocker['severity']}[/{severity_style}]"
            )

        console.print(blocker_table)

    # AI Analysis
    if analysis:
        console.print("\n[bold green]Detailed Analysis[/bold green]")
        console.print(Markdown(analysis))


def main():
    parser = argparse.ArgumentParser(
        description="Analyze Auto-Claude implementation plans",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze a plan
  %(prog)s --plan-file .auto-claude/specs/001-auth/implementation_plan.json

  # Show progress details
  %(prog)s --plan-file .auto-claude/specs/001-auth/implementation_plan.json --show-progress

  # Find blockers
  %(prog)s --plan-file .auto-claude/specs/001-auth/implementation_plan.json --find-blockers

  # JSON output
  %(prog)s --plan-file .auto-claude/specs/001-auth/implementation_plan.json --json
        """
    )

    parser.add_argument(
        "--plan-file",
        type=Path,
        required=True,
        help="Path to implementation_plan.json file"
    )
    parser.add_argument(
        "--show-progress",
        action="store_true",
        help="Show detailed progress breakdown"
    )
    parser.add_argument(
        "--find-blockers",
        action="store_true",
        help="Identify potential blockers"
    )
    parser.add_argument(
        "--focus",
        choices=["blockers", "quality", "progress"],
        help="Focus analysis on specific aspect"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format"
    )

    args = parser.parse_args()

    # Get API key
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        console = Console()
        console.print(
            "[red]Error:[/red] ANTHROPIC_API_KEY environment variable not set",
            style="bold"
        )
        sys.exit(1)

    try:
        # Load plan
        plan = load_plan(args.plan_file)

        # Calculate progress
        progress = calculate_progress(plan)

        # Identify blockers if requested
        blockers = None
        if args.find_blockers:
            blockers = identify_blockers(plan)

        # Get Claude's analysis
        analysis = analyze_plan_with_claude(plan, api_key, args.focus)

        # Display results
        format_output(plan, progress, analysis, blockers, args.json)

    except FileNotFoundError as e:
        console = Console()
        console.print(f"[red]Error:[/red] {e}", style="bold")
        sys.exit(1)
    except ValueError as e:
        console = Console()
        console.print(f"[red]Error:[/red] {e}", style="bold")
        sys.exit(1)
    except Exception as e:
        console = Console()
        console.print(f"[red]Error:[/red] {e}", style="bold")
        if not args.json:
            console.print_exception()
        sys.exit(1)


if __name__ == "__main__":
    main()

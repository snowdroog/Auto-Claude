#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "anthropic>=0.45.2",
#   "rich>=13.7.0",
# ]
# ///

"""
QA Report Analyzer SFA - Analyze Auto-Claude QA validation reports.

This single-file agent analyzes qa_report.md files to extract insights about
acceptance criteria validation, issues found, and overall quality assessment.

/// Example Usage
# Analyze a QA report
uv run sfa_qa_report_analyzer_anthropic_v1.py \
  --report-file .auto-claude/specs/001-auth/qa_report.md

# Compare multiple reports
uv run sfa_qa_report_analyzer_anthropic_v1.py \
  --specs-root .auto-claude/specs

# Show only failures
uv run sfa_qa_report_analyzer_anthropic_v1.py \
  --report-file .auto-claude/specs/001-auth/qa_report.md \
  --failures-only

# JSON output
uv run sfa_qa_report_analyzer_anthropic_v1.py \
  --report-file .auto-claude/specs/001-auth/qa_report.md \
  --json
///
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from anthropic import Anthropic
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table


def parse_qa_report(report_content: str) -> Dict[str, Any]:
    """Parse QA report to extract structured data."""
    parsed = {
        "status": "unknown",
        "acceptance_criteria": [],
        "issues": [],
        "recommendations": [],
        "metadata": {}
    }

    # Extract overall status
    if "Status: PASSED" in report_content or "✓ PASSED" in report_content:
        parsed["status"] = "passed"
    elif "Status: FAILED" in report_content or "✗ FAILED" in report_content:
        parsed["status"] = "failed"
    elif "Status: PARTIAL" in report_content:
        parsed["status"] = "partial"

    # Count criteria (look for checkboxes or numbered lists)
    criteria_pattern = r'(?:- \[[ xX]\]|✓|✗|\d+\.) (.+)'
    for match in re.finditer(criteria_pattern, report_content):
        criterion = match.group(1).strip()
        status = "passed" if ("✓" in match.group(0) or "[x]" in match.group(0).lower()) else "failed"
        parsed["acceptance_criteria"].append({
            "description": criterion,
            "status": status
        })

    # Extract issues (sections with "Issue", "Problem", "Failed")
    issue_section = False
    for line in report_content.splitlines():
        if any(keyword in line.lower() for keyword in ["issues found", "problems", "failures"]):
            issue_section = True
        elif line.startswith("#") and issue_section:
            issue_section = False
        elif issue_section and line.strip() and line.strip().startswith(("- ", "* ", "1.")):
            parsed["issues"].append(line.strip())

    return parsed


def analyze_qa_report(
    report_content: str,
    spec_name: str,
    api_key: str,
    failures_only: bool = False
) -> str:
    """Use Claude to analyze the QA report."""
    client = Anthropic(api_key=api_key)

    focus = "Focus ONLY on failures and issues. Ignore passing criteria." if failures_only else "Provide a balanced analysis of passes and failures."

    prompt = f"""Analyze this Auto-Claude QA validation report for spec: {spec_name}

**Report Content:**
```markdown
{report_content}
```

{focus}

Provide:
1. **Summary**: Overall assessment (passed/failed/partial)
2. **Acceptance Criteria**: What passed vs failed
3. **Key Issues**: Critical problems found
4. **Root Causes**: Why criteria failed (if applicable)
5. **Recommendations**: What needs to be fixed

Be specific and actionable. Reference exact criteria from the report."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2500,
        messages=[{"role": "user", "content": prompt}]
    )

    return message.content[0].text


def format_output(
    reports: List[Dict[str, Any]],
    json_output: bool
) -> None:
    """Format and display QA report analysis."""
    if json_output:
        print(json.dumps(reports, indent=2))
        return

    console = Console()

    # Header
    total = len(reports)
    passed = sum(1 for r in reports if r["parsed"]["status"] == "passed")
    failed = sum(1 for r in reports if r["parsed"]["status"] == "failed")

    console.print(Panel(
        f"[cyan]Reports Analyzed:[/cyan] {total}\n"
        f"[green]Passed:[/green] {passed}\n"
        f"[red]Failed:[/red] {failed}\n"
        f"[yellow]Partial/Unknown:[/yellow] {total - passed - failed}",
        title="[bold]QA Report Analysis",
        border_style="blue"
    ))

    # Summary table for multiple reports
    if len(reports) > 1:
        console.print("\n[bold green]Summary[/bold green]")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Spec", style="cyan")
        table.add_column("Status", justify="center")
        table.add_column("Criteria", justify="center", style="dim")
        table.add_column("Issues", justify="center", style="red")

        for report in sorted(reports, key=lambda x: x["spec_name"]):
            status = report["parsed"]["status"]
            status_icon = {
                "passed": "[green]✓[/green]",
                "failed": "[red]✗[/red]",
                "partial": "[yellow]~[/yellow]",
                "unknown": "[dim]?[/dim]"
            }.get(status, "[dim]?[/dim]")

            criteria_count = len(report["parsed"]["acceptance_criteria"])
            issues_count = len(report["parsed"]["issues"])

            table.add_row(
                report["spec_name"],
                status_icon,
                str(criteria_count) if criteria_count > 0 else "-",
                str(issues_count) if issues_count > 0 else "-"
            )

        console.print(table)

    # Detailed analysis for each report
    for report in reports:
        console.print(f"\n[bold cyan]═══ {report['spec_name']} ═══[/bold cyan]")

        # Status
        status = report["parsed"]["status"]
        status_display = {
            "passed": "[green]✓ PASSED[/green]",
            "failed": "[red]✗ FAILED[/red]",
            "partial": "[yellow]~ PARTIAL[/yellow]",
            "unknown": "[dim]? UNKNOWN[/dim]"
        }.get(status, "[dim]? UNKNOWN[/dim]")

        console.print(f"Status: {status_display}")

        # Criteria breakdown
        if report["parsed"]["acceptance_criteria"]:
            console.print(f"\n[bold]Acceptance Criteria ({len(report['parsed']['acceptance_criteria'])}):[/bold]")
            for criterion in report["parsed"]["acceptance_criteria"][:10]:  # Show first 10
                status_icon = "✓" if criterion["status"] == "passed" else "✗"
                status_color = "green" if criterion["status"] == "passed" else "red"
                console.print(f"  [{status_color}]{status_icon}[/{status_color}] {criterion['description'][:70]}")

        # Issues
        if report["parsed"]["issues"]:
            console.print(f"\n[bold red]Issues Found ({len(report['parsed']['issues'])}):[/bold red]")
            for issue in report["parsed"]["issues"][:5]:  # Show first 5
                console.print(f"  • {issue[:100]}")

        # AI Analysis
        console.print(f"\n[bold green]Detailed Analysis:[/bold green]")
        console.print(Markdown(report["analysis"]))


def main():
    parser = argparse.ArgumentParser(
        description="Analyze Auto-Claude QA validation reports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze a QA report
  %(prog)s --report-file .auto-claude/specs/001-auth/qa_report.md

  # Compare multiple reports
  %(prog)s --specs-root .auto-claude/specs

  # Show only failures
  %(prog)s --report-file .auto-claude/specs/001-auth/qa_report.md --failures-only

  # JSON output
  %(prog)s --report-file .auto-claude/specs/001-auth/qa_report.md --json
        """
    )

    parser.add_argument(
        "--report-file",
        type=Path,
        help="Path to specific qa_report.md file"
    )
    parser.add_argument(
        "--specs-root",
        type=Path,
        help="Path to root specs directory (analyze all QA reports)"
    )
    parser.add_argument(
        "--failures-only",
        action="store_true",
        help="Focus analysis on failures only"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format"
    )

    args = parser.parse_args()

    if not args.report_file and not args.specs_root:
        console = Console()
        console.print(
            "[red]Error:[/red] Must provide either --report-file or --specs-root",
            style="bold"
        )
        sys.exit(1)

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
        report_files = []

        # Collect report files
        if args.report_file:
            if not args.report_file.exists():
                raise FileNotFoundError(f"Report file not found: {args.report_file}")
            report_files.append(args.report_file)

        if args.specs_root:
            if not args.specs_root.exists():
                raise FileNotFoundError(f"Specs root directory not found: {args.specs_root}")
            # Find all qa_report.md files
            for subdir in args.specs_root.iterdir():
                if subdir.is_dir():
                    qa_file = subdir / "qa_report.md"
                    if qa_file.exists():
                        report_files.append(qa_file)

        if not report_files:
            raise ValueError("No QA report files found to analyze")

        # Analyze each report
        results = []
        console = Console()

        for report_file in report_files:
            if not args.json:
                console.print(f"[dim]Analyzing {report_file.parent.name}...[/dim]")

            report_content = report_file.read_text()
            parsed = parse_qa_report(report_content)
            analysis = analyze_qa_report(
                report_content,
                report_file.parent.name,
                api_key,
                args.failures_only
            )

            results.append({
                "spec_name": report_file.parent.name,
                "parsed": parsed,
                "analysis": analysis
            })

        # Display results
        format_output(results, args.json)

    except FileNotFoundError as e:
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

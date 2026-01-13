#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "anthropic>=0.45.2",
#   "rich>=13.7.0",
# ]
# ///

"""
Spec Validator SFA - Validate Auto-Claude spec.md files for completeness and quality.

This single-file agent validates spec files against Auto-Claude's spec format,
checking for required sections, clarity, and completeness.

/// Example Usage
# Validate a specific spec
uv run sfa_spec_validator_anthropic_v1.py \
  --spec-dir .auto-claude/specs/001-auth-feature

# Validate all specs
uv run sfa_spec_validator_anthropic_v1.py \
  --specs-root .auto-claude/specs

# Strict validation (fail on warnings)
uv run sfa_spec_validator_anthropic_v1.py \
  --spec-dir .auto-claude/specs/001-auth-feature \
  --strict

# JSON output
uv run sfa_spec_validator_anthropic_v1.py \
  --spec-dir .auto-claude/specs/001-auth-feature \
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
from rich.table import Table


REQUIRED_SECTIONS = [
    "Overview",
    "Requirements",
    "Acceptance Criteria",
    "Technical Approach",
    "Implementation Details"
]

OPTIONAL_SECTIONS = [
    "Constraints",
    "Dependencies",
    "Testing Strategy",
    "Security Considerations",
    "Performance Considerations"
]

VALIDATION_PROMPT = """
Analyze this Auto-Claude spec file for quality and completeness.

**Spec Content:**
```markdown
{spec_content}
```

**Required Sections**: {required_sections}
**Optional but Recommended**: {optional_sections}

Validate:
1. **Structure**: All required sections present
2. **Clarity**: Clear, unambiguous language
3. **Completeness**: Sufficient detail for implementation
4. **Acceptance Criteria**: Testable and specific
5. **Technical Feasibility**: Approach is sound
6. **Edge Cases**: Potential issues identified

Provide:
- **Valid**: true/false (are required sections present?)
- **Score**: 0-100 (overall quality)
- **Issues**: List of problems (if any)
- **Warnings**: Recommendations for improvement
- **Strengths**: What's done well
"""


def check_structure(spec_content: str) -> Dict[str, Any]:
    """Check if spec has required and optional sections."""
    sections_found = {
        "required": [],
        "missing_required": [],
        "optional": [],
        "missing_optional": []
    }

    # Convert to lowercase for case-insensitive matching
    content_lower = spec_content.lower()

    # Check required sections
    for section in REQUIRED_SECTIONS:
        # Look for markdown headers with the section name
        if f"#{section.lower()}" in content_lower or f"## {section.lower()}" in content_lower:
            sections_found["required"].append(section)
        else:
            sections_found["missing_required"].append(section)

    # Check optional sections
    for section in OPTIONAL_SECTIONS:
        if f"#{section.lower()}" in content_lower or f"## {section.lower()}" in content_lower:
            sections_found["optional"].append(section)
        else:
            sections_found["missing_optional"].append(section)

    return sections_found


def validate_spec(
    spec_content: str,
    spec_name: str,
    api_key: str,
    sections: Dict[str, Any]
) -> Dict[str, Any]:
    """Use Claude to validate spec quality."""
    client = Anthropic(api_key=api_key)

    prompt = VALIDATION_PROMPT.format(
        spec_content=spec_content[:8000],  # Limit to avoid token limits
        required_sections=", ".join(REQUIRED_SECTIONS),
        optional_sections=", ".join(OPTIONAL_SECTIONS)
    )

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )

    analysis = message.content[0].text

    # Parse score and valid flag
    score = None
    valid = len(sections["missing_required"]) == 0

    for line in analysis.splitlines():
        if "score" in line.lower() and any(char.isdigit() for char in line):
            import re
            match = re.search(r'\d+', line)
            if match:
                score = int(match.group())
                break

    return {
        "spec_name": spec_name,
        "valid": valid,
        "score": score,
        "sections": sections,
        "analysis": analysis,
        "word_count": len(spec_content.split())
    }


def format_output(results: List[Dict[str, Any]], json_output: bool, strict: bool) -> None:
    """Format and display validation results."""
    if json_output:
        print(json.dumps(results, indent=2))
        return

    console = Console()

    # Header
    total_valid = sum(1 for r in results if r["valid"])
    console.print(Panel(
        f"[cyan]Specs Validated:[/cyan] {len(results)}\n"
        f"[cyan]Valid:[/cyan] {total_valid}/{len(results)}",
        title="[bold]Spec Validation Results",
        border_style="green" if total_valid == len(results) else "yellow"
    ))

    # Summary table
    if len(results) > 1:
        console.print("\n[bold green]Summary[/bold green]")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Spec", style="cyan")
        table.add_column("Valid", justify="center")
        table.add_column("Score", justify="center", style="yellow")
        table.add_column("Missing", justify="center", style="red")

        for result in sorted(results, key=lambda x: x.get("score") or 0, reverse=True):
            valid_icon = "✓" if result["valid"] else "✗"
            valid_style = "green" if result["valid"] else "red"
            score_str = str(result["score"]) if result["score"] else "N/A"
            missing_count = len(result["sections"]["missing_required"])

            table.add_row(
                result["spec_name"],
                f"[{valid_style}]{valid_icon}[/{valid_style}]",
                score_str,
                str(missing_count) if missing_count > 0 else "-"
            )

        console.print(table)

    # Detailed results
    for result in results:
        console.print(f"\n[bold cyan]═══ {result['spec_name']} ═══[/bold cyan]")

        # Status
        if result["valid"]:
            console.print("[green]✓ Valid - All required sections present[/green]")
        else:
            console.print("[red]✗ Invalid - Missing required sections[/red]")

        # Sections info
        console.print(f"\n[bold]Structure:[/bold]")
        console.print(f"  [green]✓ Required:[/green] {', '.join(result['sections']['required']) if result['sections']['required'] else 'None'}")

        if result["sections"]["missing_required"]:
            console.print(f"  [red]✗ Missing Required:[/red] {', '.join(result['sections']['missing_required'])}")

        if result["sections"]["optional"]:
            console.print(f"  [yellow]+ Optional:[/yellow] {', '.join(result['sections']['optional'])}")

        # Analysis
        console.print(f"\n[bold]Quality Analysis:[/bold]")
        console.print(Markdown(result["analysis"]))

    # Exit with error if strict mode and any invalid
    if strict and not all(r["valid"] for r in results):
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Validate Auto-Claude spec files for completeness and quality",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate a specific spec
  %(prog)s --spec-dir .auto-claude/specs/001-auth

  # Validate all specs
  %(prog)s --specs-root .auto-claude/specs

  # Strict mode (fail on warnings)
  %(prog)s --spec-dir .auto-claude/specs/001-auth --strict

  # JSON output
  %(prog)s --spec-dir .auto-claude/specs/001-auth --json
        """
    )

    parser.add_argument(
        "--spec-dir",
        type=Path,
        help="Path to specific spec directory to validate"
    )
    parser.add_argument(
        "--specs-root",
        type=Path,
        help="Path to root specs directory (validate all)"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with error if any spec is invalid"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format"
    )

    args = parser.parse_args()

    if not args.spec_dir and not args.specs_root:
        console = Console()
        console.print(
            "[red]Error:[/red] Must provide either --spec-dir or --specs-root",
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
        spec_dirs = []

        # Collect spec directories
        if args.spec_dir:
            if not args.spec_dir.exists():
                raise FileNotFoundError(f"Spec directory not found: {args.spec_dir}")
            spec_dirs.append(args.spec_dir)

        if args.specs_root:
            if not args.specs_root.exists():
                raise FileNotFoundError(f"Specs root directory not found: {args.specs_root}")
            # Find all subdirectories with spec.md
            for subdir in args.specs_root.iterdir():
                if subdir.is_dir() and (subdir / "spec.md").exists():
                    spec_dirs.append(subdir)

        if not spec_dirs:
            raise ValueError("No spec directories found to validate")

        # Validate each spec
        results = []
        console = Console()

        for spec_dir in spec_dirs:
            spec_file = spec_dir / "spec.md"
            if not spec_file.exists():
                continue

            if not args.json:
                console.print(f"[dim]Validating {spec_dir.name}...[/dim]")

            spec_content = spec_file.read_text()
            sections = check_structure(spec_content)

            result = validate_spec(
                spec_content,
                spec_dir.name,
                api_key,
                sections
            )
            results.append(result)

        # Display results
        format_output(results, args.json, args.strict)

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

#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "anthropic>=0.45.2",
#   "rich>=13.7.0",
# ]
# ///

"""
Prompt Linter SFA - Lint and improve Auto-Claude agent prompts.

This single-file agent analyzes prompt files (from apps/backend/prompts/) and
provides suggestions for clarity, completeness, and best practices.

/// Example Usage
# Lint a specific prompt
uv run sfa_prompt_linter_anthropic_v1.py \
  --prompt-file apps/backend/prompts/coder.md

# Lint all prompts in directory
uv run sfa_prompt_linter_anthropic_v1.py \
  --prompt-dir apps/backend/prompts

# Get detailed suggestions
uv run sfa_prompt_linter_anthropic_v1.py \
  --prompt-file apps/backend/prompts/coder.md \
  --detailed

# JSON output
uv run sfa_prompt_linter_anthropic_v1.py \
  --prompt-file apps/backend/prompts/coder.md \
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


LINTING_CRITERIA = """
Analyze this Auto-Claude agent prompt against these criteria:

1. **Clarity & Structure**
   - Clear role definition
   - Well-organized sections
   - Logical flow of instructions

2. **Completeness**
   - Success criteria defined
   - Edge cases covered
   - Error handling guidance

3. **Tool Usage**
   - Appropriate tool permissions
   - Clear tool usage examples
   - Security considerations

4. **Best Practices**
   - Concise yet comprehensive
   - Actionable instructions
   - Avoids ambiguity

5. **Agent-Specific**
   - Appropriate for agent type (planner/coder/qa)
   - Context-aware
   - Aligns with Auto-Claude patterns

Provide:
- **Score**: 0-100
- **Strengths**: What works well
- **Issues**: Problems found (if any)
- **Suggestions**: Concrete improvements
"""


def lint_prompt(prompt_content: str, prompt_name: str, api_key: str, detailed: bool = False) -> Dict[str, Any]:
    """Use Claude to lint and analyze a prompt."""
    client = Anthropic(api_key=api_key)

    analysis_prompt = f"""{LINTING_CRITERIA}

**Prompt Name**: {prompt_name}

**Prompt Content**:
```markdown
{prompt_content}
```

{"Provide a detailed analysis with specific line references and examples." if detailed else "Provide a concise analysis focusing on the most important issues."}
"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=3000,
        messages=[{"role": "user", "content": analysis_prompt}]
    )

    response_text = message.content[0].text

    # Parse score if present
    score = None
    for line in response_text.splitlines():
        if "score" in line.lower() and any(char.isdigit() for char in line):
            import re
            match = re.search(r'\d+', line)
            if match:
                score = int(match.group())
                break

    return {
        "prompt_name": prompt_name,
        "score": score,
        "analysis": response_text,
        "word_count": len(prompt_content.split()),
        "line_count": len(prompt_content.splitlines())
    }


def format_output(results: List[Dict[str, Any]], json_output: bool) -> None:
    """Format and display the linting results."""
    if json_output:
        print(json.dumps(results, indent=2))
        return

    console = Console()

    # Header
    console.print(Panel(
        f"[cyan]Prompts Analyzed:[/cyan] {len(results)}",
        title="[bold]Prompt Linter Results",
        border_style="blue"
    ))

    # Summary table
    if len(results) > 1:
        console.print("\n[bold green]Summary[/bold green]")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Prompt", style="cyan")
        table.add_column("Score", justify="center", style="yellow")
        table.add_column("Words", justify="right", style="dim")
        table.add_column("Lines", justify="right", style="dim")

        for result in sorted(results, key=lambda x: x.get("score") or 0, reverse=True):
            score_str = str(result["score"]) if result["score"] else "N/A"
            score_style = "green" if (result["score"] or 0) >= 80 else "yellow" if (result["score"] or 0) >= 60 else "red"

            table.add_row(
                result["prompt_name"],
                f"[{score_style}]{score_str}[/{score_style}]",
                str(result["word_count"]),
                str(result["line_count"])
            )

        console.print(table)

    # Detailed analysis for each prompt
    for result in results:
        console.print(f"\n[bold cyan]═══ {result['prompt_name']} ═══[/bold cyan]")

        # Metadata
        console.print(f"[dim]Words: {result['word_count']} | Lines: {result['line_count']} | Score: {result['score'] or 'N/A'}[/dim]\n")

        # Analysis
        console.print(Markdown(result["analysis"]))


def main():
    parser = argparse.ArgumentParser(
        description="Lint and improve Auto-Claude agent prompts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Lint a specific prompt
  %(prog)s --prompt-file apps/backend/prompts/coder.md

  # Lint all prompts
  %(prog)s --prompt-dir apps/backend/prompts

  # Detailed analysis
  %(prog)s --prompt-file apps/backend/prompts/coder.md --detailed

  # JSON output
  %(prog)s --prompt-file apps/backend/prompts/coder.md --json
        """
    )

    parser.add_argument(
        "--prompt-file",
        type=Path,
        help="Path to specific prompt file to lint"
    )
    parser.add_argument(
        "--prompt-dir",
        type=Path,
        help="Path to directory containing prompts to lint"
    )
    parser.add_argument(
        "--detailed",
        action="store_true",
        help="Provide detailed analysis with specific suggestions"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format"
    )

    args = parser.parse_args()

    if not args.prompt_file and not args.prompt_dir:
        console = Console()
        console.print(
            "[red]Error:[/red] Must provide either --prompt-file or --prompt-dir",
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
        prompt_files = []

        # Collect prompt files
        if args.prompt_file:
            if not args.prompt_file.exists():
                raise FileNotFoundError(f"Prompt file not found: {args.prompt_file}")
            prompt_files.append(args.prompt_file)

        if args.prompt_dir:
            if not args.prompt_dir.exists():
                raise FileNotFoundError(f"Prompt directory not found: {args.prompt_dir}")
            prompt_files.extend(args.prompt_dir.glob("*.md"))

        if not prompt_files:
            raise ValueError("No prompt files found to analyze")

        # Analyze each prompt
        results = []
        console = Console()

        for prompt_file in prompt_files:
            if not args.json:
                console.print(f"[dim]Analyzing {prompt_file.name}...[/dim]")

            prompt_content = prompt_file.read_text()
            result = lint_prompt(
                prompt_content,
                prompt_file.stem,
                api_key,
                args.detailed
            )
            results.append(result)

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

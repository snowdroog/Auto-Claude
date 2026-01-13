#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "anthropic>=0.45.2",
#   "rich>=13.7.0",
#   "toml>=0.10.2",
# ]
# ///

"""
Dependency Analyzer SFA - Analyze Python dependencies in Auto-Claude projects.

This single-file agent analyzes requirements.txt, pyproject.toml, and PEP 723
inline dependencies to provide insights about versions, conflicts, and security.

/// Example Usage
# Analyze project dependencies
uv run sfa_dependency_analyzer_anthropic_v1.py \
  --project-dir apps/backend

# Check for outdated packages
uv run sfa_dependency_analyzer_anthropic_v1.py \
  --project-dir apps/backend \
  --check-outdated

# Analyze SFA inline dependencies
uv run sfa_dependency_analyzer_anthropic_v1.py \
  --sfa-dir apps/backend/single-file-agents/agents

# JSON output
uv run sfa_dependency_analyzer_anthropic_v1.py \
  --project-dir apps/backend \
  --json
///
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from anthropic import Anthropic
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table


def parse_requirements_txt(file_path: Path) -> List[Dict[str, str]]:
    """Parse requirements.txt file."""
    if not file_path.exists():
        return []

    deps = []
    for line in file_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        # Parse package name and version
        match = re.match(r"([a-zA-Z0-9_-]+)([><=!]+)?(.+)?", line)
        if match:
            package, operator, version = match.groups()
            deps.append({
                "package": package,
                "version": version or "any",
                "operator": operator or "",
                "source": str(file_path.name)
            })

    return deps


def parse_pyproject_toml(file_path: Path) -> List[Dict[str, str]]:
    """Parse pyproject.toml dependencies."""
    if not file_path.exists():
        return []

    try:
        import toml
        data = toml.load(file_path)

        deps = []
        # Check project.dependencies
        if "project" in data and "dependencies" in data["project"]:
            for dep in data["project"]["dependencies"]:
                match = re.match(r"([a-zA-Z0-9_-]+)([><=!]+)?(.+)?", dep)
                if match:
                    package, operator, version = match.groups()
                    deps.append({
                        "package": package,
                        "version": version or "any",
                        "operator": operator or "",
                        "source": "pyproject.toml"
                    })

        return deps
    except ImportError:
        return []


def parse_sfa_dependencies(sfa_dir: Path) -> Dict[str, List[Dict[str, str]]]:
    """Parse PEP 723 inline dependencies from SFA files."""
    sfa_deps = {}

    for sfa_file in sfa_dir.glob("sfa_*.py"):
        deps = []
        content = sfa_file.read_text()

        # Extract dependencies block
        in_deps = False
        for line in content.splitlines():
            if "# dependencies = [" in line:
                in_deps = True
                continue
            if in_deps:
                if "# ]" in line:
                    break
                # Parse dependency line
                match = re.search(r'"([a-zA-Z0-9_-]+)([><=!]+)?(.+)?"', line)
                if match:
                    package, operator, version = match.groups()
                    deps.append({
                        "package": package,
                        "version": version or "any",
                        "operator": operator or "",
                        "source": sfa_file.name
                    })

        if deps:
            sfa_deps[sfa_file.name] = deps

    return sfa_deps


def analyze_dependencies_with_claude(
    deps_data: Dict[str, Any], api_key: str, check_outdated: bool = False
) -> str:
    """Use Claude to analyze dependencies and provide insights."""
    client = Anthropic(api_key=api_key)

    prompt = f"""Analyze the following Python dependencies and provide insights:

{json.dumps(deps_data, indent=2)}

Please provide:
1. **Summary**: Total packages, common versions
2. **Potential Conflicts**: Same package with different versions
3. **Version Patterns**: Use of version pinning vs ranges
4. **Security Concerns**: Very old versions (if obvious)
{"5. **Outdated Packages**: Packages that might be outdated" if check_outdated else ""}

Be concise and actionable. Focus on actual issues, not hypotheticals."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )

    return message.content[0].text


def format_output(
    project_deps: List[Dict[str, str]],
    sfa_deps: Dict[str, List[Dict[str, str]]],
    analysis: str,
    json_output: bool,
    project_dir: Optional[Path] = None
) -> None:
    """Format and display the output."""
    if json_output:
        result = {
            "project_dependencies": project_deps,
            "sfa_dependencies": sfa_deps,
            "analysis": analysis,
            "project_dir": str(project_dir) if project_dir else None
        }
        print(json.dumps(result, indent=2))
        return

    console = Console()

    # Header
    console.print(Panel(
        f"[cyan]Project:[/cyan] {project_dir.name if project_dir else 'SFA Analysis'}\n"
        f"[cyan]Total Dependencies:[/cyan] {len(project_deps) + sum(len(d) for d in sfa_deps.values())}",
        title="[bold]Dependency Analysis",
        border_style="blue"
    ))

    # Project dependencies table
    if project_deps:
        console.print("\n[bold green]Project Dependencies[/bold green]")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Package", style="cyan")
        table.add_column("Version", style="yellow")
        table.add_column("Source", style="dim")

        for dep in sorted(project_deps, key=lambda x: x["package"]):
            version_str = f"{dep['operator']}{dep['version']}" if dep['operator'] else dep['version']
            table.add_row(dep["package"], version_str, dep["source"])

        console.print(table)

    # SFA dependencies
    if sfa_deps:
        console.print("\n[bold green]SFA Dependencies[/bold green]")
        for sfa_name, deps in sorted(sfa_deps.items()):
            console.print(f"\n[cyan]{sfa_name}[/cyan]")
            for dep in deps:
                version_str = f"{dep['operator']}{dep['version']}" if dep['operator'] else dep['version']
                console.print(f"  • {dep['package']} {version_str}")

    # AI Analysis
    console.print("\n[bold green]Analysis[/bold green]")
    console.print(Markdown(analysis))


def main():
    parser = argparse.ArgumentParser(
        description="Analyze Python dependencies in Auto-Claude projects",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze project dependencies
  %(prog)s --project-dir apps/backend

  # Analyze SFA inline dependencies
  %(prog)s --sfa-dir apps/backend/single-file-agents/agents

  # Check for outdated packages
  %(prog)s --project-dir apps/backend --check-outdated

  # JSON output
  %(prog)s --project-dir apps/backend --json
        """
    )

    parser.add_argument(
        "--project-dir",
        type=Path,
        help="Path to project directory to analyze"
    )
    parser.add_argument(
        "--sfa-dir",
        type=Path,
        help="Path to SFA directory to analyze inline dependencies"
    )
    parser.add_argument(
        "--check-outdated",
        action="store_true",
        help="Check for outdated packages"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format"
    )

    args = parser.parse_args()

    if not args.project_dir and not args.sfa_dir:
        console = Console()
        console.print(
            "[red]Error:[/red] Must provide either --project-dir or --sfa-dir",
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
        project_deps = []
        sfa_deps = {}

        # Analyze project dependencies
        if args.project_dir:
            if not args.project_dir.exists():
                raise FileNotFoundError(f"Project directory not found: {args.project_dir}")

            # Parse requirements.txt
            req_file = args.project_dir / "requirements.txt"
            project_deps.extend(parse_requirements_txt(req_file))

            # Parse pyproject.toml
            pyproject_file = args.project_dir / "pyproject.toml"
            project_deps.extend(parse_pyproject_toml(pyproject_file))

        # Analyze SFA dependencies
        if args.sfa_dir:
            if not args.sfa_dir.exists():
                raise FileNotFoundError(f"SFA directory not found: {args.sfa_dir}")

            sfa_deps = parse_sfa_dependencies(args.sfa_dir)

        # Prepare data for analysis
        deps_data = {
            "project_dependencies": project_deps,
            "sfa_dependencies": sfa_deps
        }

        # Get Claude's analysis
        analysis = analyze_dependencies_with_claude(
            deps_data, api_key, args.check_outdated
        )

        # Display results
        format_output(
            project_deps,
            sfa_deps,
            analysis,
            args.json,
            args.project_dir
        )

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

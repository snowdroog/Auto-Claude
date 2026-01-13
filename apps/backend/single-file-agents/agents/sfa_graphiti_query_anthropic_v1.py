#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "anthropic>=0.45.2",
#   "rich>=13.7.0",
# ]
# ///

"""
Graphiti Query SFA - Query Graphiti memory system for session insights.

This single-file agent queries Graphiti's graph database to retrieve session
insights, patterns, and discoveries stored during Auto-Claude builds.

/// Example Usage
# Query for authentication patterns
uv run sfa_graphiti_query_anthropic_v1.py \
  --spec-dir .auto-claude/specs/001-auth \
  --query "What patterns were discovered about authentication?"

# List all insights
uv run sfa_graphiti_query_anthropic_v1.py \
  --spec-dir .auto-claude/specs/001-auth \
  --list-insights

# Query specific entity
uv run sfa_graphiti_query_anthropic_v1.py \
  --spec-dir .auto-claude/specs/001-auth \
  --query "Tell me about JWT implementation"

# JSON output
uv run sfa_graphiti_query_anthropic_v1.py \
  --spec-dir .auto-claude/specs/001-auth \
  --query "authentication patterns" \
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


def load_graphiti_data(spec_dir: Path) -> Dict[str, Any]:
    """Load Graphiti data from spec directory."""
    graphiti_dir = spec_dir / "graphiti"

    if not graphiti_dir.exists():
        raise FileNotFoundError(
            f"Graphiti directory not found in {spec_dir}. "
            "Graphiti memory may not be enabled for this spec."
        )

    # Try to find JSON exports or readable data
    data = {
        "entities": [],
        "relationships": [],
        "insights": [],
        "metadata": {}
    }

    # Look for common Graphiti export files
    entities_file = graphiti_dir / "entities.json"
    if entities_file.exists():
        try:
            data["entities"] = json.loads(entities_file.read_text())
        except json.JSONDecodeError:
            pass

    relationships_file = graphiti_dir / "relationships.json"
    if relationships_file.exists():
        try:
            data["relationships"] = json.loads(relationships_file.read_text())
        except json.JSONDecodeError:
            pass

    # Check for database files
    db_files = list(graphiti_dir.glob("*.db"))
    if db_files:
        data["metadata"]["database_files"] = [f.name for f in db_files]

    # Check for any JSON files
    json_files = list(graphiti_dir.glob("*.json"))
    data["metadata"]["available_files"] = [f.name for f in json_files]

    return data


def query_graphiti(
    graphiti_data: Dict[str, Any],
    query: str,
    spec_name: str,
    api_key: str
) -> str:
    """Use Claude to query Graphiti data."""
    client = Anthropic(api_key=api_key)

    # Prepare context
    context_parts = []

    if graphiti_data.get("entities"):
        context_parts.append(
            f"**Entities** ({len(graphiti_data['entities'])} found):\n"
            f"```json\n{json.dumps(graphiti_data['entities'][:10], indent=2)}\n```"
        )

    if graphiti_data.get("relationships"):
        context_parts.append(
            f"\n**Relationships** ({len(graphiti_data['relationships'])} found):\n"
            f"```json\n{json.dumps(graphiti_data['relationships'][:10], indent=2)}\n```"
        )

    if graphiti_data.get("insights"):
        context_parts.append(
            f"\n**Insights** ({len(graphiti_data['insights'])} found):\n"
            f"```json\n{json.dumps(graphiti_data['insights'], indent=2)}\n```"
        )

    context = "\n".join(context_parts) if context_parts else "No Graphiti data available."

    prompt = f"""You are querying the Graphiti memory system for spec: {spec_name}

**Available Graphiti Data:**
{context}

**User Query:** {query}

Analyze the Graphiti data and answer the user's query. If the data contains relevant information, provide specific insights. If not, explain what data is available and suggest better queries.

Be concise and focus on actionable information from the memory graph."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )

    return message.content[0].text


def list_insights(graphiti_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract and list all available insights."""
    insights = []

    # Check entities for insight-like information
    for entity in graphiti_data.get("entities", []):
        if isinstance(entity, dict):
            insights.append({
                "type": "entity",
                "name": entity.get("name", "Unknown"),
                "summary": entity.get("summary", entity.get("description", ""))
            })

    # Check for explicit insights
    for insight in graphiti_data.get("insights", []):
        if isinstance(insight, dict):
            insights.append({
                "type": "insight",
                "content": insight.get("content", insight.get("text", str(insight)))
            })

    return insights


def format_output(
    result: Optional[str],
    insights: Optional[List[Dict[str, Any]]],
    spec_name: str,
    graphiti_data: Dict[str, Any],
    json_output: bool
) -> None:
    """Format and display the query results."""
    if json_output:
        output = {
            "spec_name": spec_name,
            "result": result,
            "insights": insights,
            "metadata": graphiti_data.get("metadata", {})
        }
        print(json.dumps(output, indent=2))
        return

    console = Console()

    # Header
    console.print(Panel(
        f"[cyan]Spec:[/cyan] {spec_name}\n"
        f"[cyan]Entities:[/cyan] {len(graphiti_data.get('entities', []))}\n"
        f"[cyan]Relationships:[/cyan] {len(graphiti_data.get('relationships', []))}",
        title="[bold]Graphiti Memory Query",
        border_style="blue"
    ))

    # List insights mode
    if insights is not None:
        console.print("\n[bold green]Available Insights[/bold green]")

        if not insights:
            console.print("[yellow]No insights found in Graphiti memory[/yellow]")
        else:
            for i, insight in enumerate(insights, 1):
                if insight["type"] == "entity":
                    console.print(f"\n[cyan]{i}. Entity: {insight['name']}[/cyan]")
                    if insight["summary"]:
                        console.print(f"   {insight['summary']}")
                elif insight["type"] == "insight":
                    console.print(f"\n[cyan]{i}. Insight[/cyan]")
                    console.print(f"   {insight['content']}")

    # Query result mode
    if result:
        console.print("\n[bold green]Query Result[/bold green]")
        console.print(Markdown(result))

    # Metadata
    if graphiti_data.get("metadata"):
        console.print("\n[bold dim]Metadata[/bold dim]")
        for key, value in graphiti_data["metadata"].items():
            console.print(f"[dim]{key}: {value}[/dim]")


def main():
    parser = argparse.ArgumentParser(
        description="Query Graphiti memory system for session insights",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Query for patterns
  %(prog)s --spec-dir .auto-claude/specs/001-auth --query "authentication patterns"

  # List all insights
  %(prog)s --spec-dir .auto-claude/specs/001-auth --list-insights

  # Query specific entity
  %(prog)s --spec-dir .auto-claude/specs/001-auth --query "JWT implementation"

  # JSON output
  %(prog)s --spec-dir .auto-claude/specs/001-auth --query "patterns" --json
        """
    )

    parser.add_argument(
        "--spec-dir",
        type=Path,
        required=True,
        help="Path to spec directory containing Graphiti data"
    )
    parser.add_argument(
        "--query",
        type=str,
        help="Natural language query about the memory data"
    )
    parser.add_argument(
        "--list-insights",
        action="store_true",
        help="List all available insights"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format"
    )

    args = parser.parse_args()

    if not args.query and not args.list_insights:
        console = Console()
        console.print(
            "[red]Error:[/red] Must provide either --query or --list-insights",
            style="bold"
        )
        sys.exit(1)

    # Get API key (only needed for queries, not listing)
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if args.query and not api_key:
        console = Console()
        console.print(
            "[red]Error:[/red] ANTHROPIC_API_KEY environment variable not set",
            style="bold"
        )
        sys.exit(1)

    try:
        # Validate spec directory
        if not args.spec_dir.exists():
            raise FileNotFoundError(f"Spec directory not found: {args.spec_dir}")

        # Load Graphiti data
        graphiti_data = load_graphiti_data(args.spec_dir)

        result = None
        insights = None

        # Handle list insights
        if args.list_insights:
            insights = list_insights(graphiti_data)

        # Handle query
        if args.query:
            result = query_graphiti(
                graphiti_data,
                args.query,
                args.spec_dir.name,
                api_key
            )

        # Display results
        format_output(
            result,
            insights,
            args.spec_dir.name,
            graphiti_data,
            args.json
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

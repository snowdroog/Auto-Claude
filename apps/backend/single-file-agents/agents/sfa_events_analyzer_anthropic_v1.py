#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "anthropic>=0.45.2",
#   "rich>=13.7.0",
#   "duckdb>=1.1.0",
# ]
# ///

"""
Events Analyzer SFA - Query Auto-Claude events database using natural language.

This single-file agent uses Claude to answer questions about session data
stored in the events.db DuckDB database. It translates natural language
queries into SQL and provides analyzed results.

/// Example Usage
# Query recent sessions
uv run sfa_events_analyzer_anthropic_v1.py \
  --db .auto-claude/events.db \
  --prompt "Show me all sessions from the last 7 days"

# Find failures
uv run sfa_events_analyzer_anthropic_v1.py \
  --db .auto-claude/events.db \
  --prompt "Which sessions failed during QA?"

# Performance analysis
uv run sfa_events_analyzer_anthropic_v1.py \
  --db .auto-claude/events.db \
  --prompt "Compare planner vs coder session durations"

# JSON output
uv run sfa_events_analyzer_anthropic_v1.py \
  --db .auto-claude/events.db \
  --prompt "Show session costs" \
  --json
///
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import duckdb
from anthropic import Anthropic
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table


def get_database_schema(db_path: Path) -> Dict[str, List[Dict[str, str]]]:
    """Get schema information from the events database."""
    conn = duckdb.connect(str(db_path), read_only=True)

    try:
        # Get all tables
        tables_result = conn.execute("SHOW TABLES").fetchall()
        tables = [row[0] for row in tables_result]

        schema = {}
        for table in tables:
            # Get columns for each table
            columns_result = conn.execute(
                f"PRAGMA table_info('{table}')"
            ).fetchall()
            schema[table] = [
                {"name": col[1], "type": col[2]} for col in columns_result
            ]

        return schema
    finally:
        conn.close()


def execute_sql_query(db_path: Path, sql: str) -> List[Dict[str, Any]]:
    """Execute SQL query and return results as list of dicts."""
    conn = duckdb.connect(str(db_path), read_only=True)

    try:
        result = conn.execute(sql).fetchall()
        columns = [desc[0] for desc in conn.description] if conn.description else []

        # Convert to list of dicts
        return [dict(zip(columns, row)) for row in result]
    finally:
        conn.close()


def analyze_query(
    prompt: str, schema: Dict[str, List[Dict[str, str]]], api_key: str
) -> Dict[str, Any]:
    """Use Claude to translate natural language to SQL and analyze results."""
    client = Anthropic(api_key=api_key)

    # Format schema for Claude
    schema_text = "# Database Schema\n\n"
    for table, columns in schema.items():
        schema_text += f"## {table}\n"
        for col in columns:
            schema_text += f"- {col['name']} ({col['type']})\n"
        schema_text += "\n"

    # Ask Claude to generate SQL
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        messages=[
            {
                "role": "user",
                "content": f"""You are analyzing an Auto-Claude events database. The user wants to query the database using natural language.

{schema_text}

User Query: {prompt}

Please provide:
1. A SQL query to answer the user's question
2. A brief explanation of what the query does

Format your response as:
```sql
[SQL QUERY HERE]
```

Explanation: [Brief explanation]

Important:
- Use DuckDB SQL syntax
- Only query, don't modify data
- Be specific about what data is being retrieved
- Use LIMIT to prevent large result sets (default 100 rows unless user asks for more)""",
            }
        ],
    )

    response_text = message.content[0].text

    # Extract SQL from response
    sql_query = None
    if "```sql" in response_text:
        sql_start = response_text.find("```sql") + 6
        sql_end = response_text.find("```", sql_start)
        sql_query = response_text[sql_start:sql_end].strip()

    return {"sql": sql_query, "explanation": response_text}


def analyze_results(
    prompt: str, results: List[Dict[str, Any]], api_key: str
) -> str:
    """Use Claude to analyze and explain the query results."""
    client = Anthropic(api_key=api_key)

    # Format results for Claude (limit to first 50 rows for analysis)
    results_text = json.dumps(results[:50], indent=2, default=str)

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[
            {
                "role": "user",
                "content": f"""Analyze these query results and provide insights.

Original Query: {prompt}

Results (first 50 rows):
```json
{results_text}
```

Total Rows: {len(results)}

Provide:
1. Key findings from the data
2. Any patterns or trends
3. Relevant statistics
4. Actionable insights

Keep the analysis concise and focused on what's important.""",
            }
        ],
    )

    return message.content[0].text


def format_results_table(results: List[Dict[str, Any]], max_rows: int = 20) -> Table:
    """Format query results as a Rich table."""
    if not results:
        table = Table(title="Query Results")
        table.add_column("Status")
        table.add_row("No results found")
        return table

    # Create table with columns from first result
    table = Table(title=f"Query Results ({len(results)} rows)")
    columns = list(results[0].keys())

    for col in columns:
        table.add_column(col, overflow="fold")

    # Add rows (limit to max_rows for display)
    for row in results[:max_rows]:
        table.add_row(*[str(row.get(col, "")) for col in columns])

    if len(results) > max_rows:
        table.add_row(*[f"... ({len(results) - max_rows} more rows)" for _ in columns])

    return table


def format_output(
    prompt: str,
    sql: str,
    explanation: str,
    results: List[Dict[str, Any]],
    analysis: str,
    json_output: bool,
) -> None:
    """Format and display the output."""
    if json_output:
        output = {
            "query": prompt,
            "sql": sql,
            "explanation": explanation,
            "results": results,
            "analysis": analysis,
            "row_count": len(results),
        }
        print(json.dumps(output, indent=2, default=str))
        return

    console = Console()

    # Display query info
    console.print(
        Panel(
            f"[cyan]Query:[/cyan] {prompt}\n[cyan]Rows:[/cyan] {len(results)}",
            title="[bold]Events Analysis",
            border_style="blue",
        )
    )

    # Display SQL
    console.print("\n[bold yellow]Generated SQL:[/bold yellow]")
    console.print(Panel(sql, border_style="yellow"))

    # Display results table
    console.print("\n[bold green]Results:[/bold green]")
    table = format_results_table(results, max_rows=20)
    console.print(table)

    # Display analysis
    if analysis:
        console.print("\n[bold magenta]Analysis:[/bold magenta]")
        console.print(Markdown(analysis))


def main():
    parser = argparse.ArgumentParser(
        description="Query Auto-Claude events database using natural language",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Query recent sessions
  %(prog)s --db .auto-claude/events.db --prompt "Show sessions from last 7 days"

  # Find failures
  %(prog)s --db .auto-claude/events.db --prompt "Which sessions failed during QA?"

  # Performance analysis
  %(prog)s --db .auto-claude/events.db --prompt "Compare planner vs coder durations"

  # JSON output
  %(prog)s --db .auto-claude/events.db --prompt "Show costs" --json
        """,
    )

    parser.add_argument(
        "--db",
        type=Path,
        default=".auto-claude/events.db",
        help="Path to events database (default: .auto-claude/events.db)",
    )
    parser.add_argument(
        "--prompt",
        type=str,
        required=True,
        help="Natural language query",
    )
    parser.add_argument(
        "--json", action="store_true", help="Output in JSON format"
    )
    parser.add_argument(
        "--no-analysis",
        action="store_true",
        help="Skip AI analysis of results (faster)",
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
        # Get database schema
        schema = get_database_schema(args.db)

        # Analyze query and generate SQL
        result = analyze_query(args.prompt, schema, api_key)
        sql = result["sql"]
        explanation = result["explanation"]

        if not sql:
            console = Console()
            console.print(
                "[red]Error:[/red] Could not generate SQL from query",
                style="bold",
            )
            console.print(f"\nClaude's response:\n{explanation}")
            sys.exit(1)

        # Execute SQL
        query_results = execute_sql_query(args.db, sql)

        # Analyze results (unless skipped)
        analysis = ""
        if not args.no_analysis and query_results:
            analysis = analyze_results(args.prompt, query_results, api_key)

        # Display results
        format_output(
            args.prompt, sql, explanation, query_results, analysis, args.json
        )

    except Exception as e:
        console = Console()
        console.print(f"[red]Error:[/red] {e}", style="bold")
        if not args.json:
            console.print_exception()
        sys.exit(1)


if __name__ == "__main__":
    main()

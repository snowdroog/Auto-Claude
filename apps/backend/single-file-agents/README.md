# Single-File Agents (SFAs)

Self-contained Python agents for quick analysis and utility tasks in Auto-Claude.

## Overview

Single-File Agents (SFAs) are specialized Python scripts that follow the UV + PEP 723 pattern:
- **Self-contained**: All dependencies embedded in the script
- **No venv needed**: UV manages dependencies automatically
- **Quick execution**: < 30 seconds typical runtime
- **Focused**: One task, done well

## Available Agents

### Spec & Planning

| Agent | Purpose | Usage |
|-------|---------|-------|
| `sfa_spec_query_anthropic_v1.py` | Query spec.md files | `--spec-dir PATH --query "text"` |
| `sfa_spec_validator_anthropic_v1.py` | Validate spec completeness | `--spec-dir PATH` |
| `sfa_plan_analyzer_anthropic_v1.py` | Analyze implementation plans | `--plan-file PATH` |
| `sfa_qa_report_analyzer_anthropic_v1.py` | Analyze QA reports | `--report-file PATH` |

### Project & Code Analysis

| Agent | Purpose | Usage |
|-------|---------|-------|
| `sfa_dependency_analyzer_anthropic_v1.py` | Analyze Python dependencies | `--project-dir PATH` |
| `sfa_prompt_linter_anthropic_v1.py` | Lint agent prompts | `--prompt-file PATH` |

### Memory & Knowledge

| Agent | Purpose | Usage |
|-------|---------|-------|
| `sfa_graphiti_query_anthropic_v1.py` | Query Graphiti memory | `--spec-dir PATH --query "text"` |

### Observability & Analytics

| Agent | Purpose | Usage |
|-------|---------|-------|
| `sfa_events_analyzer_anthropic_v1.py` | Natural language DB queries | `--db PATH --prompt "query"` |
| `sfa_session_cost_tracker_anthropic_v1.py` | Token usage and cost tracking | `--db PATH --days 7` |
| `sfa_loop_detector_report_anthropic_v1.py` | Detect infinite loops | `--db PATH --days 7` |
| `sfa_failure_investigator_anthropic_v1.py` | Root cause analysis | `--db PATH --session-id ID` |

## Usage

### Direct Execution

```bash
# Query a spec file
uv run apps/backend/single-file-agents/agents/sfa_spec_query_anthropic_v1.py \
  --spec-dir .auto-claude/specs/001-auth \
  --query "What are the acceptance criteria?"

# Validate spec completeness
uv run apps/backend/single-file-agents/agents/sfa_spec_validator_anthropic_v1.py \
  --spec-dir .auto-claude/specs/001-auth

# Analyze implementation plan
uv run apps/backend/single-file-agents/agents/sfa_plan_analyzer_anthropic_v1.py \
  --plan-file .auto-claude/specs/001-auth/implementation_plan.json

# Analyze QA report
uv run apps/backend/single-file-agents/agents/sfa_qa_report_analyzer_anthropic_v1.py \
  --report-file .auto-claude/specs/001-auth/qa_report.md

# Analyze project dependencies
uv run apps/backend/single-file-agents/agents/sfa_dependency_analyzer_anthropic_v1.py \
  --project-dir apps/backend

# Lint agent prompts
uv run apps/backend/single-file-agents/agents/sfa_prompt_linter_anthropic_v1.py \
  --prompt-file apps/backend/prompts/coder.md

# Query Graphiti memory
uv run apps/backend/single-file-agents/agents/sfa_graphiti_query_anthropic_v1.py \
  --spec-dir .auto-claude/specs/001-auth \
  --query "What patterns were discovered?"

# Analyze events database with natural language
uv run apps/backend/single-file-agents/agents/sfa_events_analyzer_anthropic_v1.py \
  --db .auto-claude/events.db \
  --prompt "Show me all failed sessions from the last 7 days"

# Track session costs
uv run apps/backend/single-file-agents/agents/sfa_session_cost_tracker_anthropic_v1.py \
  --db .auto-claude/events.db \
  --days 7

# Detect loop patterns
uv run apps/backend/single-file-agents/agents/sfa_loop_detector_report_anthropic_v1.py \
  --db .auto-claude/events.db \
  --days 7 \
  --severity high

# Investigate failed session
uv run apps/backend/single-file-agents/agents/sfa_failure_investigator_anthropic_v1.py \
  --db .auto-claude/events.db \
  --session-id abc123
```

### Via Claude Code Skill

Say: "use sfa to query spec 001 for acceptance criteria"

Claude Code will execute the appropriate SFA automatically.

## Agent Details

### sfa_events_analyzer_anthropic_v1.py

**Natural Language Database Queries**

Translate natural language queries into SQL and analyze results from the events database.

```bash
# Find recent failed sessions
uv run sfa_events_analyzer_anthropic_v1.py \
  --db .auto-claude/events.db \
  --prompt "Which sessions failed during QA in the last week?"

# Compare performance
uv run sfa_events_analyzer_anthropic_v1.py \
  --db .auto-claude/events.db \
  --prompt "Compare planner vs coder session durations"

# JSON output
uv run sfa_events_analyzer_anthropic_v1.py \
  --db .auto-claude/events.db \
  --prompt "Show session costs" \
  --json
```

**Features:**
- Natural language to SQL translation
- AI-powered result analysis
- Schema-aware query generation
- Support for complex aggregations

### sfa_session_cost_tracker_anthropic_v1.py

**Token Usage and Cost Analysis**

Track API costs, token usage, and efficiency metrics across sessions.

```bash
# Last 7 days costs
uv run sfa_session_cost_tracker_anthropic_v1.py \
  --db .auto-claude/events.db \
  --days 7

# Specific spec costs
uv run sfa_session_cost_tracker_anthropic_v1.py \
  --db .auto-claude/events.db \
  --spec-id 001

# Cost breakdown by agent/model
uv run sfa_session_cost_tracker_anthropic_v1.py \
  --db .auto-claude/events.db \
  --days 30 \
  --no-insights
```

**Features:**
- Cost calculation for all Claude models (Opus, Sonnet, Haiku)
- Breakdown by agent type, model, and spec
- Token usage statistics (input, output, thinking)
- Cost optimization insights

**Pricing (as of 2026-01):**
- Opus 4: $15/M input, $75/M output
- Sonnet 4/4.5: $3/M input, $15/M output
- Haiku 4: $0.80/M input, $4/M output

### sfa_loop_detector_report_anthropic_v1.py

**Infinite Loop and Stuck State Detection**

Analyze tool call patterns to identify loops and inefficient behavior.

```bash
# Detect loops in recent sessions
uv run sfa_loop_detector_report_anthropic_v1.py \
  --db .auto-claude/events.db \
  --days 7

# High severity only
uv run sfa_loop_detector_report_anthropic_v1.py \
  --db .auto-claude/events.db \
  --days 7 \
  --severity high

# Analyze specific session
uv run sfa_loop_detector_report_anthropic_v1.py \
  --db .auto-claude/events.db \
  --session-id abc123
```

**Detection Patterns:**
- **Repeated Sequences**: Same 3-tool sequence occurring 3+ times
- **File Operation Loops**: Excessive Read/Edit cycles on same file (5+ operations)
- **Long-Running Sessions**: >50 tool calls or >30 minutes duration

**Severity Levels:**
- **High**: 5+ repetitions, 8+ file ops, or >60 minutes
- **Medium**: 3-4 repetitions, 4-7 file ops, or 30-60 minutes
- **Low**: Minor inefficiencies

### sfa_failure_investigator_anthropic_v1.py

**Root Cause Analysis for Failed Sessions**

Investigate failed sessions with timeline analysis and recovery recommendations.

```bash
# Investigate specific failure
uv run sfa_failure_investigator_anthropic_v1.py \
  --db .auto-claude/events.db \
  --session-id abc123

# Find recent failures
uv run sfa_failure_investigator_anthropic_v1.py \
  --db .auto-claude/events.db \
  --days 7

# Failures by agent type
uv run sfa_failure_investigator_anthropic_v1.py \
  --db .auto-claude/events.db \
  --days 7 \
  --agent-type coder
```

**Analysis Includes:**
- Event timeline leading to failure
- Tool call patterns before failure
- Root cause hypothesis
- Similar failure detection
- Recovery steps
- Impact assessment (time, cost, scope)

## Requirements

- **UV installed**: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **ANTHROPIC_API_KEY**: Set in environment or `.env` file
- **Python 3.12+**: Managed automatically by UV

## Creating New SFAs

Follow the template pattern:

```python
#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "anthropic>=0.45.2",
#   "rich>=13.7.0",
# ]
# ///

"""
Brief description of what this SFA does.

/// Example Usage
uv run sfa_name_anthropic_v1.py --arg1 value --arg2 value
///
"""

import argparse
from anthropic import Anthropic
from rich.console import Console

def main():
    parser = argparse.ArgumentParser(description="Your SFA description")
    parser.add_argument("--arg1", required=True, help="Argument description")
    args = parser.parse_args()

    console = Console()
    # Your logic here

if __name__ == "__main__":
    main()
```

## Best Practices

1. **Keep it focused**: One clear purpose per SFA
2. **Rich output**: Use Rich library for beautiful terminal formatting
3. **CLI arguments**: Use argparse for clear interface
4. **Error handling**: Graceful failures with helpful messages
5. **Documentation**: Include usage examples in docstring
6. **JSON mode**: Support `--json` flag for machine-readable output

## Integration

SFAs complement Auto-Claude's core agents:
- **Core agents**: Multi-module, complex workflows, state management
- **SFAs**: Quick analysis, utilities, single-purpose tasks

Use SFAs when:
- You need quick information (< 30 seconds)
- Task is well-scoped and standalone
- No persistent state needed
- Analysis doesn't require multi-step orchestration

## Roadmap

**Phase 2 (Weeks 3-4)**: Initial 6 SFAs ✅ **COMPLETED**
- [x] sfa_spec_query_anthropic_v1.py
- [x] sfa_plan_analyzer_anthropic_v1.py
- [x] sfa_session_cost_tracker_anthropic_v1.py
- [x] sfa_graphiti_query_anthropic_v1.py
- [x] sfa_qa_report_analyzer_anthropic_v1.py
- [ ] sfa_worktree_manager_anthropic_v1.py (deferred)

**Phase 4 (Extended)**: Development Tools SFAs ✅ **COMPLETED**
- [x] sfa_dependency_analyzer_anthropic_v1.py
- [x] sfa_prompt_linter_anthropic_v1.py
- [x] sfa_spec_validator_anthropic_v1.py

**Phase 5 (Weeks 9-10)**: Archon Integration SFAs
- [ ] sfa_archon_task_query_anthropic_v1.py
- [ ] sfa_archon_rag_researcher_anthropic_v1.py
- [ ] sfa_archon_project_reporter_anthropic_v1.py

**Phase 6 (Weeks 11-12)**: Observability SFAs ✅ **COMPLETED**
- [x] sfa_events_analyzer_anthropic_v1.py
- [x] sfa_session_cost_tracker_anthropic_v1.py
- [x] sfa_loop_detector_report_anthropic_v1.py
- [x] sfa_failure_investigator_anthropic_v1.py

## Resources

- [SFA Development Guide (Archon)](../../../.claude/skills/single-file-agents/README.md)
- [UV Documentation](https://docs.astral.sh/uv/)
- [PEP 723 - Inline Script Metadata](https://peps.python.org/pep-0723/)
- [Rich Library](https://github.com/Textualize/rich)

# Single-File Agents Skill

Run specialized single-file agents (SFAs) for analysis and utility tasks.

## Sub-Agent Integration

This skill provides direct access to SFA execution. SFAs are used by other sub-agents, particularly:
- **session-analytics-agent** - Uses SFAs for cost tracking, pattern detection, failure investigation
- **autonomous-builder-agent** - Can use SFAs for pre-implementation research
- **qa-loop-agent** - Can use SFAs for validation analysis

**How it works:**
- User requests SFA execution → Claude detects specific SFA needed
- Claude executes SFA via UV (self-contained, no venv needed)
- SFA returns analysis results directly to user
- Results can be stored in Archon for future reference

## Quick Start

**Trigger phrases:**
- "use sfa to query X"
- "run agent for Y"
- "analyze with sfa"

**What it does:**
Executes specialized single-file Python agents that perform focused analysis or utility tasks.

## Available Agents

| SFA | Purpose | Usage |
|-----|---------|-------|
| `sfa_spec_query` | Query spec files | `--spec-dir PATH --query "text"` |
| `sfa_plan_analyzer` | Analyze plans | `--plan-file PATH` |
| `sfa_session_cost_tracker` | Cost analysis | `--days N` |
| `sfa_graphiti_query` | Memory queries | `--spec-dir PATH --query "text"` |
| `sfa_qa_report_analyzer` | QA report parsing | `--report-file PATH` |
| `sfa_worktree_manager` | Worktree management | `--action list/create/delete` |

## Usage Examples

### Query Spec for Acceptance Criteria

```bash
uv run apps/backend/single-file-agents/agents/sfa_spec_query_anthropic_v1.py \
  --spec-dir .auto-claude/specs/001-auth \
  --query "What are the acceptance criteria?"
```

### Analyze Session Costs

```bash
uv run apps/backend/single-file-agents/agents/sfa_session_cost_tracker_anthropic_v1.py \
  --days 7
```

### Query Graphiti Memory

```bash
uv run apps/backend/single-file-agents/agents/sfa_graphiti_query_anthropic_v1.py \
  --spec-dir .auto-claude/specs/001-auth \
  --query "authentication patterns"
```

## SFA Benefits

- **Self-contained**: No venv management needed
- **Fast**: < 30 seconds execution
- **Focused**: One task, done well
- **Shareable**: Just share the .py file
- **Customizable**: Easy to create new ones

## Requirements

- UV installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- ANTHROPIC_API_KEY in environment
- Python 3.12+ (managed by UV automatically)

## Creating Custom SFAs

See SFA Development Guide in Archon (Document ID: 5dd92e00-7741-42c3-81b9-d21ec500b02b) for complete template and patterns.

## Related

- **auto-claude-spec** - Create specs (SFAs can then query them)
- **auto-claude-build** - Build specs (SFAs can analyze results)
- **observability** - Session analytics (uses SFAs internally via session-analytics-agent)

## Technical Details

**Agent Integration:** Used by session-analytics-agent, autonomous-builder-agent, qa-loop-agent
**CLI Pattern:** Direct UV execution (`uv run path/to/sfa.py`)
**Model:** Haiku (fast, efficient analysis)
**Location:** `apps/backend/single-file-agents/agents/`
**Pattern:** UV + PEP 723 (self-contained dependencies)

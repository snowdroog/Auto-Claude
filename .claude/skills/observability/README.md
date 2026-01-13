# Observability Skill

Session analytics, cost tracking, and pattern detection for Auto-Claude.

## Sub-Agent Integration

This skill invokes the **session-analytics-agent** (`.claude/agents/session-analytics-agent.md`) which analyzes Auto-Claude session data using SFAs for cost tracking, performance metrics, pattern detection, and failure investigation.

**How it works:**
- User requests analytics → Claude delegates to session-analytics-agent
- Agent selects appropriate SFA (cost tracker, loop detector, failure investigator, events analyzer)
- Agent executes SFA via UV with relevant parameters
- Agent provides insights, comparisons, and recommendations
- Agent can store findings in Archon for long-term tracking

## Quick Start

**Trigger phrases:**
- "analyze sessions"
- "how much did X cost?"
- "session analytics for spec Y"
- "performance metrics"

**What it does:**
Analyzes Auto-Claude sessions using OTEL traces, hook logs, and events database to provide cost, performance, and quality insights.

## Key Analysis Tools

### Cost Tracking

```bash
# Last 7 days costs
uv run apps/backend/single-file-agents/agents/sfa_session_cost_tracker_anthropic_v1.py --days 7

# Specific spec
uv run apps/backend/single-file-agents/agents/sfa_session_cost_tracker_anthropic_v1.py \
  --spec-id 001 \
  --breakdown
```

### Natural Language Queries

```bash
# Query events database
uv run apps/backend/single-file-agents/agents/sfa_events_analyzer_anthropic_v1.py \
  --db .auto-claude/events.db \
  --prompt "What tools failed most often?"
```

### Loop Detection

```bash
# Detect infinite loops
uv run apps/backend/single-file-agents/agents/sfa_loop_detector_report_anthropic_v1.py \
  --db .auto-claude/events.db
```

### Failure Investigation

```bash
# Root cause analysis
uv run apps/backend/single-file-agents/agents/sfa_failure_investigator_anthropic_v1.py \
  --session-id abc123
```

## Data Sources

| Source | Location | Contains |
|--------|----------|----------|
| OTEL Traces | Phoenix (localhost:6006) | Span hierarchy, durations, tokens |
| Hook Logs | `.claude/hooks/hooks.log` | Tool usage, security events |
| Events DB | `.auto-claude/events.db` | Sessions, tools, messages (DuckDB) |
| Graphiti | `.auto-claude/specs/NNN/graphiti/` | Session insights, patterns |
| QA Reports | `.auto-claude/specs/NNN/qa_report.md` | Acceptance validation |

## Metrics Overview

**Cost Metrics:**
- Token usage by model and type
- Cost per phase and spec
- Cache efficiency

**Performance Metrics:**
- Phase duration (planning, coding, QA)
- Tool latency
- Subtask completion time

**Quality Metrics:**
- Test pass rate
- QA acceptance rate
- Fix iteration count

## Requirements

- Events database enabled (DuckDB)
- OTEL tracing enabled (optional, via Phoenix)
- Hook logs enabled
- UV installed for SFA execution

## Related

- **auto-claude-build** - Generates observability data (via autonomous-builder-agent)
- **archon** - Store insights for cross-spec learning (via archon-sync-agent)
- **single-file-agents** - SFAs power observability analysis

## Technical Details

**Agent Used:** `.claude/agents/session-analytics-agent.md`
**SFAs Used:**
  - `sfa_session_cost_tracker_anthropic_v1.py` - Cost analysis
  - `sfa_loop_detector_report_anthropic_v1.py` - Pattern detection
  - `sfa_failure_investigator_anthropic_v1.py` - Root cause analysis
  - `sfa_events_analyzer_anthropic_v1.py` - Natural language queries
**Model:** Haiku (fast analysis coordination)
**Triggers:** "analyze sessions", "session costs", "detect patterns", "investigate failure"

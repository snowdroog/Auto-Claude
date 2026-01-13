# snowdroog/Auto-Claude Enhancements

This document catalogs all enhancements we've added to our fork of Auto-Claude.

## Enhancement Philosophy

Our vision for Auto-Claude:
1. **Claude Code Native** - Deep integration with Claude Code features (hooks, skills, agents)
2. **UV-First** - Embrace UV as the primary Python tool for speed and simplicity
3. **Single-File Agents** - Self-contained tools with inline dependencies (PEP 723)
4. **IndyDevDan Patterns** - Apply proven patterns from IndyDevDan template
5. **Structured Prompts** - Machine-parseable prompts with YAML frontmatter + XML

## What We DON'T Change

To minimize conflicts and preserve upstream value:
- ❌ Core agent logic (planner, coder, qa loops remain as upstream designed)
- ❌ Electron frontend (except adding features that don't conflict)
- ❌ Security model (we keep their sandbox approach)
- ❌ Worktree strategy (we keep their isolated workspace pattern)
- ❌ Graphiti integration (we keep their memory system)

## Enhancement Categories (7 Total)

### 1. `.claude/` Framework

**Added**: Complete Claude Code integration framework
**Location**: `.claude/` directory (35 files)

**Structure:**
```
.claude/
├── settings.json           # Claude Code configuration
├── CLAUDE.md               # Project instructions for Claude Code
├── README.md               # Framework documentation
├── hooks/                  # 8 lifecycle hooks
│   ├── user_prompt_submit.py
│   ├── pre_tool_use.py
│   ├── post_tool_use.py    # ★ Enhanced with insight extraction
│   ├── stop.py
│   ├── session_start.py
│   ├── subagent_stop.py
│   ├── pre_compact.py
│   ├── notification.py
│   └── utils/              # Shared utilities
├── skills/                 # 5 specialized skills
│   ├── auto-claude-spec/
│   ├── auto-claude-build/
│   ├── single-file-agents/
│   ├── archon/
│   └── observability/
├── agents/                 # 5 sub-agent definitions (Phase 4 complete ✅)
│   ├── spec-creator-agent.md           # 1,134 lines - Spec creation workflow
│   ├── autonomous-builder-agent.md     # 1,178 lines - Build execution pipeline
│   ├── qa-loop-agent.md                # 856 lines - QA validation coordination
│   ├── archon-sync-agent.md            # 683 lines - Cross-session learning
│   ├── session-analytics-agent.md      # 789 lines - Cost/performance/failure analysis
│   ├── README.md                       # 656 lines - Sub-agent system docs
│   └── TEMPLATE.md                     # 279 lines - Agent creation template
├── patterns/               # Reusable patterns library
│   ├── phase-pipeline.md
│   ├── qa-loop.md
│   └── worktree-isolation.md
├── output-styles/          # Custom output formatting
└── status_lines/           # Status line configurations
```

**Why:** Claude Code is the future of AI-assisted coding. This framework makes Auto-Claude a first-class citizen in the Claude Code ecosystem.

**Phase 4 Integration:**
- All 5 sub-agents fully integrated with `.claude/` framework
- Skills provide natural language interface to agents
- Hooks enable lifecycle management and insight extraction
- Patterns library documents reusable workflows

**Commits:**
- `1e2d2cc` - chore(gitignore): commit .claude/ directory with local overrides
- `42179e4` - feat(claude-code): add Claude Code integration framework

---

### 2. Prompt Modernization (v2.0.0)

**Added**: Standardized prompt template with YAML frontmatter + XML structure
**Location**: `apps/backend/prompts/`

**Changes:**

**New Files:**
- `template.md` - Universal prompt template (1,030 lines)
- `TEMPLATE_GUIDE.md` - How to use the template (743 lines)
- `planner.v2.md` - Modernized planner prompt (1,731 lines)
- `coder.v2.md` - Modernized coder prompt (2,274 lines)

**Modernized Prompts:**
- `coder.md` - 1,948 lines with YAML frontmatter, XML sections, inlined recovery procedures
- `qa_reviewer.md` - Enhanced with structured acceptance criteria validation
- `qa_fixer.md` - Enhanced with issue resolution patterns
- `spec_gatherer.md` - Enhanced with dynamic phase pipeline guidance
- `spec_writer.md` - Enhanced with schema validation patterns

**Removed/Inlined:**
- `coder_recovery.md` → Inlined as `<recovery_procedures>` in coder.md
- `insight_extractor.md` → Inlined into `.claude/hooks/post_tool_use.py`
- `validation_fixer.md` → Logic moved to spec validation flow

**Template Structure:**
```yaml
---
# YAML Frontmatter (machine-readable)
version: "2.0.0"
agent_type: "coder"
model: "claude-sonnet-4-5"
thinking_budget: 16000
required_tools: [Read, Write, Edit, Bash]
quality_gates:
  self_critique: true
  verification: true
---

<metadata>
  <agent_info>...</agent_info>
</metadata>

<purpose>
  ## YOUR ROLE - AGENT NAME
  ...
</purpose>

<instructions>
  ## EXECUTION WORKFLOW
  ### PHASE 1: ...
  ### PHASE 2: ...
</instructions>

<tools>
  ## TOOL USAGE GUIDE
  ...
</tools>

<patterns>
  ## COMMON PATTERNS
  ...
</patterns>

<quality_gates>
  ## QUALITY GATES
  ...
</quality_gates>

<critical_reminders>
  ## CRITICAL RULES
  ...
</critical_reminders>

<completion>
  ## SESSION COMPLETION
  ...
</completion>
```

**Why:**
- Machine-parseable metadata enables smarter orchestration
- XML sections provide clear structure for agents to reference
- Consolidation reduces file count and improves maintainability
- Standardization makes it easier to create new agent prompts

**Commits:**
- `30952aa` - feat(prompts): add standardized prompt template system
- `78495dc` - feat(prompts): modernize phase 3 prompts and inline standalone helpers

---

### 3. Single-File Agents (SFA) Framework

**Added**: UV-based standalone tools with inline dependencies
**Location**: `apps/backend/single-file-agents/`

**Structure:**
```
single-file-agents/
├── README.md                                      # Framework documentation (updated)
└── agents/
    ├── sfa_spec_query_anthropic_v1.py            # Spec querying tool
    ├── sfa_events_analyzer_anthropic_v1.py       # Natural language DB queries ✅
    ├── sfa_session_cost_tracker_anthropic_v1.py  # Token usage & cost tracking ✅
    ├── sfa_loop_detector_report_anthropic_v1.py  # Infinite loop detection ✅
    └── sfa_failure_investigator_anthropic_v1.py  # Root cause analysis ✅
```

**Observability SFAs** (Phase 6 complete ✅):

1. **sfa_events_analyzer_anthropic_v1.py** (368 lines)
   - Query events.db using natural language
   - Translates queries to SQL using Claude
   - Analyzes results and provides insights
   - Usage: `uv run sfa_events_analyzer_anthropic_v1.py --db .auto-claude/events.db --prompt "query"`

2. **sfa_session_cost_tracker_anthropic_v1.py** (440 lines)
   - Track token usage and API costs across sessions
   - Cost breakdowns by agent, model, and spec
   - Pricing for all Claude models (Opus, Sonnet, Haiku)
   - Usage: `uv run sfa_session_cost_tracker_anthropic_v1.py --db .auto-claude/events.db --days 7`

3. **sfa_loop_detector_report_anthropic_v1.py** (442 lines)
   - Detect infinite loops and stuck states
   - Identify repeated tool call sequences
   - Flag excessive file read/edit cycles
   - Usage: `uv run sfa_loop_detector_report_anthropic_v1.py --db .auto-claude/events.db --severity high`

4. **sfa_failure_investigator_anthropic_v1.py** (509 lines)
   - Root cause analysis for failed sessions
   - Event timeline reconstruction
   - Recovery recommendations
   - Usage: `uv run sfa_failure_investigator_anthropic_v1.py --db .auto-claude/events.db --session-id abc123`

**Pattern:**
```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "anthropic>=0.40.0",
#     "rich>=13.9.4",
# ]
# ///
"""
Docstring with usage examples and purpose
"""

# Self-contained tool with all dependencies inline
# Runnable with: uv run script.py [args]
```

**Why:**
- **No virtual environment needed** - UV handles dependencies automatically
- **PEP 723 compliant** - Standard Python packaging metadata
- **Portable** - Copy file anywhere and it works
- **Fast** - UV is blazing fast compared to pip/poetry
- **Simple** - One file = one tool, no package management complexity

**Completed SFAs:** 5 total
- ✅ `sfa_spec_query_anthropic_v1.py` - Query spec.md files
- ✅ `sfa_events_analyzer_anthropic_v1.py` - Natural language DB queries
- ✅ `sfa_session_cost_tracker_anthropic_v1.py` - Cost tracking
- ✅ `sfa_loop_detector_report_anthropic_v1.py` - Loop detection
- ✅ `sfa_failure_investigator_anthropic_v1.py` - Failure analysis

**Planned SFA Additions:**
- `sfa_plan_analyzer_anthropic_v1.py` - Analyze implementation plans
- `sfa_graphiti_query_anthropic_v1.py` - Query Graphiti memory
- `sfa_qa_report_analyzer_anthropic_v1.py` - QA report analysis
- `sfa_worktree_manager_anthropic_v1.py` - Worktree management
- `sfa_archon_task_query_anthropic_v1.py` - Archon task queries
- `sfa_archon_rag_researcher_anthropic_v1.py` - RAG knowledge search
- `sfa_dependency_analyzer.py` - Analyze project dependencies
- `sfa_prompt_linter.py` - Validate prompt structure
- `sfa_spec_validator.py` - Validate spec.md against schema

**Commits:**
- `6f5084f` - feat(sfa): add single-file-agents framework
- Additional SFA commits integrated with Phase 4 and observability work

---

### 4. Sub-Agent System (Phase 4 Complete ✅)

**Added**: Natural language interface for Auto-Claude workflows via sub-agents
**Location**: `.claude/agents/` directory (7 files)

**Agents Created:**

1. **spec-creator-agent.md** (1,134 lines)
   - Creates feature specifications through guided discovery
   - Trigger: "create a spec for X"
   - Skill: `auto-claude-spec`

2. **autonomous-builder-agent.md** (1,178 lines)
   - Executes autonomous builds with multi-phase pipeline
   - Trigger: "build this autonomously"
   - Skill: `auto-claude-build`

3. **qa-loop-agent.md** (856 lines)
   - Coordinates quality assurance validation and fix loops
   - Trigger: "run QA on spec X"
   - Invoked by auto-claude-build or manual request

4. **archon-sync-agent.md** (683 lines)
   - Synchronizes specs, tasks, and insights with Archon
   - Trigger: "sync to archon"
   - Skill: `archon`

5. **session-analytics-agent.md** (789 lines)
   - Analyzes session data for cost tracking, performance metrics, failure investigation
   - Trigger: "analyze session costs"
   - Skill: `observability`
   - Uses all 4 observability SFAs

**Supporting Files:**
- **README.md** (656 lines) - Complete sub-agent system documentation
- **TEMPLATE.md** (279 lines) - Template for creating new agents

**Integration:**
- All agents integrated with corresponding `.claude/skills/`
- Trigger-based delegation via keyword detection
- Model selection (Sonnet for complex, Haiku for fast operations)
- Tool permissions scoped per agent

**Why:** Provides natural language interface to Auto-Claude CLI tools. Users describe what they want instead of running commands directly. Context-aware, error-handling, progress reporting.

**Completion:**
- 10/10 Phase 4 tasks complete
- All agents tested and documented
- Skills integration complete
- Test validation guide created

**Commits:**
- Part of Phase 4 modernization (multiple commits)

---

### 5. IndyDevDan Pattern Integration

**Added**: Patterns and practices from IndyDevDan template
**Location**: Distributed across `.claude/` framework

**Patterns Applied:**

**Hook Pattern:**
- Pre/Post tool use validation
- Session lifecycle management
- Context preservation during compaction
- Notification handling

**Skills Pattern:**
- User-invocable skills with `/skill-name` syntax
- Isolated skill execution environments
- Skill composition and chaining

**Agent Pattern:**
- Specialized sub-agents for complex tasks
- Agent orchestration and coordination
- Quality gates and validation

**Output Styles Pattern:**
- Customizable output formatting
- Context-aware presentation
- Machine and human readable formats

**Why:** IndyDevDan template represents battle-tested patterns for Claude Code integration. These patterns emerged from real-world usage and solve common problems elegantly.

---

### 6. Enhanced Insight Extraction

**Modified**: `apps/backend/analysis/insight_extractor.py`
**Modified**: `.claude/hooks/post_tool_use.py`

**Changes:**
- Inlined insight extraction prompt into PostToolUse hook
- Direct integration with Archon RAG for knowledge persistence
- Automatic pattern/gotcha detection during sessions

**Why:** Consolidates insight logic and enables real-time knowledge graph updates during Claude Code sessions.

---

### 7. Updated Orchestrator Integration

**Modified**: `apps/backend/spec/pipeline/orchestrator.py`
**Modified**: `apps/backend/spec/pipeline/agent_runner.py`
**Modified**: `apps/backend/spec/phases/planning_phases.py`

**Changes:**
- Reference modernized prompt files
- Support for YAML frontmatter parsing (future)
- Integration hooks for .claude/ framework

**Why:** Ensures orchestrator works with modernized prompts and can leverage new metadata.

---

## Divergences from Upstream

### Intentional Divergences

None currently. We layer on top, we don't replace.

### Potential Future Divergences

If upstream makes changes that conflict with our vision:

**Scenario 1: Upstream removes prompt flexibility**
- **Our response**: Maintain flexible prompt system in our fork
- **Reason**: Structured prompts are core to our enhancement strategy

**Scenario 2: Upstream changes Python dependency tool**
- **Our response**: Keep UV as default, add upstream's tool as alternative
- **Reason**: UV speed and simplicity align with SFA paradigm

**Scenario 3: Upstream integrates conflicting memory system**
- **Our response**: Support both, make ours opt-in
- **Reason**: Avoid breaking existing functionality

### Emergency Rollback Scenarios

Document here if we ever need to skip an upstream commit:

**[None yet]**

---

## Testing Our Enhancements

After syncing from upstream:

### 1. Test .claude/ Framework
```bash
# Open Claude Code and verify:
# - Skills appear in /skills list
# - Hooks execute without errors
# - Agents are available
```

### 2. Test Prompt Modernization
```bash
cd apps/backend
python spec_runner.py --task "test enhancement compatibility" --complexity simple
# Verify: Prompts load correctly, agents function normally
```

### 3. Test SFA Framework
```bash
cd apps/backend/single-file-agents
./agents/sfa_spec_query_anthropic_v1.py --help
# Should show usage without dependency errors
```

### 4. Test Integration
```bash
# Run full pipeline
python spec_runner.py --task "full integration test"
python run.py --spec [latest-spec]
# Verify: No errors, insights extracted, patterns recognized
```

---

## Contribution Strategy

### Contributing to Upstream

**Policy**: We do NOT contribute our enhancements back to AndyMik90/Auto-Claude.

**Reason**: Our vision diverges intentionally. We embrace:
- Claude Code deep integration (they may stay CLI-focused)
- UV-first paradigm (they may prefer pip/poetry)
- SFA pattern (they may prefer traditional packages)
- Structured prompts (they may prefer prose)

### Sharing Knowledge

We can share:
- ✅ Bug reports (if we discover upstream bugs)
- ✅ Security issues (responsible disclosure)
- ✅ Documentation improvements (general knowledge)
- ❌ Our enhancement code (keep as competitive advantage)

### Community

If others want our enhancements:
- Point them to `snowdroog/Auto-Claude`
- Explain our fork philosophy
- Help them understand the differences

---

## Metrics

**Current Enhancement Stats:**
```
Files Added:      59  (+5 observability SFAs + docs)
Lines Added:      +14,932  (includes Phase 4 agents + SFAs)
Lines Removed:    -973
Net Addition:     +13,959 lines

Commits:          7
Categories:       7  (added Sub-Agent System)
Frameworks:       3 (.claude/, SFA, template)
Prompts Modernized: 5
Agents Created:   5  (spec-creator, builder, qa-loop, archon-sync, analytics)
SFAs Created:     5  (spec-query, events-analyzer, cost-tracker, loop-detector, failure-investigator)
```

**Maintenance Burden:**
- **Low**: Most enhancements are additive (new files in new directories)
- **Medium**: Prompt modernization may need updates if upstream changes prompts
- **Low**: SFA framework is isolated from upstream changes

---

## Future Enhancements

See Archon project for roadmap:
- **Project**: Auto-Claude Fork Maintenance & Enhancement
- **Project ID**: 24e20808-303f-4c64-95e8-248d8095518c

**Completed:**
- ✅ Sub-Agent System (Phase 4) - 5 agents created
- ✅ Observability SFAs (Phase 6) - 4 SFAs created
- ✅ Branch strategy documentation
- ✅ Skills integration for all agents

**In Progress:**
- Branch strategy: develop (upstream) + snowdroog-clean (enhanced)

**Planned:**
1. Expand SFA library (9+ additional agents planned)
   - Plan analyzer, Graphiti query, QA report analyzer
   - Worktree manager, Archon task query, RAG researcher
   - Dependency analyzer, prompt linter, spec validator
2. Apply IndyDevDan patterns (hooks, skills refinement)
3. Create ENHANCEMENTS.md philosophy documentation
4. Automated upstream monitoring workflow
5. Advanced patterns library (more reusable patterns)
6. Claude Code statusline integration
7. Output style customization
8. UV-based plugin system
9. Unified .env configuration for OTEL
10. Crawl OTEL docs into Archon RAG

---

## Questions?

- **Why fork instead of contribute?** Different visions. Both valid, both useful.
- **Will you stay synced?** Yes, we pull all upstream improvements.
- **Can I use your fork?** Yes! `git clone https://github.com/snowdroog/Auto-Claude`
- **Can I contribute to your fork?** Open an issue first to discuss alignment.

---

## Enhancement Commits (snowdroog-clean branch)

All 7 enhancement commits on top of upstream base `6dc538c`:

```
4b9cb83 - docs: add fork status summary and troubleshooting
3c7b5ba - docs: add fork maintenance and enhancement documentation
78495dc - feat(prompts): modernize phase 3 prompts and inline standalone helpers
6f5084f - feat(sfa): add single-file-agents framework
30952aa - feat(prompts): add standardized prompt template system
42179e4 - feat(claude-code): add Claude Code integration framework
1e2d2cc - chore(gitignore): commit .claude/ directory with local overrides
```

**Base Upstream Commit:** `6dc538c` - fix: properly quote Windows .cmd/.bat paths in spawn() calls

## Recent Completions (Jan 2026)

**Phase 4: Sub-Agent System** ✅ Complete (10/10 tasks)
- Created 5 sub-agents (spec-creator, autonomous-builder, qa-loop, archon-sync, session-analytics)
- Integrated with `.claude/skills/` system
- Comprehensive documentation (README.md, TEMPLATE.md, test validation guide)
- Natural language interface to Auto-Claude workflows

**Phase 6: Observability SFAs** ✅ Complete (4/4 SFAs)
- `sfa_events_analyzer_anthropic_v1.py` - Natural language DB queries
- `sfa_session_cost_tracker_anthropic_v1.py` - Cost tracking and analysis
- `sfa_loop_detector_report_anthropic_v1.py` - Loop pattern detection
- `sfa_failure_investigator_anthropic_v1.py` - Root cause analysis

**Documentation** ✅ Complete
- Updated single-file-agents README with all 5 SFAs
- Updated session-analytics-agent with SFA integration
- Updated FORK_MAINTENANCE.md with branch strategy
- Updated FORK_STATUS.md with current state

---

**Last Updated**: 2026-01-13
**Active Branch**: `snowdroog-clean` (myfork/snowdroog-clean)
**Fork Base**: AndyMik90/Auto-Claude@6dc538c (v2.7.3 + bug fixes)
**Enhancement Commits**: 7 commits
**Enhancement Version**: v1.1.0 (Phase 4 + Observability complete)
**GitHub**: https://github.com/snowdroog/Auto-Claude/tree/snowdroog-clean

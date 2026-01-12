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

## Enhancement Categories

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
├── agents/                 # 5 sub-agent definitions
│   ├── spec-creator-agent.md
│   ├── autonomous-builder-agent.md
│   ├── qa-loop-agent.md
│   ├── archon-sync-agent.md
│   └── session-analytics-agent.md
├── patterns/               # Reusable patterns library
│   ├── phase-pipeline.md
│   ├── qa-loop.md
│   └── worktree-isolation.md
├── output-styles/          # Custom output formatting
└── status_lines/           # Status line configurations
```

**Why:** Claude Code is the future of AI-assisted coding. This framework makes Auto-Claude a first-class citizen in the Claude Code ecosystem.

**Commits:**
- `e24a07b` - chore(gitignore): commit .claude/ directory with local overrides
- `98c3f25` - feat(claude-code): add Claude Code integration framework

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
- `71f3451` - feat(prompts): add standardized prompt template system
- `38903e4` - feat(prompts): modernize phase 3 prompts and inline standalone helpers

---

### 3. Single-File Agents (SFA) Framework

**Added**: UV-based standalone tools with inline dependencies
**Location**: `apps/backend/single-file-agents/`

**Structure:**
```
single-file-agents/
├── README.md                          # Framework documentation
└── agents/
    └── sfa_spec_query_anthropic_v1.py # First SFA: Spec querying tool
```

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

**Planned SFA Additions:**
- `sfa_dependency_analyzer.py` - Analyze project dependencies
- `sfa_prompt_linter.py` - Validate prompt structure
- `sfa_spec_validator.py` - Validate spec.md against schema
- `sfa_memory_query.py` - Query Graphiti/Archon memory
- `sfa_cost_tracker.py` - Track OpenTelemetry costs

**Commits:**
- `228977e` - feat(sfa): add single-file-agents framework

---

### 4. IndyDevDan Pattern Integration

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

### 5. Enhanced Insight Extraction

**Modified**: `apps/backend/analysis/insight_extractor.py`
**Modified**: `.claude/hooks/post_tool_use.py`

**Changes:**
- Inlined insight extraction prompt into PostToolUse hook
- Direct integration with Archon RAG for knowledge persistence
- Automatic pattern/gotcha detection during sessions

**Why:** Consolidates insight logic and enables real-time knowledge graph updates during Claude Code sessions.

---

### 6. Updated Orchestrator Integration

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
Files Added:      54
Lines Added:      +12,173
Lines Removed:    -973
Net Addition:     +11,200 lines

Commits:          5
Categories:       6
Frameworks:       3 (.claude/, SFA, template)
Prompts Modernized: 5
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

**Planned:**
1. Expand SFA library (5+ new agents)
2. Enhanced skill system (more user-invocable skills)
3. Advanced patterns library (more reusable patterns)
4. Claude Code statusline integration
5. Output style customization
6. UV-based plugin system

---

## Questions?

- **Why fork instead of contribute?** Different visions. Both valid, both useful.
- **Will you stay synced?** Yes, we pull all upstream improvements.
- **Can I use your fork?** Yes! `git clone https://github.com/snowdroog/Auto-Claude`
- **Can I contribute to your fork?** Open an issue first to discuss alignment.

---

**Last Updated**: 2026-01-12
**Fork Base**: AndyMik90/Auto-Claude@5e84912
**Enhancement Version**: v1.0.0 (first documented release)

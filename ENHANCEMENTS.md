# snowdroog/Auto-Claude Enhancements

This document catalogs all enhancements we've added to our fork of Auto-Claude.

## Enhancement Philosophy

Our vision for Auto-Claude:
1. **Claude Code Native** - Deep integration with Claude Code features (hooks, skills, agents)
2. **UV-First** - Embrace UV as the primary Python tool for speed and simplicity
3. **Single-File Agents** - Self-contained tools with inline dependencies (PEP 723)
4. **IndyDevDan Patterns** - Apply proven patterns from IndyDevDan template
5. **Structured Prompts** - Machine-parseable prompts with YAML frontmatter + XML
6. **Cross-Session Memory** - Semantic retrieval of insights across all sessions

## What We DON'T Change

To minimize conflicts and preserve upstream value:
- ❌ Core agent logic (planner, coder, qa loops remain as upstream designed)
- ❌ Electron frontend (except adding features that don't conflict)
- ❌ Security model (we keep their sandbox approach)
- ❌ Worktree strategy (we keep their isolated workspace pattern)
- ❌ Graphiti integration (we keep their memory system)

## Enhancement Categories (9 Total)

### 1. `.claude/` Framework

**Added**: Complete Claude Code integration framework
**Location**: `.claude/` directory (35+ files)

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
├── skills/                 # 6 specialized skills
│   ├── auto-claude-spec/
│   ├── auto-claude-build/
│   ├── single-file-agents/
│   ├── archon/
│   ├── observability/
│   └── git-helper/
├── agents/                 # 5 sub-agent definitions
│   ├── spec-creator-agent.md
│   ├── autonomous-builder-agent.md
│   ├── qa-loop-agent.md
│   ├── archon-sync-agent.md
│   ├── session-analytics-agent.md
│   ├── README.md
│   └── TEMPLATE.md
├── patterns/               # 5 reusable patterns
│   ├── phase-pipeline.md
│   ├── qa-loop.md
│   ├── worktree-isolation.md
│   ├── error-handling.md
│   └── git-workflow.md
├── output-styles/          # Custom output formatting
└── status_lines/           # Status line configurations
```

**Why:** Claude Code is the future of AI-assisted coding. This framework makes Auto-Claude a first-class citizen in the Claude Code ecosystem.

---

### 2. Prompt Modernization (v2.0.0)

**Added**: Standardized prompt template with YAML frontmatter + XML structure
**Location**: `apps/backend/prompts/`

**New Files:**
- `template.md` - Universal prompt template
- `TEMPLATE_GUIDE.md` - How to use the template
- `planner.v2.md` - Modernized planner prompt
- `coder.v2.md` - Modernized coder prompt
- `README.md` - Prompt system documentation

**Modernized Prompts:**
- `coder.md` - With YAML frontmatter, XML sections, inlined recovery procedures
- `qa_reviewer.md` - Enhanced with structured acceptance criteria validation
- `qa_fixer.md` - Enhanced with issue resolution patterns
- `spec_gatherer.md` - Enhanced with dynamic phase pipeline guidance
- `spec_writer.md` - Enhanced with schema validation patterns

**Removed/Inlined:**
- `coder_recovery.md` → Inlined as `<recovery_procedures>` in coder.md
- `insight_extractor.md` → Inlined into `.claude/hooks/post_tool_use.py`
- `validation_fixer.md` → Logic moved to spec validation flow

---

### 3. Single-File Agents (SFA) Framework ✅ Complete

**Added**: UV-based standalone tools with inline dependencies
**Location**: `apps/backend/single-file-agents/`
**Status**: **11 SFAs created** (all planned agents complete)

**All SFAs:**
```
single-file-agents/agents/
├── sfa_spec_query_anthropic_v1.py            # Query spec.md files
├── sfa_events_analyzer_anthropic_v1.py       # Natural language DB queries
├── sfa_session_cost_tracker_anthropic_v1.py  # Token usage & cost tracking
├── sfa_loop_detector_report_anthropic_v1.py  # Infinite loop detection
├── sfa_failure_investigator_anthropic_v1.py  # Root cause analysis
├── sfa_plan_analyzer_anthropic_v1.py         # Analyze implementation plans
├── sfa_graphiti_query_anthropic_v1.py        # Query Graphiti memory
├── sfa_qa_report_analyzer_anthropic_v1.py    # QA report analysis
├── sfa_dependency_analyzer_anthropic_v1.py   # Project dependencies
├── sfa_prompt_linter_anthropic_v1.py         # Validate prompt structure
└── sfa_spec_validator_anthropic_v1.py        # Validate spec.md schema
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
"""Self-contained tool with all dependencies inline"""
# Runnable with: uv run script.py [args]
```

**Why:**
- **No virtual environment needed** - UV handles dependencies automatically
- **PEP 723 compliant** - Standard Python packaging metadata
- **Portable** - Copy file anywhere and it works
- **Fast** - UV is blazing fast compared to pip/poetry

**Note:** Archon-related SFAs (task query, RAG researcher) not needed - we have direct Archon MCP integration.

---

### 4. Sub-Agent System ✅ Complete

**Added**: Natural language interface for Auto-Claude workflows via sub-agents
**Location**: `.claude/agents/` directory (7 files)

**Agents:**
1. **spec-creator-agent.md** - Creates feature specifications
2. **autonomous-builder-agent.md** - Executes autonomous builds
3. **qa-loop-agent.md** - Coordinates QA validation
4. **archon-sync-agent.md** - Syncs with Archon MCP
5. **session-analytics-agent.md** - Cost/performance analysis

**Why:** Natural language interface to Auto-Claude CLI tools. Users describe what they want instead of running commands directly.

---

### 5. IndyDevDan Pattern Integration ✅ Complete

**Added**: Patterns and practices from IndyDevDan template
**Location**: Distributed across `.claude/` framework

**Patterns Applied:**
- **Hook Pattern** - Pre/Post tool use validation, lifecycle management
- **Skills Pattern** - User-invocable skills with `/skill-name` syntax
- **Agent Pattern** - Specialized sub-agents for complex tasks
- **Output Styles Pattern** - Customizable output formatting
- **Patterns Library** - 5 reusable workflow patterns

---

### 6. TLDR Token Efficiency System ✅ Complete (Phase 6)

**Added**: AST-based code summarization for 80%+ token savings
**Location**: `apps/backend/tldr/`

**Structure:**
```
tldr/
├── __init__.py
├── analyzer.py           # Core TLDR analysis engine
├── cache.py              # File hash-based caching
├── models.py             # TLDRSummary dataclass
├── extractors/           # Language-specific extractors
│   ├── base.py
│   ├── python_extractor.py
│   └── typescript_extractor.py
├── hooks/                # Claude Code integration
│   ├── cache_updater.py
│   ├── config.py
│   ├── read_enforcer.py
│   └── setup.py
└── semantic/             # Semantic search
    ├── embedder.py       # TF-IDF embeddings
    ├── index.py          # Semantic index
    └── search.py         # Search interface
```

**CLI Commands:**
```bash
--tldr FILE              # Get TLDR summary of a file
--tldr-index             # Build/rebuild TLDR index
--tldr-stats             # Show token savings statistics
--tldr-semantic-index    # Build semantic search index
--tldr-semantic-search   # Semantic search across codebase
--tldr-semantic-stats    # Show semantic index stats
```

**Why:** Reduces token usage by 80%+ when reading code files, enabling longer context windows and cheaper API calls.

---

### 7. Cross-Session Memory System ✅ Complete (Phase 7)

**Added**: Semantic memory extraction and retrieval across sessions
**Location**: `apps/backend/memory/`

**Structure:**
```
memory/
├── extraction/           # Memory extraction daemon
│   ├── daemon.py         # Background extraction
│   ├── extractor.py      # Insight extraction
│   ├── patterns.py       # Pattern matching
│   └── processor.py      # Transcript processing
└── retrieval/            # Semantic search
    ├── index.py          # Memory index with embeddings
    └── search.py         # Search interface
```

**CLI Commands:**
```bash
--memory-extract         # Extract insights from transcripts
--memory-status          # Show daemon status
--memory-insights        # View extracted insights
--memory-stats           # Show memory statistics
--memory-clear           # Clear insights (with --confirm)
--memory-index-build     # Build/rebuild search index
--memory-search QUERY    # Search session memories
--memory-context TASK    # Get relevant context for task
--memory-patterns        # Discover recurring patterns
--memory-index-stats     # Show index statistics
```

**Insight Types Extracted:**
- `gotcha` - Pitfalls and gotchas to avoid
- `pattern` - Successful patterns to follow
- `discovery` - New learnings
- `failure` - What went wrong
- `success` - What worked well
- `recommendation` - Suggested approaches
- `decision` - Key decisions made
- `workaround` - Workarounds for issues
- `reasoning` - Important reasoning chains

**Why:** Enables cross-session learning. Search past sessions for relevant insights, patterns, and gotchas.

---

### 8. Archon MCP Integration ✅ Complete

**Added**: Direct integration with Archon for knowledge management
**Location**: `apps/backend/core/client.py`, `.claude/` framework

**Features:**
- RAG knowledge base search
- Project and task management
- Cross-session insight sync
- Best practices guidance in agent prompts

**Documentation:**
- `ARCHON_INTEGRATION_PLAN.md`
- `guides/ARCHON_BEST_PRACTICES.md`

---

### 9. Multi-Project Registry ✅ Complete (Phase 5)

**Added**: Portfolio management across multiple Auto-Claude projects
**Location**: `apps/backend/registry/`

**CLI Commands:**
```bash
--projects               # Portfolio dashboard
--project-status ID      # Detailed project status
--register-project       # Register current directory
--discover-project       # Auto-discover project info
--unregister-project ID  # Remove from registry
--link-archon ID         # Link to Archon project
```

---

## Metrics

**Current Enhancement Stats:**
```
Enhancement Categories:   9
SFAs Created:            11 (all planned complete)
Sub-Agents Created:       5
Skills Created:           6
Patterns Documented:      5
CLI Commands Added:      20+

Frameworks:
- .claude/ framework (hooks, skills, agents, patterns)
- SFA framework (UV + PEP 723)
- TLDR system (AST extraction + semantic search)
- Memory system (extraction + retrieval)
- Registry system (multi-project)
```

**Maintenance Burden:**
- **Low**: Most enhancements are additive (new files in new directories)
- **Medium**: Prompt modernization may need updates if upstream changes prompts
- **Low**: SFA/TLDR/Memory frameworks are isolated from upstream changes

---

## Future Enhancements

**Remaining TODO:**
1. ☐ Automated upstream monitoring workflow (GitHub Actions)
2. ☐ Claude Code statusline integration
3. ☐ Output style customization
4. ☐ UV-based plugin system

**Not Needed (superseded):**
- ~~sfa_worktree_manager~~ - CLI commands sufficient
- ~~sfa_archon_task_query~~ - Have Archon MCP tools
- ~~sfa_archon_rag_researcher~~ - Have Archon MCP tools

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

### 2. Test SFA Framework
```bash
cd apps/backend/single-file-agents/agents
uv run sfa_spec_query_anthropic_v1.py --help
# Should show usage without dependency errors
```

### 3. Test TLDR System
```bash
cd apps/backend
python run.py --tldr-stats
python run.py --tldr README.md
```

### 4. Test Memory System
```bash
cd apps/backend
python run.py --memory-stats
python run.py --memory-index-stats
python run.py --memory-search "authentication"
```

---

## Enhancement Commits (snowdroog-clean branch)

All enhancement commits on top of upstream v2.7.4:

```
824d843 - feat(memory): add Phase 6-7 memory system from enhancement plan
269f8f4 - docs(readme): add Archon MCP integration documentation
4b3aae9 - feat(archon): enhance agent prompts with RAG query guidance
fa68566 - docs(archon): add comprehensive integration plan
9c62655 - feat(archon): integrate Archon MCP for knowledge-driven development
26b796e - feat(claude): apply IndyDevDan patterns - hooks, skills, patterns
384e5e8 - feat(sfa): add 6 new UV-first analysis and validation agents
9f65a2b - docs: complete Phase 4 sub-agent system and observability SFAs
1999b72 - docs: add fork status summary and troubleshooting
c30e3fe - docs: add fork maintenance and enhancement documentation
f4a99a2 - feat(prompts): modernize phase 3 prompts and inline standalone helpers
9aa2289 - feat(sfa): add single-file-agents framework
5645286 - feat(prompts): add standardized prompt template system
5dcb5fa - feat(claude-code): add Claude Code integration framework
5a25e1f - chore(gitignore): commit .claude/ directory with local overrides
```

**Base Upstream**: AndyMik90/Auto-Claude v2.7.4
**Enhancement Commits**: 15

---

## Questions?

- **Why fork instead of contribute?** Different visions. Both valid, both useful.
- **Will you stay synced?** Yes, we pull all upstream improvements.
- **Can I use your fork?** Yes! `git clone https://github.com/snowdroog/Auto-Claude`
- **Can I contribute to your fork?** Open an issue first to discuss alignment.

---

**Last Updated**: 2026-01-14
**Active Branch**: `snowdroog-clean` (synced with myfork/develop)
**Fork Base**: AndyMik90/Auto-Claude v2.7.4
**Enhancement Version**: v2.0.0 (All phases complete through Phase 7)
**GitHub**: https://github.com/snowdroog/Auto-Claude

# Archon MCP Integration Plan for Auto-Claude

## Executive Summary

This document outlines how to integrate Archon's knowledge base (RAG) and task management with Auto-Claude's autonomous build pipeline to enable knowledge-driven development.

**Goal**: Auto-Claude agents should query Archon's RAG for similar patterns, code examples, and past learnings before implementing features.

---

## Current State Analysis

### ✅ What's Already Working

1. **Custom MCP Support**: `CUSTOM_MCP_SERVERS` is implemented in `core/client.py`
2. **Agent-Aware Configuration**: `AGENT_CONFIGS` in `agents/tools_pkg/models.py` supports per-agent MCP servers
3. **Prompt Integration Points**: Planner already has "Phase 0: Deep Codebase Investigation" that searches for similar patterns
4. **Infrastructure**: MCP server routing and tool permissions are fully functional

### ❌ What's Missing

1. **Archon in Default Configs**: Not included in any `AGENT_CONFIGS.mcp_servers` lists
2. **Prompt Instructions**: Agents don't know to query Archon RAG
3. **Documentation**: No `.env.example` entry for Archon MCP configuration
4. **Workflow Integration**: No guidance on when/how to use Archon knowledge

---

## Integration Architecture

### Phase 1: Configuration & Documentation ⭐ START HERE

**Objective**: Enable users to connect Archon MCP to Auto-Claude

**Changes:**

1. **Add to `.env.example`**:
```bash
# =============================================================================
# ARCHON MCP INTEGRATION (OPTIONAL)
# =============================================================================
# Enable Archon knowledge base integration for autonomous agents.
# Archon provides RAG search across past builds, code examples, and learnings.
#
# Prerequisites:
#   1. Archon MCP server running: http://localhost:8051/mcp
#   2. Archon RAG populated with documentation and code examples
#
# When enabled, agents can query Archon for:
#   - Similar patterns from past implementations
#   - Code examples for specific technologies
#   - Known gotchas and best practices
#   - Acceptance criteria patterns
#
# Enable Archon integration (default: false)
# ARCHON_MCP_ENABLED=true
#
# Archon MCP server URL (default: http://localhost:8051/mcp)
# ARCHON_MCP_URL=http://localhost:8051/mcp
#
# Configure which agents can use Archon (comma-separated)
# Options: planner, coder, spec_gatherer, spec_researcher, qa_reviewer
# ARCHON_AGENTS=planner,coder,spec_researcher
```

2. **Update `core/client.py`** to conditionally add Archon:
```python
def _load_project_mcp_config(project_dir: Path) -> dict[str, Any]:
    """Load MCP configuration from project .env file."""
    # ... existing code ...

    # Auto-configure Archon if enabled
    if config.get("ARCHON_MCP_ENABLED", "").lower() == "true":
        archon_url = config.get("ARCHON_MCP_URL", "http://localhost:8051/mcp")
        if "CUSTOM_MCP_SERVERS" not in config:
            config["CUSTOM_MCP_SERVERS"] = []
        config["CUSTOM_MCP_SERVERS"].append({
            "id": "archon",
            "name": "Archon Knowledge Base",
            "type": "http",
            "url": archon_url
        })
```

### Phase 2: Agent Configuration

**Objective**: Add Archon to agent MCP server lists

**Changes to `agents/tools_pkg/models.py`**:

```python
AGENT_CONFIGS = {
    # Spec creation - add Archon to researcher and gatherer
    "spec_gatherer": {
        "tools": BASE_READ_TOOLS + WEB_TOOLS,
        "mcp_servers": ["archon"],  # Query for similar specs
        "auto_claude_tools": [],
        "thinking_default": "medium",
    },
    "spec_researcher": {
        "tools": BASE_READ_TOOLS + WEB_TOOLS,
        "mcp_servers": ["context7", "archon"],  # Docs + RAG
        "auto_claude_tools": [],
        "thinking_default": "medium",
    },

    # Build phases - add Archon to planner and coder
    "planner": {
        "tools": BASE_READ_TOOLS + BASE_WRITE_TOOLS + WEB_TOOLS,
        "mcp_servers": ["context7", "graphiti", "auto-claude", "archon"],
        "mcp_servers_optional": ["linear"],
        # ... rest unchanged
    },
    "coder": {
        "tools": BASE_READ_TOOLS + BASE_WRITE_TOOLS + WEB_TOOLS,
        "mcp_servers": ["context7", "graphiti", "auto-claude", "archon"],
        "mcp_servers_optional": ["linear"],
        # ... rest unchanged
    },

    # QA phases - add Archon to reviewer
    "qa_reviewer": {
        "tools": BASE_READ_TOOLS + BASE_WRITE_TOOLS + WEB_TOOLS,
        "mcp_servers": ["context7", "graphiti", "auto-claude", "browser", "archon"],
        "mcp_servers_optional": ["linear"],
        # ... rest unchanged
    },
}
```

**Conditional Loading**:
```python
def _filter_unavailable_servers(servers: list[str], mcp_config: dict) -> list[str]:
    """Filter out servers that are not available."""
    # ... existing graphiti check ...

    # Remove archon if not enabled
    if not mcp_config.get("ARCHON_MCP_ENABLED", "").lower() == "true":
        servers = [s for s in servers if s != "archon"]

    return servers
```

### Phase 3: Prompt Enhancement

**Objective**: Teach agents to use Archon RAG effectively

**Key Integration Points:**

1. **`prompts/planner.md`** - Phase 0 Investigation:
```markdown
### 0.2: Query Archon Knowledge Base (If Available)

Before grepping the codebase, query Archon for similar patterns:

```bash
# Use Archon MCP tools to search for similar implementations
# These tools are only available if Archon MCP is enabled

# Search for similar features
mcp__archon__rag_search_knowledge_base(
    query="authentication patterns",
    match_count=5
)

# Search for code examples
mcp__archon__rag_search_code_examples(
    query="React hooks useState",
    match_count=3
)
```

**When to use Archon:**
- ✅ Looking for similar features implemented before
- ✅ Need code examples for specific technologies
- ✅ Want to learn from past gotchas
- ❌ Archon is unavailable (use grep/search instead)
- ❌ Looking for project-specific patterns (use grep)

**Fallback**: If Archon tools aren't available, proceed with grep-based investigation.
```

2. **`prompts/spec_gatherer.md`** - Requirements Discovery:
```markdown
## OPTIONAL: Query Archon for Similar Specs

If Archon MCP is available, query for similar past specs:

```bash
mcp__archon__rag_search_knowledge_base(
    query="user authentication feature",
    match_count=3
)
```

This helps you:
- Ask better questions based on past experiences
- Identify common requirements patterns
- Discover edge cases from previous implementations
```

3. **`prompts/coder.md`** - Implementation Phase:
```markdown
## Knowledge Integration

Before implementing a subtask, consider querying Archon:

**Query for code examples:**
```bash
mcp__archon__rag_search_code_examples(
    query="FastAPI middleware",
    match_count=3
)
```

**Query for known gotchas:**
```bash
mcp__archon__rag_search_knowledge_base(
    query="database migration pitfalls PostgreSQL",
    match_count=5
)
```

This is OPTIONAL but recommended for:
- Unfamiliar technologies
- Complex integrations
- Security-sensitive code
```

### Phase 4: Workflow Integration

**Objective**: Enable bidirectional sync between Auto-Claude and Archon

**Future enhancements (not in initial implementation):**

1. **Spec → Archon**: Store completed specs in Archon as documents
2. **Tasks → Archon**: Sync implementation plan subtasks to Archon tasks
3. **Learnings → Archon**: Auto-extract gotchas to Archon RAG
4. **Acceptance Criteria → Archon**: Build corpus of validation patterns

---

## Implementation Checklist

### Minimal Integration (Can do NOW)

- [ ] Add `ARCHON_MCP_ENABLED` to `.env.example` with full documentation
- [ ] Add conditional Archon server loading in `core/client.py`
- [ ] Add "archon" to relevant `AGENT_CONFIGS.mcp_servers` lists
- [ ] Add Archon filtering logic to `_filter_unavailable_servers()`
- [ ] Test with Archon enabled and disabled
- [ ] Document in main README.md

### Enhanced Integration (Phase 2)

- [ ] Update `prompts/planner.md` with Archon query examples
- [ ] Update `prompts/spec_gatherer.md` with RAG search guidance
- [ ] Update `prompts/coder.md` with code example lookups
- [ ] Add Archon query examples to agent training data
- [ ] Create helper functions for common Archon queries

### Advanced Integration (Phase 3)

- [ ] Bidirectional spec syncing (Auto-Claude → Archon)
- [ ] Task status synchronization
- [ ] Auto-extract learnings to Archon RAG
- [ ] Cross-session pattern learning

---

## Benefits

1. **Faster Planning**: Learn from past implementations instead of starting from scratch
2. **Better Code Quality**: Reference proven patterns and code examples
3. **Avoid Pitfalls**: Query for known gotchas before implementation
4. **Knowledge Accumulation**: Each build enriches the knowledge base
5. **Cross-Session Learning**: Benefit from other developers' experiences

---

## Testing Strategy

1. **Without Archon**: Ensure agents work normally when Archon is disabled
2. **With Archon**: Verify agents query RAG during investigation phases
3. **Graceful Degradation**: Handle Archon unavailability without failures
4. **Query Quality**: Verify agents use appropriate search terms
5. **Result Usage**: Confirm agents incorporate RAG results into plans

---

## Rollout Plan

**Week 1**: Minimal Integration
- Add configuration support
- Update agent configs
- Test with local Archon instance
- Document setup process

**Week 2**: Prompt Enhancement
- Update key prompts (planner, coder)
- Add usage examples
- Test knowledge-driven builds

**Week 3**: Advanced Features
- Spec syncing
- Task correlation
- Learning extraction

---

## Success Metrics

1. **Query Rate**: Agents query Archon RAG in >80% of builds
2. **Pattern Reuse**: Code examples from Archon used in >50% of implementations
3. **Quality**: Builds with Archon complete with fewer iterations
4. **Knowledge Growth**: RAG database grows with each build

---

## Next Steps

**Immediate (this session):**
1. Add `ARCHON_MCP_ENABLED` to `.env.example`
2. Update `AGENT_CONFIGS` to include "archon"
3. Add conditional loading in `core/client.py`
4. Test the integration

**Follow-up (next session):**
1. Enhance prompts with Archon query guidance
2. Create usage documentation
3. Test with real builds

Would you like me to proceed with the immediate implementation?

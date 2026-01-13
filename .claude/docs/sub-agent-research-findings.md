# Sub-Agent Research Findings & Recommendations

This document summarizes research findings from analyzing IndyDev Template sub-agent patterns and provides recommendations for Auto-Claude's Phase 4 implementation.

## Research Summary

**Date:** 2026-01-12
**Objective:** Understand IndyDev Template sub-agent patterns for Auto-Claude Phase 4 (Sub-Agent System)
**Primary Sources:**
- Archon document: "IndyDev Template Pattern Analysis & Adoption Guide" (ID: ce20d28c-f93a-4e92-b5af-5c6da0a30acc)
- Existing Auto-Claude agents: `.claude/agents/*.md`
- Auto-Claude skills: `.claude/skills/*/SKILL.md`

## Key Findings

### 1. Sub-Agent Definition Pattern

**Structure:** Markdown files with YAML frontmatter

**Location:**
- Project-level: `.claude/agents/*.md` (Auto-Claude-specific)
- User-level: `~/.claude/agents/*.md` (Personal tools, shared across projects)

**Frontmatter Schema:**
```yaml
name: agent-name              # Required - kebab-case identifier
version: 1.0.0                # Required - semver
description: "..."            # Required - acts as trigger
tools: [Read, Grep, ...]      # Required - tool permissions
model: sonnet                 # Optional - sonnet/opus/haiku/inherit
triggers:                     # Optional - explicit triggers
  - keyword: example
  - file_pattern: "**/*.py"
```

**Key Insight:** Frontmatter separates configuration (tools, model, triggers) from implementation (system prompt in markdown body). This enables declarative agent definitions without modifying code.

### 2. CLI Wrapping Pattern

**Core Principle:** Sub-agents provide natural language interfaces to existing command-line tools.

**Pattern Flow:**
```
User (Natural Language)
  ↓
Claude (Context-aware agent selection)
  ↓
Sub-Agent (Markdown definition)
  ↓
CLI Tool (Existing command-line program)
  ↓
Agent Response (Interprets output, guides next steps)
```

**Auto-Claude Examples:**
- `spec-creator-agent` wraps `spec_runner.py`
- `autonomous-builder-agent` wraps `run.py`
- `qa-loop-agent` wraps QA system (`qa_reviewer.py`, `qa_fixer.py`)
- `session-analytics-agent` wraps SFA tools
- `archon-sync-agent` wraps Archon MCP tools

**Benefits:**
1. Reusability - Leverage existing, tested tools
2. Accessibility - Natural language lowers barrier to entry
3. Maintainability - Update CLI tool, agent automatically benefits
4. Composability - Agents can chain CLI tools in workflows

### 3. Tool Permissions

**Declarative Security:** Tools field in frontmatter defines what agent can use.

**Permission Levels:**

| Level | Tools | Use Case |
|-------|-------|----------|
| Read-only | `[Read, Grep, Glob]` | Analysis, inspection |
| Read-write | `[Read, Edit, Write, Grep, Glob]` | File modifications |
| Full access | `[Read, Edit, Write, Bash, Grep, Glob]` | Implementation |
| Scoped Bash | `[Bash(git:*), Read]` | Git operations only |
| MCP integration | `[Read, mcp__archon__*]` | External service access |

**Auto-Claude Permissions:**

| Agent | Tools | Rationale |
|-------|-------|-----------|
| spec-creator | Read, Glob, Grep, Write, Edit, WebFetch, WebSearch, Bash | Full research & spec creation |
| autonomous-builder | Read, Glob, Grep, Write, Edit, Bash | Full implementation access |
| qa-loop | Read, Glob, Grep, Write, Edit, Bash | Validation & reporting |
| archon-sync | Read, Glob, Grep, Write, mcp__archon__* | Archon integration only |
| session-analytics | Read, Glob, Grep, Bash, mcp__archon__* | Analysis & reporting |

**Key Insight:** Tool restrictions enable focused, secure agents. Each agent only gets the minimum tools needed for its task.

### 4. Trigger Patterns

**Two Types:**

**1. Implicit Triggers (Description):**
- Description field acts as primary trigger
- Claude uses it for context-aware agent selection
- Should include: action verbs, domain terms, use cases, keywords

**2. Explicit Triggers (Optional):**
```yaml
triggers:
  - keyword: authentication
  - keyword: auth
  - file_pattern: "**/auth/**"
```

**Best Practices:**
- Write clear, specific descriptions
- Include keywords users would mention
- Use explicit triggers for technical terms, abbreviations
- Don't over-specify - let Claude's context-aware selection work

**Example (QA Agent):**
```yaml
description: Quality assurance validation specialist. Use for validating acceptance
  criteria, testing implementations, and creating QA reports. Performs E2E testing
  for frontend changes using Electron MCP.
triggers:
  - keyword: qa
  - keyword: test
  - keyword: validate
  - keyword: acceptance criteria
```

### 5. Model Selection

**Options:**
- `sonnet` - Balanced performance (default for most tasks)
- `opus` - Maximum capability (complex reasoning, large context)
- `haiku` - Fast & efficient (simple tasks, quick iterations)
- `inherit` - Use parent agent's model (for subagents)

**Auto-Claude Strategy:**
- **Spec Creator**: `sonnet` - Balanced requirements gathering
- **Autonomous Builder**: `sonnet` - Balanced implementation
- **QA Loop**: `sonnet` - Thorough validation
- **Archon Sync**: `haiku` - Simple API operations
- **Session Analytics**: `haiku` - Fast analysis queries

**Key Insight:** Model selection is task-specific. Use haiku for simple operations (cost efficiency), sonnet for balanced work (default), opus for complex reasoning (rare, high-value tasks).

### 6. Skill-Agent Relationship

**Skills** (`.claude/skills/`) are high-level capabilities:
- Invoked by user through natural language
- May coordinate multiple agents
- Define workflows and orchestration

**Agents** (`.claude/agents/`) are focused executors:
- Wrap specific CLI tools
- Handle single responsibilities
- Invoked by skills or directly by Claude

**Example Hierarchy:**
```
auto-claude-spec skill
  → spec-creator-agent
    → spec_runner.py CLI

auto-claude-build skill
  → autonomous-builder-agent
    → run.py CLI
      → planner agent
      → coder agent(s)
      → qa-loop-agent
```

**Key Insight:** Skills provide high-level UX, agents provide focused execution. This separation enables composability and reusability.

### 7. IndyDev Template Patterns Not Yet Adopted

**Hooks System:**
- Lifecycle automation (PreToolUse, PostToolUse, Stop, etc.)
- Auto-formatting, security validation, test running
- Current status: Documented in Archon guide, not yet implemented in Auto-Claude

**Slash Commands:**
- Quick workflow invocation (`/create-spec`, `/run-qa`, `/merge`)
- Current status: Documented pattern, not yet implemented

**Session State Management:**
- `.claude/data/sessions/<session_id>.json` for cross-hook coordination
- Current status: Graphiti handles session memory, state management pattern not adopted

**Shared Utilities:**
- `.claude/hooks/utils/` for reusable code (TTS, LLM providers, etc.)
- Current status: Not applicable to Auto-Claude's current needs

## Recommendations for Phase 4 Implementation

### 1. Adopt Sub-Agent Pattern (High Priority)

**Status:** Already implemented in Auto-Claude.

**Current Implementation:**
- 5 agents in `.claude/agents/`: spec-creator, autonomous-builder, qa-loop, archon-sync, session-analytics
- All follow IndyDev Template pattern (YAML frontmatter + Markdown)
- Tools permissions defined declaratively
- Model selection per-agent

**Recommendation:** Continue using this pattern for future agents. It's proven and aligns with ecosystem standards.

### 2. Create Template and Documentation (Completed)

**Deliverables:**
- ✅ `.claude/docs/sub-agent-development-guide.md` - Comprehensive guide
- ✅ `.claude/agents/TEMPLATE.md` - Ready-to-use template

**Next Steps:**
- Reference these docs when creating new agents
- Update onboarding documentation to include sub-agent patterns
- Add to contributor guidelines

### 3. Refine Existing Agents (Medium Priority)

**Current Gaps:**

| Agent | Gap | Recommendation |
|-------|-----|----------------|
| spec-creator | Good | No changes needed |
| autonomous-builder | Good | No changes needed |
| qa-loop | Missing E2E testing details | Add Electron MCP workflow examples |
| archon-sync | Missing implementation | Implement sync logic in hooks or dedicated script |
| session-analytics | Missing SFA integration | Ensure all SFAs are documented and accessible |

**Action Items:**
1. Enhance `qa-loop-agent.md` with Electron MCP E2E testing examples
2. Implement Archon sync in hooks (PostToolUse, Stop)
3. Test all agents with real user requests
4. Add error handling examples to each agent

### 4. Implement Hooks System (Future Phase)

**Priority:** Low (Phase 5 or 6)

**Rationale:**
- Sub-agents provide most value for Phase 4
- Hooks are powerful but add complexity
- Current Graphiti integration handles session insights
- Security validation already implemented in `core/security.py`

**If Implemented:**
- **PreToolUse**: Wrap existing `security.py` validation
- **PostToolUse**: Auto-formatting (black, prettier)
- **Stop**: Test running, Graphiti insights extraction
- **SessionStart**: Load Graphiti context

**Configuration:** `.claude/settings.json`

### 5. Model Selection Strategy (Apply Now)

**Current Status:** All agents use `model: sonnet` except session-analytics (haiku).

**Recommendations:**

| Agent | Current | Recommended | Reason |
|-------|---------|-------------|--------|
| spec-creator | sonnet | sonnet ✓ | Balanced requirements gathering |
| autonomous-builder | sonnet | sonnet ✓ | Balanced implementation |
| qa-loop | sonnet | sonnet ✓ | Thorough validation |
| archon-sync | sonnet | haiku ⚠️ | Simple API operations, cost efficiency |
| session-analytics | haiku | haiku ✓ | Fast analysis queries |

**Action Item:** Change `archon-sync-agent.md` model to `haiku` for cost efficiency.

### 6. Tool Permission Audit (Apply Now)

**Recommendation:** Ensure each agent has minimum required tools.

**Current Status:** All agents have appropriate tools except:
- **archon-sync**: Has `[Read, Glob, Grep, Write, mcp__archon]` - Consider if all needed

**Action Item:** Review archon-sync tools after implementation to ensure minimal permissions.

### 7. Integration Testing (High Priority)

**Current Gap:** Sub-agents not tested with real user requests.

**Recommendation:**

1. **Create Test Cases:**
   ```
   User: "create a spec for adding dark mode"
   Expected: spec-creator-agent invoked → spec_runner.py executed

   User: "build spec 001"
   Expected: autonomous-builder-agent invoked → run.py executed

   User: "run qa on spec 001"
   Expected: qa-loop-agent invoked → QA system executed

   User: "analyze costs for last week"
   Expected: session-analytics-agent invoked → SFA executed
   ```

2. **Test Agent Coordination:**
   ```
   User: "create and build a spec for feature X"
   Expected: spec-creator → autonomous-builder coordination
   ```

3. **Document Results:**
   - Create test report: `.claude/docs/agent-test-results.md`
   - Note any issues, edge cases
   - Update agent definitions based on findings

### 8. Contributor Documentation (Medium Priority)

**Current Gap:** No contributor guide for creating new agents.

**Recommendation:**

1. **Update CLAUDE.md:**
   - Add section: "Creating Sub-Agents"
   - Reference development guide and template
   - Include quick start example

2. **Update README.md:**
   - Add section: "Sub-Agents"
   - List available agents with descriptions
   - Link to development guide

3. **Create Contributor Guide:**
   - Path: `.claude/docs/contributor-guide.md`
   - Include: Agent creation, testing, PR process
   - Reference TEMPLATE.md and development guide

## Implementation Checklist

### Completed ✅
- [x] Research IndyDev Template patterns
- [x] Analyze existing Auto-Claude agents
- [x] Create comprehensive development guide
- [x] Create TEMPLATE.md with full schema
- [x] Document findings and recommendations

### Immediate Actions (Week 1-2)
- [ ] Update `archon-sync-agent.md` model to `haiku`
- [ ] Enhance `qa-loop-agent.md` with E2E testing examples
- [ ] Create test cases for all 5 agents
- [ ] Test agents with real user requests
- [ ] Document test results

### Short-term Actions (Week 3-4)
- [ ] Update CLAUDE.md with sub-agent section
- [ ] Update README.md with sub-agent documentation
- [ ] Create contributor guide
- [ ] Add sub-agent patterns to onboarding
- [ ] Review and refine tool permissions

### Medium-term Actions (Month 2-3)
- [ ] Implement Archon sync logic (hooks or script)
- [ ] Add error handling examples to all agents
- [ ] Create agent coordination tests
- [ ] Document agent orchestration patterns

### Future Considerations (Phase 5+)
- [ ] Implement hooks system (.claude/settings.json)
- [ ] Add slash commands for quick workflows
- [ ] Consider session state management pattern
- [ ] Evaluate shared utilities structure

## Key Insights for Phase 4

1. **CLI Wrapping is Core Pattern** - Sub-agents wrap existing CLI tools for natural language UX. This enables reusability and maintainability.

2. **Tool Permissions Enable Security** - Declarative tool restrictions in frontmatter provide fine-grained security without code changes.

3. **Trigger Patterns are Descriptions** - Clear, specific descriptions act as primary triggers. Explicit triggers are secondary and optional.

4. **Model Selection is Task-Specific** - Use haiku for simple operations, sonnet for balanced work, opus for complex reasoning (rare).

5. **Skills Coordinate Agents** - Skills provide high-level workflows, agents provide focused execution. This separation enables composability.

6. **Template Accelerates Development** - TEMPLATE.md provides a starting point with all required sections, inline documentation, and examples.

7. **Documentation is Critical** - Comprehensive documentation (development guide, template, examples) enables consistent agent creation.

## Success Metrics for Phase 4

1. **Agent Coverage** - 5 core agents implemented (✅ Complete)
2. **Documentation Quality** - Guide + template + examples (✅ Complete)
3. **Pattern Consistency** - All agents follow template (✅ Complete)
4. **Integration Testing** - All agents tested with real requests (⏳ Pending)
5. **User Experience** - Natural language invocation works smoothly (⏳ Pending)

## Next Steps

1. **Test Agents** - Create test cases, validate with real user requests
2. **Refine Based on Testing** - Update agents based on test findings
3. **Update Documentation** - Add sub-agent docs to CLAUDE.md and README.md
4. **Create Contributor Guide** - Enable community contributions
5. **Plan Phase 5** - Evaluate hooks system, slash commands, advanced features

## Conclusion

Auto-Claude's sub-agent implementation follows IndyDev Template patterns and Claude Code ecosystem standards. The pattern is proven, well-documented, and ready for testing.

**Key Success Factors:**
- CLI wrapping pattern enables reusability
- Tool permissions provide security
- Trigger patterns enable natural language UX
- Model selection optimizes cost/performance
- Skills-agent separation enables composability

**Immediate Focus:**
1. Test all agents with real user requests
2. Refine based on testing
3. Update project documentation

**Future Phases:**
- Phase 5: Hooks system for lifecycle automation
- Phase 6: Slash commands for quick workflows
- Phase 7: Advanced coordination patterns

The foundation is solid. Now it's time to test, refine, and document for broader use.

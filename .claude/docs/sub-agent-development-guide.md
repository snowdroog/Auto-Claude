# Sub-Agent Development Guide

This guide explains how to create and manage sub-agents in Auto-Claude, following the IndyDev Template pattern and Claude Code ecosystem best practices.

## Table of Contents

1. [What are Sub-Agents?](#what-are-sub-agents)
2. [File Structure](#file-structure)
3. [Agent Definition Format](#agent-definition-format)
4. [CLI Wrapping Pattern](#cli-wrapping-pattern)
5. [Tool Permissions](#tool-permissions)
6. [Trigger Patterns](#trigger-patterns)
7. [Integration with Skills](#integration-with-skills)
8. [Best Practices](#best-practices)
9. [Examples](#examples)

## What are Sub-Agents?

Sub-agents are specialized AI agents defined as Markdown files with YAML frontmatter. They provide:

- **Natural Language UX** - Users can invoke agents through conversational requests
- **CLI Wrapping** - Agents wrap existing command-line tools for accessibility
- **Role Specialization** - Each agent has focused capabilities and tool permissions
- **Composability** - Multiple agents can work together on complex tasks

**Key Difference from Core Agents:**
- **Core agents** (in `apps/backend/agents/*.py`) - Complex multi-session workflows with state management
- **Sub-agents** (in `.claude/agents/*.md`) - Natural language interfaces to CLI tools and focused tasks

## File Structure

Sub-agents live in the `.claude/agents/` directory:

```
.claude/
├── agents/
│   ├── spec-creator-agent.md      # Wraps spec_runner.py
│   ├── autonomous-builder-agent.md # Wraps run.py
│   ├── qa-loop-agent.md           # Wraps QA system
│   ├── archon-sync-agent.md       # Wraps Archon MCP tools
│   └── session-analytics-agent.md # Wraps SFA tools
└── skills/
    └── {skill-name}/
        └── SKILL.md               # Skill definitions (invoke agents)
```

**Storage Levels:**
- **Project-level**: `.claude/agents/*.md` - Available only in current project
- **User-level**: `~/.claude/agents/*.md` - Available in all projects (personal tools)

**Recommendation**: Use project-level for Auto-Claude-specific agents, user-level for general utilities.

## Agent Definition Format

Agents are Markdown files with YAML frontmatter:

```markdown
---
name: agent-name
version: 1.0.0
description: Clear description of what the agent does and when to use it. Include keywords for triggering.
tools: [Read, Glob, Grep, Write, Edit, Bash, mcp__*]
model: sonnet
---

# Agent Name

Your detailed instructions for Claude go here...

## Your Role

You are [role description]. Your responsibilities include...

## Workflow

1. Step-by-step process
2. Commands to execute
3. Expected outcomes

## Key Responsibilities

- Responsibility 1
- Responsibility 2

## Tips

- Best practices
- Common pitfalls to avoid
```

### Frontmatter Fields

| Field | Required | Values | Description |
|-------|----------|--------|-------------|
| `name` | Yes | kebab-case string | Agent identifier (matches filename) |
| `version` | Yes | semver (e.g., 1.0.0) | Agent version |
| `description` | Yes | string | What the agent does, when to use it. Acts as trigger. |
| `tools` | Yes | array of tool names | Tools agent can use (see Tool Permissions) |
| `model` | No | sonnet/opus/haiku/inherit | Model to use (defaults to inherit if omitted) |
| `triggers` | No | array of keywords | Explicit trigger patterns (optional, description also acts as trigger) |

### Model Selection Strategy

```yaml
model: sonnet    # Balanced - most tasks (default)
model: opus      # Maximum capability - complex reasoning
model: haiku     # Fast & efficient - simple tasks, quick iterations
model: inherit   # Use parent agent's model (for subagents)
```

**Auto-Claude Model Recommendations:**
- **Spec Creator**: `sonnet` - Balanced requirements gathering
- **Autonomous Builder**: `sonnet` - Balanced implementation
- **QA Loop**: `sonnet` - Thorough validation
- **Archon Sync**: `haiku` - Simple API operations
- **Session Analytics**: `haiku` - Fast analysis queries

## CLI Wrapping Pattern

**Key Principle**: Sub-agents provide natural language interfaces to existing command-line tools.

### Pattern Structure

1. **User Request** (Natural Language)
   ```
   "create a spec for adding dark mode"
   ```

2. **Agent Invocation** (Claude selects appropriate agent based on description)
   ```
   spec-creator-agent (matches description: "Creates feature specifications...")
   ```

3. **CLI Execution** (Agent wraps existing tool)
   ```bash
   cd apps/backend && python spec_runner.py --task "Add dark mode toggle"
   ```

4. **Response** (Agent interprets output, guides next steps)
   ```
   Spec created at .auto-claude/specs/001-dark-mode/
   Next: Review spec.md, then run autonomous build with auto-claude-build skill
   ```

### CLI Wrapping Example

```markdown
---
name: spec-creator-agent
description: Creates feature specifications through multi-phase discovery process.
tools: [Read, Glob, Grep, Write, Edit, WebFetch, WebSearch, Bash]
model: sonnet
---

# Spec Creator Agent

You are the Spec Creator Agent. Your role is to guide users through creating
comprehensive feature specifications.

## Workflow

Execute Auto-Claude's spec creation CLI:

```bash
cd apps/backend && python spec_runner.py --interactive
```

Or for quick specs:

```bash
python spec_runner.py --task "Add user authentication with OAuth"
```

The spec runner will guide through phases based on complexity:
- **SIMPLE** (3 phases): Discovery → Quick Spec → Validate
- **STANDARD** (6-7 phases): Discovery → Requirements → [Research] → Context → Spec → Plan → Validate
- **COMPLEX** (8 phases): Full pipeline with Research and Self-Critique

## Key Responsibilities

1. **Clarify Requirements** - Ask focused questions to understand the feature
2. **Assess Complexity** - Determine appropriate spec pipeline depth
3. **Execute Spec Runner** - Use spec_runner.py with appropriate flags
4. **Validate Output** - Ensure spec has clear acceptance criteria
5. **Prepare for Build** - Confirm spec is ready for autonomous implementation
```

### Why CLI Wrapping?

1. **Reusability** - Leverage existing, tested command-line tools
2. **Accessibility** - Natural language interface lowers barrier to entry
3. **Maintainability** - Update CLI tool, agent automatically benefits
4. **Composability** - Agents can chain CLI tools in workflows

## Tool Permissions

Tools field restricts what agent can use. This enables focused, secure agents.

### Tool Categories

**File Operations:**
- `Read` - Read files (read-only analysis)
- `Grep` - Search file contents
- `Glob` - Find files by pattern
- `Write` - Create new files
- `Edit` - Modify existing files

**Command Execution:**
- `Bash` - Full bash access (use carefully)
- `Bash(git:*)` - Scoped bash (only git commands)
- `Bash(python:*)` - Scoped bash (only python commands)

**Web Access:**
- `WebFetch` - Fetch web content
- `WebSearch` - Search the web

**MCP Tools:**
- `mcp__archon__*` - All Archon tools
- `mcp__electron__*` - All Electron MCP tools
- `mcp__archon__rag_search_knowledge_base` - Specific tool

### Tool Permission Examples

```yaml
# Read-only analyzer (safe, no modifications)
tools: [Read, Grep, Glob]

# Full-stack coder (needs all tools)
tools: [Read, Edit, Write, Bash, Grep, Glob]

# Git automation (scoped bash access)
tools: [Bash(git:*), Read]

# Archon integration (MCP tools)
tools: [Read, Glob, Grep, Write, mcp__archon__*]

# QA with E2E testing
tools: [Read, Grep, Glob, Bash(git:*), mcp__electron__*]
```

### Auto-Claude Tool Permissions

| Agent | Tools | Rationale |
|-------|-------|-----------|
| spec-creator | Read, Glob, Grep, Write, Edit, WebFetch, WebSearch, Bash | Full research & spec creation |
| autonomous-builder | Read, Glob, Grep, Write, Edit, Bash | Full implementation access |
| qa-loop | Read, Glob, Grep, Write, Edit, Bash | Validation & reporting |
| archon-sync | Read, Glob, Grep, Write, mcp__archon__* | Archon integration only |
| session-analytics | Read, Glob, Grep, Bash, mcp__archon__* | Analysis & reporting |

## Trigger Patterns

Trigger patterns help Claude decide when to delegate to an agent.

### Implicit Triggers (Description)

**Best Practice**: Write clear, specific descriptions that indicate when to use the agent.

```yaml
description: Creates feature specifications through multi-phase discovery process.
  PROACTIVELY use when user wants to define a new feature, enhancement, or bug fix.
```

**Keywords to include:**
- Action verbs: "create", "build", "analyze", "validate", "sync"
- Domain terms: "specification", "implementation", "QA", "analytics"
- Use cases: "when user wants to...", "use for..."

### Explicit Triggers (Optional)

```yaml
triggers:
  - keyword: authentication
  - keyword: auth
  - keyword: login
  - file_pattern: "**/auth/**"
```

**When to use explicit triggers:**
- Specific technical terms (e.g., "OAuth", "JWT")
- File patterns (e.g., testing agent for `**/tests/**`)
- Abbreviations (e.g., "qa" for quality assurance)

### Trigger Examples

```yaml
# QA Agent
description: Quality assurance validation specialist. Use for validating acceptance
  criteria, testing implementations, and creating QA reports.
triggers:
  - keyword: qa
  - keyword: test
  - keyword: validate
  - keyword: acceptance criteria

# Security Reviewer
description: Security analysis expert. Use for security reviews, vulnerability
  scanning, and identifying security issues in authentication, authorization,
  or data handling code.
triggers:
  - keyword: security
  - keyword: vulnerability
  - keyword: auth
  - keyword: authorization
  - keyword: sensitive data
```

## Integration with Skills

Skills (in `.claude/skills/`) invoke sub-agents through natural language context.

### Skill → Agent Relationship

**Skills** are high-level capabilities that may use multiple agents:
```
auto-claude-spec skill → spec-creator-agent
auto-claude-build skill → autonomous-builder-agent → coder agent(s) → qa-loop-agent
```

**Agents** are focused executors that wrap specific CLI tools:
```
spec-creator-agent → spec_runner.py CLI
autonomous-builder-agent → run.py CLI
```

### Skill Definition Example

```markdown
---
name: auto-claude-spec
description: Create feature specifications through Auto-Claude's guided discovery process
triggers:
  - create a spec
  - new specification
  - define a feature
model: sonnet
---

# Auto-Claude Spec Creation Skill

You are an Auto-Claude Spec Creator. Your role is to guide users through creating
comprehensive feature specifications.

## When to Use

Use this skill when the user wants to:
- Create a new feature specification
- Define requirements for a new feature
- Document a bug fix or enhancement

## How to Execute

Delegate to the spec-creator-agent:

"I'll help you create a spec. Let me invoke the spec creator agent."

[Claude automatically selects spec-creator-agent based on context]

## What Gets Created

The spec creation process generates:
- **spec.md** - Feature specification with acceptance criteria
- **requirements.json** - Structured requirements
- **context.json** - Discovered codebase context
- **implementation_plan.json** - Subtask-based implementation plan
```

### Coordination Pattern

Skills enable **automatic multi-agent coordination**:

```
User: "create a spec for dark mode and build it"

Claude:
1. Invokes auto-claude-spec skill
   → Delegates to spec-creator-agent
   → Runs spec_runner.py
   → Creates spec.md

2. Invokes auto-claude-build skill
   → Delegates to autonomous-builder-agent
   → Runs run.py
   → Executes build pipeline
```

**No explicit agent references needed** - Claude's context-aware selection handles coordination.

## Best Practices

### 1. Single Responsibility Principle

Each agent should wrap ONE CLI tool or handle ONE focused task.

**Good:**
```yaml
name: spec-creator-agent
description: Creates feature specifications using spec_runner.py
# Wraps spec_runner.py only
```

**Bad:**
```yaml
name: spec-and-build-agent
description: Creates specs AND runs builds
# Tries to do too much - split into two agents
```

### 2. Clear CLI Execution Patterns

Always show the exact command in the agent definition:

```markdown
## Workflow

Execute Auto-Claude's CLI:

```bash
cd apps/backend && python run.py --spec 001
```
```

### 3. Tool Permission Minimization

Give agents only the tools they need:

```yaml
# Analytics agent doesn't need Write/Edit
tools: [Read, Glob, Grep, Bash]

# Builder agent needs full access
tools: [Read, Glob, Grep, Write, Edit, Bash]
```

### 4. User Guidance in Responses

Always guide users on next steps:

```markdown
## After Build Completion

1. **Review**: `python run.py --spec 001 --review`
2. **Test**: Manual testing in `.worktrees/001-name/`
3. **Merge**: `python run.py --spec 001 --merge`
4. **Discard**: `python run.py --spec 001 --discard`
```

### 5. Error Handling

Anticipate common errors and provide guidance:

```markdown
## Troubleshooting

If spec creation fails:
- Check that you're in the project root
- Verify `apps/backend/` directory exists
- Ensure Python 3.12+ is available
- Run `uv pip install -r requirements.txt`
```

### 6. Integration Documentation

Document how the agent fits in the broader system:

```markdown
## Integration

This agent wraps the existing `spec_runner.py` CLI. It provides a natural
language interface to Auto-Claude's sophisticated spec creation pipeline.

## Related Agents

- **autonomous-builder-agent** - Implements specs created by this agent
- **qa-loop-agent** - Validates implementations
```

### 7. Version Control

Use semantic versioning in frontmatter:

```yaml
version: 1.0.0  # Major.Minor.Patch

# Increment:
# - Major: Breaking changes to agent interface
# - Minor: New features, capabilities
# - Patch: Bug fixes, documentation updates
```

### 8. Documentation First

Write agent documentation before implementation:
1. Define agent's role and responsibilities
2. Map out CLI commands to wrap
3. Document expected inputs/outputs
4. Create frontmatter with tool permissions
5. Test with example user requests

## Examples

### Example 1: Spec Creator Agent

**Purpose**: Wrap `spec_runner.py` for natural language spec creation.

```markdown
---
name: spec-creator-agent
version: 1.0.0
description: Creates feature specifications through multi-phase discovery process. PROACTIVELY use when user wants to define a new feature, enhancement, or bug fix.
tools: [Read, Glob, Grep, Write, Edit, WebFetch, WebSearch, Bash]
model: sonnet
---

# Spec Creator Agent

You are the Spec Creator Agent for Auto-Claude. Your role is to guide users
through a structured discovery process to create comprehensive feature
specifications that can be built autonomously.

## Workflow

Execute Auto-Claude's spec creation CLI:

```bash
cd apps/backend && python spec_runner.py --interactive
```

Or for quick specs:

```bash
python spec_runner.py --task "Add user authentication with OAuth"
```

The spec runner will guide through phases based on complexity:
- **SIMPLE** (3 phases): Discovery → Quick Spec → Validate
- **STANDARD** (6-7 phases): Discovery → Requirements → [Research] → Context → Spec → Plan → Validate
- **COMPLEX** (8 phases): Full pipeline with Research and Self-Critique

## Key Responsibilities

1. **Clarify Requirements** - Ask focused questions to understand the feature
2. **Assess Complexity** - Determine appropriate spec pipeline depth
3. **Execute Spec Runner** - Use spec_runner.py with appropriate flags
4. **Validate Output** - Ensure spec has clear acceptance criteria
5. **Prepare for Build** - Confirm spec is ready for autonomous implementation

## Integration

This agent wraps the existing `spec_runner.py` CLI. It provides a natural
language interface to Auto-Claude's sophisticated spec creation pipeline.

## Tips

- Use `--interactive` for first-time users or complex features
- Use `--task "description"` for quick, well-defined specs
- Force complexity with `--complexity simple|standard|complex` if needed
- Check output in `.auto-claude/specs/NNN-feature-name/`
```

### Example 2: Session Analytics Agent

**Purpose**: Wrap SFA tools for session analysis and cost tracking.

```markdown
---
name: session-analytics-agent
version: 1.0.0
description: Analyzes Auto-Claude session data for cost tracking, performance metrics, pattern detection, and failure investigation.
tools: [Read, Glob, Grep, Bash, mcp__archon]
model: haiku
---

# Session Analytics Agent

You are the Session Analytics Agent. Your role is to analyze Auto-Claude
session data to provide insights on costs, performance, patterns, and quality
metrics.

## Workflow

Use Single-File Agents (SFAs) for analysis:

### Cost Analysis
```bash
uv run apps/backend/single-file-agents/agents/sfa_session_cost_tracker_anthropic_v1.py \
  --days 7 \
  --group-by spec
```

### Natural Language Queries
```bash
uv run apps/backend/single-file-agents/agents/sfa_events_analyzer_anthropic_v1.py \
  --db .auto-claude/events.db \
  --prompt "What tools were used most in the last build?"
```

### Loop Detection
```bash
uv run apps/backend/single-file-agents/agents/sfa_loop_detector_report_anthropic_v1.py \
  --db .auto-claude/events.db \
  --severity high
```

## Key Responsibilities

1. **Cost Tracking** - Monitor token usage and costs by model, phase, spec
2. **Performance Analysis** - Track phase duration, tool latency
3. **Pattern Detection** - Identify common errors, successful patterns
4. **Failure Investigation** - Root cause analysis for failed builds
5. **Report Generation** - Create summary reports

## Data Sources

| Source | Location | Contains |
|--------|----------|----------|
| OTEL Traces | Phoenix UI (localhost:6006) | Span hierarchy, durations |
| Events DB | `.auto-claude/events.db` | Sessions, tools, messages |
| Hook Logs | `.claude/hooks/hooks.log` | Tool usage, security events |
| Graphiti | `.auto-claude/specs/NNN/graphiti/` | Session insights |

## Tips

- Run cost analysis weekly to track trends
- Investigate failures immediately after occurrence
- Use loop detection to catch stuck agents early
- Store insights in Archon RAG for cross-session learning
```

### Example 3: QA Loop Agent

**Purpose**: Wrap QA system for validation and fix loops.

```markdown
---
name: qa-loop-agent
version: 1.0.0
description: Quality assurance validation and fix loop coordination. Use when user wants to validate a build, run QA manually, or resolve QA issues.
tools: [Read, Glob, Grep, Write, Edit, Bash]
model: sonnet
---

# QA Loop Agent

You are the QA Loop Agent. Your role is to coordinate quality assurance
validation and guide the iterative fix process for Auto-Claude builds.

## Workflow

Execute Auto-Claude's QA CLI:

```bash
cd apps/backend && python run.py --spec 001 --qa
```

The QA process:
1. **Load Spec** - Read spec.md for acceptance criteria
2. **Run QA Reviewer** - Validate build against criteria
3. **Generate Report** - Create qa_report.md with findings
4. **Fix Loop** - If rejected, QA Fixer resolves issues
5. **Iterate** - Repeat until accepted or max attempts

## QA Commands

```bash
# Run QA validation
python run.py --spec 001 --qa

# Check QA status
python run.py --spec 001 --qa-status

# View QA report
cat .auto-claude/specs/001-name/qa_report.md
```

## Key Responsibilities

1. **Validate Against Spec** - Ensure all acceptance criteria met
2. **Run Tests** - Execute test suites if available
3. **Check Build** - Verify build succeeds
4. **E2E Testing** - For frontend changes (via Electron MCP)
5. **Generate Report** - Document findings clearly
6. **Guide Fixes** - Help interpret QA feedback

## QA Criteria

The QA Reviewer validates:
- **Acceptance Criteria** - All criteria from spec.md met
- **Tests** - All tests pass (if test suite exists)
- **Build** - Project builds successfully
- **Functionality** - Feature works as described
- **Quality** - Code quality meets standards

## Fix Loop

If QA rejects:
1. **Review Report** - Check `.auto-claude/specs/NNN/qa_report.md`
2. **Run QA Fixer** - Automatically attempts fixes
3. **Re-validate** - QA Reviewer checks again
4. **Iterate** - Up to max attempts (default: 3)

## Tips

- Always run QA before merging
- Review QA reports carefully
- If QA keeps failing, spec may need refinement
- Check `QA_FIX_REQUEST.md` for detailed fix guidance
- E2E testing available for Electron frontend (requires app running)
```

## Summary

Sub-agents in Auto-Claude follow these principles:

1. **CLI Wrapping** - Natural language interface to command-line tools
2. **Role Specialization** - Each agent wraps one tool or handles one task
3. **Tool Permissions** - Declarative tool restrictions in frontmatter
4. **Trigger Patterns** - Clear descriptions act as selection criteria
5. **Composability** - Multiple agents coordinate through skills
6. **User Guidance** - Always provide next steps and error handling

**Next Steps:**
1. Use `TEMPLATE.md` as starting point for new agents
2. Follow naming conventions (kebab-case, descriptive)
3. Test agent with example user requests
4. Document integration points with other agents/skills
5. Add to Auto-Claude ecosystem documentation

## Additional Resources

- **IndyDev Template Pattern Analysis**: Archon document ID `ce20d28c-f93a-4e92-b5af-5c6da0a30acc`
- **Existing Agents**: `.claude/agents/*.md` for working examples
- **Skills Documentation**: `.claude/skills/*/SKILL.md` for skill integration
- **Auto-Claude CLAUDE.md**: Project instructions and architecture
- **Claude Code Documentation**: https://code.claude.com/docs/

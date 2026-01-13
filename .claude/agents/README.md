# Auto-Claude Sub-Agent System

Natural language interface for Auto-Claude's autonomous development workflows through specialized sub-agents.

## Overview

The Auto-Claude sub-agent system provides conversational interfaces to Auto-Claude's CLI tools. Instead of running commands directly, users describe what they want in natural language, and Claude delegates to specialized sub-agents that orchestrate the workflows.

**Key Benefits:**
- **Natural Language**: "create a spec for X" instead of `python spec_runner.py --task "X"`
- **Context Aware**: Agents understand project state and previous conversations
- **Error Handling**: Agents provide guidance when things go wrong
- **Progress Reporting**: Real-time updates on multi-phase operations
- **Workflow Coordination**: Agents handle complex multi-step processes

## Available Sub-Agents

### 1. Spec Creator Agent
**File:** `spec-creator-agent.md`
**Model:** Sonnet
**Skill:** `auto-claude-spec`

Creates feature specifications through Auto-Claude's multi-phase discovery process.

**Trigger Phrases:**
- "create a spec for X"
- "new specification for Y"
- "define a feature Z"

**What It Does:**
- Executes `spec_runner.py` with appropriate flags
- Guides through interactive or quick mode
- Assesses complexity (SIMPLE/STANDARD/COMPLEX)
- Creates comprehensive spec with acceptance criteria

**Example:**
```
User: "Create a spec for adding OAuth authentication"

Agent:
- Detects spec creation intent
- Asks interactive vs quick mode preference
- Runs spec_runner.py
- Reports progress through discovery phases
- Outputs spec to .auto-claude/specs/NNN-oauth/
```

---

### 2. Autonomous Builder Agent
**File:** `autonomous-builder-agent.md`
**Model:** Sonnet
**Skill:** `auto-claude-build`

Executes autonomous builds using the multi-phase implementation pipeline.

**Trigger Phrases:**
- "build this autonomously"
- "implement spec 001"
- "run auto-claude on spec 002"

**What It Does:**
- Executes `run.py` with spec ID
- Manages plan → code → QA → fix pipeline
- Reports progress through each phase
- Handles worktree isolation
- Provides merge/review/discard options

**Example:**
```
User: "Build spec 001 autonomously"

Agent:
- Creates isolated worktree
- Planning: Creates implementation subtasks
- Coding: Implements each subtask (can parallelize)
- QA: Validates acceptance criteria
- Reports: Success/failure with next steps
```

---

### 3. QA Loop Agent
**File:** `qa-loop-agent.md`
**Model:** Sonnet
**Skill:** Invoked by `auto-claude-build` or manual request

Coordinates quality assurance validation and fix loops.

**Trigger Phrases:**
- "run QA on spec X"
- "validate the build"
- "test spec Y"

**What It Does:**
- Executes `run.py --qa`
- Runs qa_reviewer to validate acceptance criteria
- On failure: Activates qa_fixer in loop
- Supports E2E testing for frontend changes
- Generates qa_report.md

**Example:**
```
User: "Run QA on spec 003"

Agent:
- Loads spec and acceptance criteria
- Validates each criterion
- Runs tests, builds project
- Reports PASS/FAIL with details
- If FAIL: Enters fix loop automatically
```

---

### 4. Archon Sync Agent
**File:** `archon-sync-agent.md`
**Model:** Haiku
**Skill:** `archon`

Synchronizes Auto-Claude specs, tasks, and insights with Archon for cross-session learning.

**Trigger Phrases:**
- "sync to archon"
- "update archon tasks"
- "store insights in archon"

**What It Does:**
- Creates Archon projects for specs
- Syncs implementation plan as tasks
- Stores specs, QA reports, insights
- Updates task status during builds
- Enables cross-spec pattern discovery

**Example:**
```
User: "Sync spec 001 to Archon"

Agent:
- Reads spec.md and implementation_plan.json
- Creates Archon project
- Creates tasks for each subtask
- Stores spec as document
- Saves project ID for future sync
```

---

### 5. Session Analytics Agent
**File:** `session-analytics-agent.md`
**Model:** Haiku
**Skill:** `observability`

Analyzes Auto-Claude session data for cost tracking, performance metrics, and failure investigation.

**Trigger Phrases:**
- "analyze session costs"
- "how much did spec X cost?"
- "detect patterns in recent builds"
- "why did spec Y fail?"

**What It Does:**
- Executes observability SFAs (single-file agents)
- Tracks token usage and API costs
- Detects loops and stuck states
- Investigates build failures
- Compares performance across specs

**Example:**
```
User: "How much did spec 001 cost to build?"

Agent:
- Executes sfa_session_cost_tracker_anthropic_v1.py
- Queries events database
- Provides cost breakdown by phase
- Compares to average costs
- Suggests optimizations
```

---

## How Sub-Agents Work

### 1. Trigger Detection

Claude detects intent through:
- **Explicit keywords** in trigger list
- **Description matching** (implicit triggers)
- **Conversational context** (previous messages)

### 2. Agent Delegation

When Claude detects a match:
```
User Request
    ↓
Claude analyzes intent
    ↓
Delegates to appropriate sub-agent
    ↓
Agent executes workflow
    ↓
Agent reports results to user
```

### 3. Tool Permissions

Each agent has restricted tools based on its role:

| Agent | Tools |
|-------|-------|
| Spec Creator | `[Read, Glob, Grep, Write, Bash]` |
| Builder | `[Read, Glob, Grep, Write, Edit, Bash]` |
| QA Loop | `[Read, Grep, Glob, Bash(git:*), mcp__electron__*]` |
| Archon Sync | `[Read, Glob, Grep, Write, mcp__archon__*]` |
| Analytics | `[Read, Glob, Grep, Bash]` |

### 4. Model Selection

Each agent uses the optimal model:
- **Sonnet**: Spec Creator, Builder, QA Loop (complex reasoning)
- **Haiku**: Archon Sync, Analytics (fast, efficient operations)

---

## Sub-Agent Template Structure

Every sub-agent follows this template (`TEMPLATE.md`):

### YAML Frontmatter
```yaml
---
name: agent-name
version: 1.0.0
description: Brief description. PROACTIVELY use when user wants to [use case].
tools: [Read, Glob, Grep, Write, Edit, Bash]
model: sonnet
triggers:
  - keyword: trigger-phrase
  - keyword: alternative-phrase
---
```

### Markdown Content
```markdown
# Agent Name

You are the [Agent Name] for Auto-Claude. Your role is to [primary responsibility].

## Your Role
- Responsibility 1
- Responsibility 2

## Workflow
Step-by-step execution process

## Key Responsibilities
Detailed responsibilities

## Expected Inputs/Outputs
Tables defining I/O

## Integration
Related agents and skills

## Usage Examples
Real-world scenarios

## Error Handling
Common errors and solutions

## Troubleshooting
Debugging guidance

## Tips
Best practices
```

---

## Creating New Sub-Agents

### 1. Define Purpose

Ask:
- What CLI tool does this wrap?
- What workflow does it orchestrate?
- When should it be triggered?
- What tools does it need?

### 2. Copy Template

```bash
cp .claude/agents/TEMPLATE.md .claude/agents/new-agent.md
```

### 3. Fill Frontmatter

```yaml
name: new-agent
version: 1.0.0
description: Clear description with PROACTIVELY use case
tools: [Minimum required tools]
model: sonnet  # or haiku for simple tasks
triggers:
  - keyword: natural phrase
  - keyword: alternative phrase
```

### 4. Write Content

- **Clear role description**: What is this agent for?
- **Step-by-step workflow**: How does it execute?
- **Usage examples**: 3-5 realistic scenarios
- **Error handling**: Common issues and fixes
- **Integration notes**: How it fits with other agents

### 5. Test Triggers

Verify Claude detects triggers:
```
User: [trigger phrase]
→ Should delegate to your agent
```

### 6. Document in README

Add entry to "Available Sub-Agents" section above.

---

## Usage Patterns

### Pattern 1: Sequential Workflow
```
User: "Create a spec for dark mode"
→ spec-creator-agent

User: "Build it"
→ autonomous-builder-agent

User: "Sync to Archon"
→ archon-sync-agent
```

### Pattern 2: Conditional Branching
```
User: "Implement spec 005"
→ autonomous-builder-agent

If QA fails:
  → qa-loop-agent activates automatically

If user asks "why did it fail?":
  → session-analytics-agent investigates
```

### Pattern 3: Proactive Analysis
```
After expensive build:
  User: "How much did that cost?"
  → session-analytics-agent (proactive cost tracking)

After repeated failures:
  User: "Analyze the patterns"
  → session-analytics-agent (loop detection)
```

---

## Integration with Skills

Sub-agents are invoked through skills (`.claude/skills/`):

| Skill | Sub-Agent(s) | Purpose |
|-------|--------------|---------|
| `auto-claude-spec` | spec-creator-agent | Spec creation |
| `auto-claude-build` | autonomous-builder-agent | Build execution |
| `archon` | archon-sync-agent | Data synchronization |
| `observability` | session-analytics-agent | Analytics |
| `single-file-agents` | (direct SFA execution) | Quick utilities |

**How Skills Work:**
1. User mentions skill-related phrase
2. Claude checks if skill should be invoked
3. Skill documentation guides Claude
4. Claude delegates to appropriate sub-agent
5. Sub-agent executes and reports back

---

## Trigger Reference

Quick reference for all trigger phrases:

### Spec Creation
- "create a spec", "new specification", "define a feature"

### Building
- "build this", "implement spec", "run auto-claude"

### QA Validation
- "run QA", "validate build", "test spec"

### Archon Sync
- "sync to archon", "update archon", "store insights"

### Session Analytics
- "analyze costs", "investigate failure", "detect patterns"

**Context Awareness:**
Agents also respond to contextual phrases:
- "build it" (after creating spec)
- "analyze it" (after build failure)
- "sync everything" (after successful build)

---

## Troubleshooting

### Agent Not Triggering

**Problem:** Claude doesn't delegate to agent

**Solutions:**
1. **Use explicit triggers**: "create a spec" vs "make a spec"
2. **Check description**: Is intent in PROACTIVELY clause?
3. **Add more triggers**: Update frontmatter with variations
4. **Test isolation**: "I want to use the spec-creator-agent to..."

### Agent Executes Wrong Command

**Problem:** Agent runs incorrect CLI command

**Solutions:**
1. **Check Workflow section**: Are commands documented correctly?
2. **Update examples**: Add example showing correct usage
3. **Clarify in prompt**: "Use --interactive flag for..."

### Agent Lacks Permissions

**Problem:** Agent can't access needed tools

**Solutions:**
1. **Update tools list**: Add required tool to frontmatter
2. **Use scoped Bash**: `Bash(git:*)` instead of full `Bash`
3. **Check tool availability**: Verify tool exists in Claude Code

### Model Too Slow/Expensive

**Problem:** Agent using wrong model tier

**Solutions:**
1. **Switch to Haiku**: For simple/fast operations
2. **Use Sonnet**: For complex reasoning/planning
3. **Default to inherit**: Let parent context decide

---

## Best Practices

### 1. Clear Trigger Phrases
- Use natural language users would say
- Include multiple variations
- Avoid technical jargon in triggers

### 2. Comprehensive Examples
- Show 5-8 realistic usage scenarios
- Include both success and error cases
- Demonstrate integration with other agents

### 3. Minimal Tool Access
- Grant only required tools
- Use scoped Bash when possible
- Avoid overly permissive access

### 4. Detailed Error Handling
- Document common errors
- Provide actionable solutions
- Include troubleshooting steps

### 5. Version Management
- Use semantic versioning (major.minor.patch)
- Document breaking changes
- Maintain version history

### 6. Model Selection
- **Haiku**: Fast operations, simple logic, API calls
- **Sonnet**: Complex reasoning, multi-step planning
- **Inherit**: Let parent agent decide

---

## File Organization

```
.claude/agents/
├── README.md                      # This file
├── TEMPLATE.md                    # Template for new agents
├── spec-creator-agent.md          # Spec creation
├── autonomous-builder-agent.md    # Build execution
├── qa-loop-agent.md              # QA validation
├── archon-sync-agent.md          # Archon integration
└── session-analytics-agent.md    # Session analytics
```

---

## Technical Architecture

### Agent Lifecycle

```
1. User Input
   ↓
2. Claude analyzes (description + triggers)
   ↓
3. Delegate to sub-agent (if match found)
   ↓
4. Agent reads context (spec, plan, etc.)
   ↓
5. Agent executes workflow (CLI + tools)
   ↓
6. Agent reports results
   ↓
7. Claude summarizes for user
```

### Communication Flow

```
User ←→ Claude (main agent)
          ↓
    Sub-Agent (specialized)
          ↓
    CLI Tool (spec_runner.py, run.py, etc.)
          ↓
    File System (.auto-claude/, .worktrees/, etc.)
```

### State Management

Sub-agents are **stateless** between invocations:
- Read state from files (spec.md, implementation_plan.json, etc.)
- Execute operations
- Write results to files
- Report to user

No persistent memory across sessions (except through files).

---

## Testing Sub-Agents

See `.claude/docs/sub-agent-test-validation.md` for comprehensive test cases.

**Quick Test:**
```
1. Say trigger phrase
2. Verify agent activates
3. Check command execution
4. Validate output
```

**Integration Test:**
```
1. Create spec (spec-creator-agent)
2. Build spec (autonomous-builder-agent)
3. Validate (qa-loop-agent)
4. Sync (archon-sync-agent)
5. Analyze (session-analytics-agent)
```

---

## FAQ

### Q: When should I create a new sub-agent?

**A:** Create a sub-agent when:
- You have a CLI tool that needs a conversational interface
- The workflow involves multiple steps that need orchestration
- Users would benefit from natural language instead of commands
- The task is complex enough to warrant dedicated logic

### Q: Can sub-agents call other sub-agents?

**A:** Yes, indirectly:
- Sub-agents can suggest user invoke another agent
- Example: "Now that the build is complete, you can run QA validation"
- Claude (parent agent) handles delegation between sub-agents

### Q: How do I update an existing sub-agent?

**A:** Update process:
1. Increment version number (following semver)
2. Update frontmatter if triggers/tools change
3. Update workflow/examples in content
4. Document changes in Version History section
5. Test with trigger phrases

### Q: What if multiple agents match the same trigger?

**A:** Claude decides based on:
1. Description specificity
2. Conversational context
3. User's explicit intent
4. Most recently used agent

### Q: Can I disable a sub-agent?

**A:** Yes:
1. Rename file (add `.disabled` extension)
2. Remove from this README
3. Update related skill documentation

---

## Related Documentation

- **Skills**: `.claude/skills/*/README.md` - Skill documentation
- **Hooks**: `.claude/hooks/README.md` - Lifecycle hooks
- **Development Guide**: `.claude/docs/sub-agent-development-guide.md`
- **Test Guide**: `.claude/docs/sub-agent-test-validation.md`
- **Main Docs**: `CLAUDE.md` - Project overview

---

## Contributing

When adding new sub-agents:

1. **Follow template structure** - Use TEMPLATE.md as base
2. **Add comprehensive examples** - Show real-world usage
3. **Document triggers clearly** - Natural language phrases
4. **Test thoroughly** - Verify triggers and workflows
5. **Update this README** - Add to Available Sub-Agents section
6. **Update skills** - Link from relevant skill documentation

---

## Version History

### v1.0.0 (2026-01-13)
- Initial sub-agent system release
- 5 core agents: spec-creator, autonomous-builder, qa-loop, archon-sync, session-analytics
- TEMPLATE.md for creating new agents
- Integration with skills system
- Comprehensive documentation and test guide

---

## License

Part of Auto-Claude autonomous coding framework.

# Sub-Agent Quick Reference

Quick reference for Auto-Claude sub-agent patterns.

## Agent Definition Template

```yaml
---
name: agent-name              # kebab-case identifier
version: 1.0.0                # semantic version
description: "Clear description with keywords for triggering"
tools: [Read, Grep, Glob]     # tool permissions
model: sonnet                 # sonnet|opus|haiku|inherit
triggers:                     # optional explicit triggers
  - keyword: example
---

# Agent Name

Instructions and workflow...
```

## Tool Permission Patterns

```yaml
# Read-only analysis
tools: [Read, Grep, Glob]

# File modifications
tools: [Read, Edit, Write, Grep, Glob]

# Full implementation
tools: [Read, Edit, Write, Bash, Grep, Glob]

# Scoped bash (git only)
tools: [Bash(git:*), Read]

# Scoped bash (multiple patterns)
tools: [Bash(git:*,npm:*), Read]

# MCP integration
tools: [Read, mcp__archon__*]

# E2E testing
tools: [Read, Bash(git:*), mcp__electron__*]
```

## Model Selection

```yaml
model: sonnet   # Balanced (default) - most tasks
model: opus     # Complex reasoning - rare, high-value
model: haiku    # Fast & efficient - simple operations
model: inherit  # Parent's model - for subagents
```

## CLI Wrapping Pattern

```markdown
## Workflow

Execute the CLI:

```bash
cd apps/backend && python script.py --arg value
```

The process:
1. Step 1 description
2. Step 2 description
3. Step 3 description
```

## Trigger Pattern Examples

```yaml
# Implicit (description)
description: "Creates specs. Use when user wants to define features."

# Explicit (optional)
triggers:
  - keyword: authentication
  - keyword: auth
  - file_pattern: "**/auth/**"
```

## Agent Structure Checklist

- [ ] Frontmatter complete (name, version, description, tools)
- [ ] Model selection appropriate
- [ ] Clear role definition
- [ ] CLI commands documented
- [ ] Workflow steps listed
- [ ] Key responsibilities outlined
- [ ] Usage examples included
- [ ] Error handling documented
- [ ] Integration notes added
- [ ] Tips and best practices
- [ ] Version history started

## Common Sections

1. **Agent Name** - Title and overview
2. **Your Role** - Detailed responsibilities
3. **Workflow** - Step-by-step process with CLI commands
4. **Key Responsibilities** - Bullet list of duties
5. **Integration** - How agent fits in system
6. **Usage Examples** - Real-world scenarios
7. **Error Handling** - Common errors and solutions
8. **Tips** - Best practices
9. **Next Steps** - Post-execution guidance

## File Locations

```
.claude/
├── agents/                   # Agent definitions
│   ├── TEMPLATE.md          # Template for new agents
│   ├── spec-creator-agent.md
│   ├── autonomous-builder-agent.md
│   ├── qa-loop-agent.md
│   ├── archon-sync-agent.md
│   └── session-analytics-agent.md
├── docs/                     # Documentation
│   ├── README.md
│   ├── sub-agent-development-guide.md
│   ├── sub-agent-research-findings.md
│   └── quick-reference.md (this file)
└── skills/                   # Skill definitions
    └── {skill-name}/
        └── SKILL.md
```

## Creating a New Agent

```bash
# 1. Copy template
cp .claude/agents/TEMPLATE.md .claude/agents/my-agent.md

# 2. Edit frontmatter (name, version, description, tools, model)

# 3. Write instructions (role, workflow, responsibilities)

# 4. Add examples and tips

# 5. Test with user requests

# 6. Document integration

# 7. Add to project docs
```

## Testing Checklist

- [ ] Natural language invocation works
- [ ] CLI wrapping executes correctly
- [ ] Tool permissions are appropriate
- [ ] Error handling works
- [ ] Output is user-friendly
- [ ] Integration with skills tested
- [ ] Edge cases handled
- [ ] Documentation is clear

## Auto-Claude Agents Reference

| Agent | CLI Tool | Tools | Model |
|-------|----------|-------|-------|
| spec-creator | spec_runner.py | Full + Web | sonnet |
| autonomous-builder | run.py | Full | sonnet |
| qa-loop | QA system | Full | sonnet |
| archon-sync | Archon MCP | Read + MCP | haiku |
| session-analytics | SFA tools | Read + Bash + MCP | haiku |

## Best Practices

1. **One Agent, One Tool** - Single responsibility
2. **Minimum Permissions** - Only required tools
3. **Clear Triggers** - Specific descriptions
4. **User Guidance** - Always show next steps
5. **Error Handling** - Anticipate common issues
6. **Examples** - Real-world usage scenarios
7. **Integration** - Document relationships
8. **Version Control** - Track changes with semver

## Common Patterns

**Analysis Agent:**
```yaml
tools: [Read, Grep, Glob]
model: haiku
```

**Implementation Agent:**
```yaml
tools: [Read, Edit, Write, Bash, Grep, Glob]
model: sonnet
```

**Integration Agent:**
```yaml
tools: [Read, mcp__service__*]
model: haiku
```

**QA/Testing Agent:**
```yaml
tools: [Read, Bash(git:*), mcp__electron__*]
model: sonnet
```

## Resources

- **Full Guide:** [sub-agent-development-guide.md](./sub-agent-development-guide.md)
- **Template:** [TEMPLATE.md](../agents/TEMPLATE.md)
- **Research:** [sub-agent-research-findings.md](./sub-agent-research-findings.md)
- **Examples:** `.claude/agents/*.md`

# Auto-Claude Documentation

This directory contains comprehensive documentation for Auto-Claude's sub-agent system and development patterns.

## Available Documentation

### Sub-Agent Development

1. **[Sub-Agent Development Guide](./sub-agent-development-guide.md)**
   - Complete guide to creating and managing sub-agents
   - CLI wrapping patterns
   - Tool permissions
   - Trigger patterns
   - Integration with skills
   - Best practices and examples

2. **[Sub-Agent Template](../.claude/agents/TEMPLATE.md)**
   - Ready-to-use template for new agents
   - Complete YAML frontmatter schema
   - All required sections with inline documentation
   - Usage examples and patterns

3. **[Research Findings](./sub-agent-research-findings.md)**
   - IndyDev Template pattern analysis
   - Key findings and insights
   - Implementation recommendations
   - Success metrics and next steps

## Quick Start: Creating a Sub-Agent

1. **Copy the template:**
   ```bash
   cp .claude/agents/TEMPLATE.md .claude/agents/my-new-agent.md
   ```

2. **Update frontmatter:**
   - Set `name`, `version`, `description`
   - Define `tools` permissions
   - Choose `model` (sonnet/opus/haiku)
   - Add `triggers` if needed

3. **Write agent instructions:**
   - Define agent's role
   - Document workflow and CLI commands
   - List responsibilities
   - Add examples and tips

4. **Test with user requests:**
   - Test natural language invocation
   - Verify CLI wrapping works
   - Check tool permissions
   - Validate error handling

5. **Document integration:**
   - Note related agents and skills
   - Add to project documentation
   - Update contributor guides

## Sub-Agent Pattern Overview

**Structure:** Markdown files with YAML frontmatter

**Location:** `.claude/agents/*.md`

**Core Principle:** Sub-agents wrap CLI tools for natural language UX

**Key Components:**
- **Frontmatter** - Configuration (name, tools, model, triggers)
- **Instructions** - System prompt in Markdown
- **CLI Wrapping** - Execute existing command-line tools
- **Tool Permissions** - Declarative security
- **Trigger Patterns** - Natural language selection

## Auto-Claude Sub-Agents

| Agent | Purpose | Wraps | Model |
|-------|---------|-------|-------|
| spec-creator-agent | Create feature specs | spec_runner.py | sonnet |
| autonomous-builder-agent | Execute builds | run.py | sonnet |
| qa-loop-agent | Validate & fix | QA system | sonnet |
| archon-sync-agent | Sync with Archon | Archon MCP | haiku |
| session-analytics-agent | Analyze sessions | SFA tools | haiku |

## Integration with Skills

Skills (`.claude/skills/`) invoke agents through natural language:

```
auto-claude-spec skill → spec-creator-agent → spec_runner.py
auto-claude-build skill → autonomous-builder-agent → run.py
```

Skills provide high-level workflows, agents provide focused execution.

## Best Practices

1. **Single Responsibility** - One agent, one CLI tool
2. **Minimum Permissions** - Only required tools
3. **Clear Documentation** - Examples, tips, troubleshooting
4. **User Guidance** - Next steps, error handling
5. **Version Control** - Semantic versioning

## Resources

- **Claude Code Docs:** https://code.claude.com/docs/
- **Archon Knowledge Base:** Search for "IndyDev Template" and "sub-agent"
- **Auto-Claude CLAUDE.md:** Project instructions and architecture
- **Existing Agents:** `.claude/agents/*.md` for working examples

## Contributing

When creating new sub-agents:
1. Follow the template structure
2. Document thoroughly
3. Test with real user requests
4. Add to this documentation
5. Submit PR with examples

## Next Steps

**Immediate:**
- Test all agents with real user requests
- Refine based on testing
- Update CLAUDE.md and README.md

**Future:**
- Hooks system (lifecycle automation)
- Slash commands (quick workflows)
- Advanced coordination patterns

---

For questions or contributions, see the main [Auto-Claude README](../../README.md).

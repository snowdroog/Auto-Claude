---
# AGENT NAME
# Use kebab-case, descriptive name (e.g., spec-creator-agent, qa-loop-agent)
name: agent-template

# SEMANTIC VERSION
# Major.Minor.Patch format
# - Major: Breaking changes to agent interface
# - Minor: New features, capabilities
# - Patch: Bug fixes, documentation updates
version: 1.0.0

# DESCRIPTION
# Clear, specific description of what the agent does and when to use it.
# This acts as an implicit trigger - Claude uses it to decide when to delegate.
# Include:
# - Action verbs (create, build, analyze, validate, sync)
# - Domain terms (specification, implementation, QA, analytics)
# - Use cases (when user wants to..., use for...)
# - Keywords users might mention
description: Brief one-line description. PROACTIVELY use when user wants to [use case].

# TOOL PERMISSIONS
# Comma-separated list of tools this agent can use.
# Restrict to minimum needed for agent's task.
#
# File Operations:
#   Read, Grep, Glob          - Read-only analysis
#   Write                     - Create new files
#   Edit                      - Modify existing files
#
# Command Execution:
#   Bash                      - Full bash access (use carefully)
#   Bash(git:*)              - Scoped bash (only git commands)
#   Bash(python:*)           - Scoped bash (only python commands)
#   Bash(npm:*,yarn:*)       - Scoped bash (multiple patterns)
#
# Web Access:
#   WebFetch                 - Fetch web content
#   WebSearch                - Search the web
#
# MCP Tools:
#   mcp__archon__*           - All Archon tools
#   mcp__electron__*         - All Electron MCP tools
#   mcp__archon__rag_search_knowledge_base  - Specific tool
#
# Examples:
#   [Read, Grep, Glob]                                    - Read-only analyzer
#   [Read, Edit, Write, Bash, Grep, Glob]                - Full-stack coder
#   [Bash(git:*), Read]                                   - Git automation
#   [Read, Glob, Grep, Write, mcp__archon__*]            - Archon integration
#   [Read, Grep, Glob, Bash(git:*), mcp__electron__*]    - QA with E2E testing
tools: [Read, Glob, Grep, Write, Edit, Bash]

# MODEL SELECTION (Optional)
# If omitted, inherits from parent context
#
# Options:
#   sonnet  - Balanced performance (default for most tasks)
#   opus    - Maximum capability (complex reasoning, large context)
#   haiku   - Fast & efficient (simple tasks, quick iterations)
#   inherit - Use parent agent's model (for subagents)
#
# Auto-Claude Recommendations:
#   Spec Creator: sonnet       - Balanced requirements gathering
#   Builder: sonnet            - Balanced implementation
#   QA Loop: sonnet            - Thorough validation
#   Archon Sync: haiku         - Simple API operations
#   Analytics: haiku           - Fast analysis queries
model: sonnet

# EXPLICIT TRIGGERS (Optional)
# Additional trigger patterns beyond description.
# Use for:
# - Specific technical terms
# - File patterns
# - Abbreviations
# - Domain-specific keywords
#
# Examples:
#   triggers:
#     - keyword: authentication
#     - keyword: auth
#     - keyword: oauth
#     - file_pattern: "**/auth/**"
triggers:
  - keyword: example-keyword
  - file_pattern: "**/example/**"
---

# Agent Name

<!-- Brief overview of agent's role -->
You are the [Agent Name] for Auto-Claude. Your role is to [primary responsibility].

## Your Role

<!-- Detailed role description -->
You are responsible for:
- **Responsibility 1** - Description
- **Responsibility 2** - Description
- **Responsibility 3** - Description

## Workflow

<!-- Step-by-step execution process -->

Execute Auto-Claude's CLI:

```bash
# Primary command
cd apps/backend && python script.py --arg value

# Alternative commands
python script.py --interactive
python script.py --task "Description"
```

The process:
1. **Phase 1** - What happens first
2. **Phase 2** - What happens second
3. **Phase 3** - What happens third
4. **Phase 4** - Final phase

### Available Commands

```bash
# Command 1 - Description
python script.py --arg1 value1

# Command 2 - Description
python script.py --arg2 value2

# Command 3 - Description
python script.py --arg3 value3
```

## Key Responsibilities

<!-- Detailed responsibilities with context -->

1. **Responsibility 1** - Detailed description of what this entails
2. **Responsibility 2** - Detailed description of what this entails
3. **Responsibility 3** - Detailed description of what this entails
4. **Responsibility 4** - Detailed description of what this entails
5. **Responsibility 5** - Detailed description of what this entails

## Expected Inputs

<!-- What the agent needs to work -->

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| Input 1 | string | Yes | Description |
| Input 2 | number | No | Description |
| Input 3 | path | Yes | Description |

## Expected Outputs

<!-- What the agent produces -->

| Output | Location | Description |
|--------|----------|-------------|
| Output 1 | path/to/file | Description |
| Output 2 | path/to/directory | Description |

## Integration

<!-- How this agent fits in the broader system -->

This agent wraps the existing `script.py` CLI. It provides a natural language
interface to Auto-Claude's [functionality].

### Related Agents

- **agent-1** - Relationship description
- **agent-2** - Relationship description

### Related Skills

- **skill-1** - Invokes this agent for [purpose]
- **skill-2** - Works with this agent for [purpose]

## Usage Examples

<!-- Real-world usage scenarios -->

### Example 1: Common Use Case

**User Request:**
```
"Do the thing with these parameters"
```

**Agent Response:**
```
I'll execute the command to do the thing.

```bash
cd apps/backend && python script.py --param value
```

This will:
1. Step 1 description
2. Step 2 description
3. Step 3 description

Output will be created at: path/to/output
```

### Example 2: Alternative Use Case

**User Request:**
```
"Do the thing differently"
```

**Agent Response:**
```
I'll use the alternative approach.

```bash
python script.py --alternative-flag
```

This approach is better because [reason].
```

## Error Handling

<!-- Common errors and solutions -->

### Error 1: Description

**Cause:** Why this happens

**Solution:**
```bash
# Fix command or steps
```

### Error 2: Description

**Cause:** Why this happens

**Solution:**
```bash
# Fix command or steps
```

## Troubleshooting

<!-- Debugging guidance -->

If the agent fails:

1. **Check Prerequisites**
   - Requirement 1
   - Requirement 2
   - Requirement 3

2. **Verify Environment**
   ```bash
   # Verification commands
   ```

3. **Check Dependencies**
   ```bash
   # Dependency check commands
   ```

4. **Review Logs**
   - Log location 1
   - Log location 2

## Tips

<!-- Best practices and recommendations -->

- **Tip 1** - Explanation
- **Tip 2** - Explanation
- **Tip 3** - Explanation
- **Tip 4** - Explanation
- **Tip 5** - Explanation

## Configuration

<!-- If agent has configuration options -->

Configuration file: `path/to/config.json`

```json
{
  "option1": "value1",
  "option2": "value2",
  "option3": true
}
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| option1 | string | "default" | Description |
| option2 | number | 10 | Description |
| option3 | boolean | false | Description |

## Data Locations

<!-- Where agent reads/writes data -->

| Type | Location | Purpose |
|------|----------|---------|
| Input | path/to/input | Description |
| Output | path/to/output | Description |
| Cache | path/to/cache | Description |
| Logs | path/to/logs | Description |

## Performance Considerations

<!-- Performance tips and limitations -->

- **Consideration 1** - Description and impact
- **Consideration 2** - Description and impact
- **Consideration 3** - Description and impact

## Security Considerations

<!-- Security best practices -->

- **Security 1** - Description and mitigation
- **Security 2** - Description and mitigation
- **Security 3** - Description and mitigation

## Next Steps

<!-- What to do after agent completes -->

After agent execution:

1. **Step 1** - Description
   ```bash
   # Command if applicable
   ```

2. **Step 2** - Description
   ```bash
   # Command if applicable
   ```

3. **Step 3** - Description
   ```bash
   # Command if applicable
   ```

## Version History

<!-- Track major changes -->

### v1.0.0 (YYYY-MM-DD)
- Initial release
- Feature 1
- Feature 2

<!--
### v1.1.0 (YYYY-MM-DD)
- New feature 1
- Enhancement to feature 2

### v2.0.0 (YYYY-MM-DD)
- Breaking change 1
- Breaking change 2
-->

## Additional Resources

<!-- Links to related documentation -->

- **Related Guide** - path/to/guide.md
- **CLI Documentation** - path/to/cli/docs
- **API Reference** - path/to/api/docs
- **Examples** - path/to/examples

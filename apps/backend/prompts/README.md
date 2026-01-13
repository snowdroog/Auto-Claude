# Auto-Claude Prompt System Documentation

This document describes the modernized prompt system for Auto-Claude agents. All prompts follow a standardized structure using YAML frontmatter and XML sections for machine-parseability, clarity, and maintainability.

---

## Table of Contents

- [Overview](#overview)
- [Prompt Structure](#prompt-structure)
- [Agent Catalog](#agent-catalog)
- [Creating New Prompts](#creating-new-prompts)
- [Migrating Existing Prompts](#migrating-existing-prompts)
- [Best Practices](#best-practices)
- [Rationale](#rationale)
- [Template Reference](#template-reference)

---

## Overview

Auto-Claude uses a standardized prompt system across all agents. Each agent prompt is a single Markdown file containing:

1. **YAML Frontmatter** - Machine-readable metadata (version, agent type, capabilities, dependencies)
2. **XML Sections** - Structured content (purpose, instructions, tools, examples, recovery procedures)
3. **Markdown Content** - Human-readable documentation

This structure provides:
- **Machine-parseability**: Programmatic access to agent metadata and capabilities
- **Clarity**: Structured sections make prompts easy to navigate
- **Maintainability**: Consistent format simplifies updates and reviews
- **Self-documentation**: Prompts serve as both instructions and reference docs

---

## Prompt Structure

### YAML Frontmatter Schema

Every prompt begins with YAML frontmatter between `---` markers:

```yaml
---
# Core metadata
version: "2.0.0"                    # Semantic version (MAJOR.MINOR.PATCH)
agent_type: "coder"                 # Agent identifier
description: "Brief description"    # One-line summary
model: "claude-sonnet-4-5"          # Target model
thinking_budget: 16000              # Extended thinking token limit
session_type: "multi"               # "single" or "multi" session
last_updated: "2026-01-12"          # ISO date

# Tool configuration
required_tools:                     # Tools that MUST be available
  - Read
  - Write
  - Bash

optional_tools:                     # Tools that enhance functionality
  - WebFetch
  - WebSearch

# MCP server configuration
required_mcp_servers:               # MCP servers that MUST be configured
  - context7

optional_mcp_servers:               # MCP servers that enhance functionality
  - puppeteer
  - electron

# Security and permissions
tool_permissions:
  can_modify_files: true
  can_commit: true
  can_push: false                   # User controls when to push
  can_modify_git_config: false      # NEVER modify git user config
  can_spawn_subagents: true
  can_install_packages: false       # Use existing dependencies

# Agent workflow
agent_dependencies:
  requires_before: ["planner"]      # Agents that must run before this one
  requires_after: ["qa_reviewer"]   # Agents that run after this one

# Quality control
quality_gates:
  self_critique: true               # Run self-critique before completion
  verification: true                # Run verification before marking complete
  test_execution: false             # Run tests as part of this agent
---
```

#### Required Frontmatter Fields

All prompts MUST include:
- `version` - Semantic version number
- `agent_type` - Unique identifier for the agent
- `description` - Brief summary of agent purpose
- `model` - Target Claude model
- `last_updated` - ISO date of last modification

#### Optional Frontmatter Fields

Context-specific fields:
- `thinking_budget` - Extended thinking token limit (default: varies by agent)
- `session_type` - "single" (one session) or "multi" (multiple sessions)
- `required_tools` - Core tools needed for agent operation
- `optional_tools` - Tools that enhance but aren't required
- `required_mcp_servers` - MCP servers that must be available
- `optional_mcp_servers` - MCP servers that enhance functionality
- `tool_permissions` - What this agent can/cannot do
- `agent_dependencies` - Workflow ordering requirements
- `quality_gates` - Quality control checkpoints
- `capabilities` - List of agent capabilities (for spec agents)
- `contract` - Input/output contract (for spec agents)
- `templates` - Template files used by this agent

### XML Sections

Prompts use XML tags to structure content into logical sections:

#### Core Sections

```markdown
<purpose>
## YOUR ROLE
Brief description of the agent's role and key principles.
</purpose>

<instructions>
## PHASE-BY-PHASE EXECUTION

Detailed step-by-step instructions organized into phases.
</instructions>

<tools>
## TOOL USAGE GUIDE
When and how to use each available tool.
</tools>

<examples>
## EXAMPLES
Working examples of common scenarios.
</examples>

<recovery_procedures>
## RECOVERY PROCEDURES
How to handle errors and retry scenarios.
</recovery_procedures>
```

#### Metadata Sections

```markdown
<metadata>
  <agent_info>
    <name>Agent Name</name>
    <role>Brief role description</role>
    <scope>What it does and doesn't do</scope>
  </agent_info>

  <capabilities>
    <can_do>
      - Capability 1
      - Capability 2
    </can_do>
    <cannot_do>
      - Limitation 1
      - Limitation 2
    </cannot_do>
  </capabilities>
</metadata>
```

#### Nested Sections

Sections can be nested for organization:

```markdown
<phase id="0" name="Load Context" mandatory="true">
Instructions for this phase...
</phase>

<phase id="1" name="Analysis">
Instructions for this phase...
</phase>
```

#### Section Attributes

XML tags support attributes for metadata:
- `id` - Unique identifier
- `name` - Human-readable name
- `mandatory` - Whether phase is required
- `conditional` - Condition for including this section

---

## Agent Catalog

### Implementation Agents

| Agent | File | Purpose |
|-------|------|---------|
| **Planner** | `planner.md` | Creates subtask-based implementation plans (Session 1) |
| **Coder** | `coder.md` | Implements subtasks from the plan (Sessions 2-N) |
| **QA Reviewer** | `qa_reviewer.md` | Validates implementation completeness and quality |
| **QA Fixer** | `qa_fixer.md` | Resolves issues found by QA Reviewer |

### Spec Creation Agents

| Agent | File | Purpose |
|-------|------|---------|
| **Spec Gatherer** | `spec_gatherer.md` | Interactive requirements discovery (Phase 1) |
| **Spec Writer** | `spec_writer.md` | Non-interactive spec.md generation (Phase 5) |
| **Spec Researcher** | `spec_researcher.md` | External API/library research (Phase 3) |
| **Spec Critic** | `spec_critic.md` | Ultrathink self-critique (Phase 7, complex only) |

### Utility Agents

| Agent | File | Purpose |
|-------|------|---------|
| **Complexity Assessor** | `complexity_assessor.md` | Determines spec pipeline complexity |
| **Followup Planner** | `followup_planner.md` | Creates follow-up tasks from completed specs |

### Feature Flags

Some agents exist but may not be in active use:
- `competitor_analysis.md` - Market analysis
- `ideation_*.md` - Various ideation modes
- `roadmap_*.md` - Roadmap planning

---

## Creating New Prompts

### Step 1: Copy the Template

Start with `template.md` as a base:

```bash
cp apps/backend/prompts/template.md apps/backend/prompts/my_agent.md
```

### Step 2: Fill in YAML Frontmatter

Update all metadata fields:

```yaml
---
version: "1.0.0"
agent_type: "my_agent"
description: "My agent does X"
model: "claude-sonnet-4-5"
thinking_budget: 8000
session_type: "single"
last_updated: "2026-01-12"

required_tools:
  - Read
  - Bash

tool_permissions:
  can_modify_files: true
  can_commit: false
---
```

### Step 3: Write the Purpose Section

Clearly state what this agent does:

```markdown
<purpose>
You are the **My Agent** in the Auto-Claude system. Your job is to [clear description].

**Key Principle**: [Core principle in one sentence]

**Input**: [What you receive]
**Output**: [What you produce]
</purpose>
```

### Step 4: Structure Instructions as Phases

Break down the workflow into clear phases:

```markdown
<instructions>
## PHASE 0: LOAD CONTEXT (MANDATORY)

<phase id="0" name="Load Context" mandatory="true">
```bash
# Read inputs
cat input.json
```
</phase>

## PHASE 1: ANALYZE

<phase id="1" name="Analyze">
Detailed instructions...
</phase>

## PHASE N: OUTPUT

<phase id="N" name="Output">
Final output instructions...
</phase>
</instructions>
```

### Step 5: Document Tool Usage

Explain when and how to use each tool:

```markdown
<tools>
## TOOL USAGE GUIDE

### Read Tool
**When to use**: Loading context files
**Best practices**:
- Always read before modifying
- Verify file exists

### Write Tool
**When to use**: Creating new files
**Best practices**:
- Use Write for new files
- Use Edit for existing files
</tools>
```

### Step 6: Add Examples

Provide concrete examples:

```markdown
<examples>
## EXAMPLE 1: Common Scenario

Input:
```json
{"task": "example"}
```

Process:
1. Step 1
2. Step 2

Output:
```json
{"result": "success"}
```
</examples>
```

### Step 7: Include Recovery Procedures

Document error handling:

```markdown
<recovery_procedures>
## RECOVERY PROCEDURES

### If Verification Fails
1. Identify the issue
2. Apply fix
3. Re-verify

### If Context Missing
1. Check input files
2. Request missing data
3. Proceed with available context
</recovery_procedures>
```

### Step 8: Validate

Check your prompt:

```bash
# 1. YAML is valid
python -c "import yaml; yaml.safe_load(open('apps/backend/prompts/my_agent.md').read().split('---')[1])"

# 2. All XML tags are closed
grep -E "<[^/]" apps/backend/prompts/my_agent.md | wc -l
grep -E "</.*>" apps/backend/prompts/my_agent.md | wc -l
# These should match

# 3. Required sections present
grep -E "<purpose>" apps/backend/prompts/my_agent.md
grep -E "<instructions>" apps/backend/prompts/my_agent.md
```

---

## Migrating Existing Prompts

### Step 1: Identify the Prompt

Determine if the prompt is:
- **Standalone helper** → Should be inlined into another agent (see Rationale section)
- **Active agent** → Should be modernized

### Step 2: Add YAML Frontmatter

If the prompt lacks YAML frontmatter, add it at the top:

```yaml
---
version: "2.0.0"
agent_type: "[extract from filename or content]"
description: "[extract from first paragraph]"
model: "claude-sonnet-4-5"
last_updated: "[today's date]"

# Add relevant fields from schema
---
```

### Step 3: Wrap Sections in XML

Identify logical sections and wrap them:

**Before:**
```markdown
## YOUR ROLE

You are the coder agent...

## EXECUTION WORKFLOW

Phase 1: Load Context
...
```

**After:**
```markdown
<purpose>
## YOUR ROLE

You are the coder agent...
</purpose>

<instructions>
## EXECUTION WORKFLOW

<phase id="1" name="Load Context">
...
</phase>
</instructions>
```

### Step 4: Extract Tool Usage

Move tool documentation into `<tools>` section:

```markdown
<tools>
## TOOL USAGE GUIDE

### Read Tool
[Consolidated guidance from throughout prompt]

### Write Tool
[Consolidated guidance from throughout prompt]
</tools>
```

### Step 5: Inline Standalone Helpers

If this prompt references standalone helper prompts (like `coder_recovery.md` or `insight_extractor.md`), inline their content:

**Before (coder.md):**
```markdown
If subtask fails, see coder_recovery.md for recovery procedures.
```

**After (coder.md):**
```markdown
<recovery_procedures>
## RECOVERY PROCEDURES

[Inline full content from coder_recovery.md]
</recovery_procedures>
```

Delete the standalone helper file after inlining.

### Step 6: Update Version History

Add changelog comment at the end:

```markdown
<!--
PROMPT VERSION: 2.0.0
LAST UPDATED: 2026-01-12
CHANGELOG:
- 2.0.0 (2026-01-12): Modernized with YAML frontmatter and XML structure
- 1.0.0 (2025-XX-XX): Original version
-->
```

---

## Best Practices

### Structure

1. **One agent per file** - Don't combine multiple agents
2. **Phases must be sequential** - Number phases 0, 1, 2, etc.
3. **Mandatory phases first** - Critical phases at the beginning
4. **XML tags must close** - Every `<tag>` needs `</tag>`
5. **YAML must be valid** - Test with `yaml.safe_load()`

### Content

6. **Be specific** - Use exact file paths, commands, examples
7. **Be actionable** - Every instruction should be executable
8. **Be complete** - Don't reference external docs that might not exist
9. **Use code blocks** - Show concrete examples with syntax highlighting
10. **Document edge cases** - Explain error conditions and recovery

### Style

11. **Active voice** - "Run the command" not "The command should be run"
12. **Imperative mood** - "Create the file" not "You should create the file"
13. **Clear headers** - Use `##` for major sections, `###` for subsections
14. **Consistent terminology** - Pick one term and stick with it
15. **Bulleted lists for items** - Use `- item` for lists
16. **Numbered lists for steps** - Use `1. step` for sequences

### Quality

17. **Self-contained** - Agent should work without external context
18. **Testable instructions** - Each phase should have verifiable output
19. **Error recovery** - Document what to do when things fail
20. **Tool guidance** - Explain when and why to use each tool

### Maintenance

21. **Version on changes** - Bump version when updating
22. **Date updates** - Update `last_updated` field
23. **Changelog comments** - Document what changed and why
24. **Cross-references** - Update related prompts when changing contracts

---

## Rationale

### Why Standardize Prompts?

**Problem**: Original prompts had inconsistent structure:
- Some used YAML frontmatter, some didn't
- Some were standalone helpers, some were full agents
- No clear structure for navigation
- Hard to parse programmatically

**Solution**: Standardized structure with:
- YAML frontmatter for metadata
- XML sections for logical grouping
- Consistent phase numbering
- Self-contained agents

### Benefits of YAML Frontmatter

1. **Machine-readable metadata** - Orchestrator can query agent capabilities
2. **Tool dependency management** - Know what tools an agent needs
3. **Version tracking** - Track changes over time
4. **Pipeline configuration** - Define agent workflow order
5. **Quality gates** - Specify validation requirements

### Benefits of XML Sections

1. **Logical grouping** - Related content stays together
2. **Easy navigation** - Jump to `<instructions>` or `<tools>`
3. **Conditional content** - Include sections based on context
4. **Nested structure** - Phases can be nested and numbered
5. **Programmatic parsing** - Extract sections for analysis

### Why Inline Standalone Helpers?

**Problem**: Some functionality was split into separate "helper" prompts:
- `coder_recovery.md` - Recovery procedures for coder agent
- `insight_extractor.md` - Memory extraction procedures
- `validation_fixer.md` - Validation error fixing

**Issues**:
- Fragmented context - Agent needs to reference external prompts
- Maintenance burden - Update two files for one agent
- Confusion - Unclear when to use helpers vs main prompt

**Solution**: Inline helpers into main agent prompts:
- `coder_recovery.md` → `<recovery_procedures>` in `coder.md`
- `insight_extractor.md` → Memory sections in relevant agents
- `validation_fixer.md` → Error recovery sections in relevant agents

**Benefits**:
- Self-contained agents - All context in one file
- Easier maintenance - One file to update
- Clearer structure - Recovery is clearly part of the agent
- Better context efficiency - No need to load multiple prompts

### Machine-Parseability

The structured format enables programmatic access:

```python
# Parse prompt metadata
import yaml

with open("apps/backend/prompts/coder.md") as f:
    content = f.read()

# Extract YAML frontmatter
frontmatter = yaml.safe_load(content.split("---")[1])

print(f"Agent: {frontmatter['agent_type']}")
print(f"Version: {frontmatter['version']}")
print(f"Required tools: {frontmatter['required_tools']}")
```

```python
# Extract XML sections
import re

# Get all phases
phases = re.findall(r'<phase id="(\d+)" name="([^"]+)"[^>]*>(.*?)</phase>',
                    content, re.DOTALL)

for phase_id, phase_name, phase_content in phases:
    print(f"Phase {phase_id}: {phase_name}")
```

This enables:
- Dynamic agent selection based on capabilities
- Validation of tool availability
- Automated workflow orchestration
- Quality gate enforcement

---

## Template Reference

### Complete Template Structure

See `template.md` for a complete example with all sections.

### Quick Reference

**Minimal prompt:**
```yaml
---
version: "1.0.0"
agent_type: "my_agent"
description: "Brief description"
model: "claude-sonnet-4-5"
last_updated: "2026-01-12"
---

<purpose>
Role and key principle
</purpose>

<instructions>
## PHASE 0: [Phase Name]

<phase id="0" name="Phase Name">
Instructions
</phase>
</instructions>
```

**Standard agent prompt:**
```yaml
---
version: "2.0.0"
agent_type: "my_agent"
description: "Full agent with all sections"
model: "claude-sonnet-4-5"
thinking_budget: 8000
session_type: "single"
last_updated: "2026-01-12"

required_tools:
  - Read
  - Write
  - Bash

tool_permissions:
  can_modify_files: true
  can_commit: true
  can_push: false
---

<metadata>
  <agent_info>
    <name>Agent Name</name>
    <role>Agent role</role>
    <scope>What it does</scope>
  </agent_info>
</metadata>

<purpose>
## YOUR ROLE
Role description
</purpose>

<instructions>
## PHASES

<phase id="0" name="Phase 0" mandatory="true">
Instructions
</phase>

<phase id="1" name="Phase 1">
Instructions
</phase>
</instructions>

<tools>
## TOOL USAGE
Tool guidance
</tools>

<examples>
## EXAMPLES
Working examples
</examples>

<recovery_procedures>
## RECOVERY
Error handling
</recovery_procedures>

<critical_reminders>
## CRITICAL RULES
Key rules
</critical_reminders>

<!--
PROMPT VERSION: 2.0.0
CHANGELOG:
- 2.0.0: Initial version
-->
```

### Section Priority

**Must Have:**
- YAML frontmatter (version, agent_type, description, model, last_updated)
- `<purpose>` - Agent role
- `<instructions>` - Phase-by-phase steps

**Should Have:**
- `<tools>` - Tool usage guidance
- `<critical_reminders>` - Key rules
- Version changelog comment

**Nice to Have:**
- `<metadata>` - Structured agent info
- `<examples>` - Working examples
- `<recovery_procedures>` - Error handling
- `<patterns>` - Common patterns

**Optional:**
- `<validation>` - Output validation
- `<completion>` - Session completion
- Any domain-specific sections

---

## Examples from Existing Prompts

### Example 1: Spec Gatherer (Simple Discovery Agent)

**YAML Frontmatter:**
```yaml
---
version: "2.0.0"
agent_type: spec_gatherer
description: Requirements Gatherer Agent for Auto-Claude spec creation pipeline. Conducts interactive discovery sessions to understand user requirements and outputs structured requirements.json. First phase of the dynamic spec creation pipeline (simple/standard/complex).
model: claude-sonnet-4-5
thinking_budget: 5000
session_type: single
last_updated: "2026-01-12"

required_tools:
  - Read
  - Write
  - Bash

capabilities:
  - Interactive requirements gathering
  - Workflow type determination
  - Service identification
  - Acceptance criteria elicitation
  - Constraint discovery
  - Structured JSON output

contract:
  input: project_index.json
  output: requirements.json
  required_fields:
    - task_description
    - workflow_type
    - services_involved
    - user_requirements
    - acceptance_criteria
    - constraints
    - created_at
---
```

**Key Features:**
- Clear contract (input/output)
- List of capabilities
- Required fields documented
- Interactive session (single session type)

### Example 2: Coder (Complex Multi-Session Agent)

**YAML Frontmatter:**
```yaml
---
version: "2.0.0"
agent_type: coder
model: claude-sonnet-4-5
thinking_budget: 16000
session_type: multi

required_tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob

optional_tools:
  - WebFetch
  - WebSearch

required_mcp_servers:
  - context7

optional_mcp_servers:
  - puppeteer
  - electron

tool_permissions:
  can_modify_files: true
  can_commit: true
  can_push: false
  can_modify_git_config: false
  can_spawn_subagents: true
  can_install_packages: false

agent_dependencies:
  requires_before: ["planner"]
  requires_after: ["qa_reviewer"]

quality_gates:
  self_critique: true
  verification: true
  test_execution: false
---
```

**Key Features:**
- Extensive tool configuration
- MCP server dependencies
- Security permissions clearly defined
- Agent workflow dependencies
- Quality gates specified
- Higher thinking budget (complex agent)

**Recovery Procedures Inlined:**

The coder.md prompt includes recovery procedures that were previously in `coder_recovery.md`:

```markdown
<recovery_procedures>
## RECOVERY PROCEDURES

### The Recovery Loop
1. Start subtask
2. Check attempt_history.json for this subtask
3. If previous attempts exist:
   a. READ what was tried
   b. READ what failed
   c. Choose DIFFERENT approach
...

### When to Mark as Stuck
A subtask should be marked as stuck if:
- 3+ attempts with different approaches all failed
- Circular fix detected
...
</recovery_procedures>
```

### Example 3: QA Reviewer (Validation Agent)

**Context7 Integration:**

The qa_reviewer.md prompt shows how MCP server integration is documented:

```yaml
required_mcp_servers:
  - context7  # Third-party API/library validation
  - electron  # E2E testing for Electron apps (optional, project-dependent)
```

**Tool Usage Documentation:**

```markdown
<tools>
### Context7 MCP Tools

<tool name="context7">
  <purpose>Validate third-party library/API usage against official documentation</purpose>

  <workflow>
    1. resolve-library-id - Find library in Context7
    2. get-library-docs - Retrieve documentation with topic filter
    3. Compare implementation against docs
    4. Document discrepancies in QA report
  </workflow>

  <when_to_use>
    - Implementation uses external APIs
    - Third-party libraries are imported
    - SDKs are integrated
  </when_to_use>
</tool>
</tools>
```

**Key Features:**
- MCP servers with clear purpose annotations
- Nested XML for tool documentation
- When-to-use guidance
- Workflow steps documented

---

## Versioning

### Version Numbers

Use semantic versioning: `MAJOR.MINOR.PATCH`

- **MAJOR** (X.0.0) - Breaking changes to agent contract or behavior
- **MINOR** (2.X.0) - New features, additional sections, enhanced capabilities
- **PATCH** (2.0.X) - Bug fixes, clarifications, minor improvements

### When to Bump Version

**MAJOR (1.x.x → 2.0.0):**
- Change agent input/output contract
- Remove required sections
- Change phase execution order
- Fundamentally alter agent behavior

**MINOR (2.0.x → 2.1.0):**
- Add new phases
- Add new tool usage patterns
- Enhance capabilities
- Add optional sections

**PATCH (2.0.0 → 2.0.1):**
- Fix typos or formatting
- Clarify existing instructions
- Update examples
- Improve documentation

### Changelog Format

Add version history at the end of the prompt:

```markdown
<!--
PROMPT VERSION: 2.0.1
LAST UPDATED: 2026-01-12
CHANGELOG:
- 2.0.1 (2026-01-12): Fix typo in Phase 3 instructions
- 2.0.0 (2026-01-12): Modernized with YAML frontmatter and XML structure, inlined recovery procedures
- 1.5.0 (2025-12-15): Add Context7 integration for library validation
- 1.0.0 (2025-10-01): Initial version
-->
```

---

## Validation Checklist

Before considering a prompt complete, verify:

### Structure
- [ ] YAML frontmatter is valid (test with `yaml.safe_load()`)
- [ ] All required frontmatter fields present
- [ ] All XML tags are properly closed
- [ ] Phases are numbered sequentially (0, 1, 2, ...)
- [ ] All sections use consistent heading levels

### Content
- [ ] Purpose section clearly states agent role
- [ ] Instructions broken into clear phases
- [ ] Each phase has actionable steps
- [ ] Tool usage documented for all required tools
- [ ] Examples provided for common scenarios
- [ ] Error recovery procedures documented

### Quality
- [ ] No placeholder content (e.g., `[TODO]`, `[FIXME]`)
- [ ] All file paths are specific, not generic
- [ ] Code blocks have syntax highlighting
- [ ] Cross-references are accurate
- [ ] Terminology is consistent throughout

### Compliance
- [ ] Follows best practices from this document
- [ ] Matches template structure
- [ ] Version number updated
- [ ] Changelog comment present
- [ ] Related prompts updated if contract changed

---

## Support and Questions

### Where to Get Help

1. **Reference existing prompts**: Look at modernized prompts for patterns
   - `coder.md` - Complex multi-phase agent with recovery
   - `spec_gatherer.md` - Simple interactive agent
   - `qa_reviewer.md` - Validation agent with MCP integration

2. **Use the template**: Start with `template.md` for new prompts

3. **Check CLAUDE.md**: Project-level guidance for Auto-Claude development

4. **Review this README**: You're already here!

### Common Issues

**Issue**: YAML parsing fails
**Solution**: Validate YAML syntax with `python -c "import yaml; yaml.safe_load(open('prompt.md').read().split('---')[1])"`

**Issue**: XML tags don't match
**Solution**: Count opening and closing tags, ensure they match

**Issue**: Instructions unclear
**Solution**: Add specific examples with code blocks

**Issue**: Agent doesn't work as expected
**Solution**: Check required_tools and tool_permissions in frontmatter

---

## Conclusion

The modernized prompt system provides a consistent, machine-parseable, and maintainable foundation for Auto-Claude agents. By following this guide, you can create clear, effective prompts that work reliably across the autonomous coding pipeline.

**Next Steps:**
1. Review the template: `template.md`
2. Study working examples: `coder.md`, `spec_gatherer.md`, `qa_reviewer.md`
3. Create or migrate prompts following this guide
4. Test your prompts with the orchestrator
5. Update related documentation if you change contracts

**Remember**: Prompts are both instructions and documentation. Write them clearly, structure them consistently, and maintain them carefully.

---

*Last updated: 2026-01-12*
*Documentation version: 1.0.0*

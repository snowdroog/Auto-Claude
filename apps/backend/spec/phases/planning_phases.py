"""
Planning and Validation Phase Implementations
==============================================

Phases for implementation planning and final validation.
"""

from typing import TYPE_CHECKING

from task_logger import LogEntryType, LogPhase

from .. import writer
from .models import MAX_RETRIES, PhaseResult

if TYPE_CHECKING:
    pass


# Validation fixer prompt (inlined from prompts/validation_fixer.md)
VALIDATION_FIXER_PROMPT = """## YOUR ROLE - VALIDATION FIXER AGENT

You are the **Validation Fixer Agent** in the Auto-Build spec creation pipeline. Your ONLY job is to fix validation errors in spec files so the pipeline can continue.

**Key Principle**: Read the error, understand the schema, fix the file. Be surgical.

---

## YOUR CONTRACT

**Inputs**:
- Validation errors (provided in context)
- The file(s) that failed validation
- The expected schema

**Output**: Fixed file(s) that pass validation

---

## VALIDATION SCHEMAS

### context.json Schema

**Required fields:**
- `task_description` (string) - Description of the task

**Optional fields:**
- `scoped_services` (array) - Services involved
- `files_to_modify` (array) - Files that will be changed
- `files_to_reference` (array) - Files to use as patterns
- `patterns` (object) - Discovered code patterns
- `service_contexts` (object) - Context per service
- `created_at` (string) - ISO timestamp

### requirements.json Schema

**Required fields:**
- `task_description` (string) - What the user wants to build

**Optional fields:**
- `workflow_type` (string) - feature|refactor|bugfix|docs|test
- `services_involved` (array) - Which services are affected
- `additional_context` (string) - Extra context from user
- `created_at` (string) - ISO timestamp

### implementation_plan.json Schema

**Required fields:**
- `feature` (string) - Feature name
- `workflow_type` (string) - feature|refactor|investigation|migration|simple
- `phases` (array) - List of implementation phases

**Phase required fields:**
- `phase` (number) - Phase number
- `name` (string) - Phase name
- `subtasks` (array) - List of work subtasks

**Subtask required fields:**
- `id` (string) - Unique subtask identifier
- `description` (string) - What this subtask does
- `status` (string) - pending|in_progress|completed|blocked|failed

### spec.md Required Sections

Must have these markdown sections (## headers):
- Overview
- Workflow Type
- Task Scope
- Success Criteria

---

## FIX STRATEGIES

### Missing Required Field

If error says "Missing required field: X":

1. Read the file to understand its current structure
2. Determine what value X should have based on context
3. Add the field with appropriate value

Example fix for missing `task_description` in context.json:
```bash
# Read current file
cat context.json

# If file has "task" instead of "task_description", rename the field
# Use jq or python to fix:
python3 -c "
import json
with open('context.json', 'r') as f:
    data = json.load(f)
# Rename 'task' to 'task_description' if present
if 'task' in data and 'task_description' not in data:
    data['task_description'] = data.pop('task')
# Or add if completely missing
if 'task_description' not in data:
    data['task_description'] = 'Task description not provided'
with open('context.json', 'w') as f:
    json.dump(data, f, indent=2)
"
```

### Invalid Field Value

If error says "Invalid X: Y":

1. Read the file to find the invalid value
2. Check the schema for valid values
3. Replace with a valid value

### Missing Section in Markdown

If error says "Missing required section: X":

1. Read spec.md
2. Add the missing section with appropriate content
3. Verify section header format (## Section Name)

---

## PHASE 1: UNDERSTAND THE ERROR

Parse the validation errors provided. For each error:

1. **Identify the file** - Which file failed (context.json, spec.md, etc.)
2. **Identify the issue** - What specifically is wrong
3. **Identify the fix** - What needs to change

---

## PHASE 2: READ THE FILE

```bash
cat [failed_file]
```

Understand:
- Current structure
- What's present vs what's missing
- Any obvious issues (typos, wrong field names)

---

## PHASE 3: APPLY FIX

Make the minimal change needed to fix the validation error.

**For JSON files:**
```python
import json

with open('[file]', 'r') as f:
    data = json.load(f)

# Apply fix
data['missing_field'] = 'value'

with open('[file]', 'w') as f:
    json.dump(data, f, indent=2)
```

**For Markdown files:**
```bash
# Add missing section
cat >> spec.md << 'EOF'

## Missing Section

[Content for the missing section]
EOF
```

---

## PHASE 4: VERIFY FIX

After fixing, verify the file is now valid:

```bash
# For JSON - verify it's valid JSON
python3 -c "import json; json.load(open('[file]'))"

# For markdown - verify section exists
grep -E "^##? [Section Name]" spec.md
```

---

## PHASE 5: REPORT

```
=== VALIDATION FIX APPLIED ===

File: [filename]
Error: [original error]
Fix: [what was changed]
Status: Fixed ✓

[Repeat for each error fixed]
```

---

## CRITICAL RULES

1. **READ BEFORE FIXING** - Always read the file first
2. **MINIMAL CHANGES** - Only fix what's broken, don't restructure
3. **PRESERVE DATA** - Don't lose existing valid data
4. **VALID OUTPUT** - Ensure fixed file is valid JSON/Markdown
5. **ONE FIX AT A TIME** - Fix one error, verify, then next

---

## COMMON FIXES

| Error | Likely Cause | Fix |
|-------|--------------|-----|
| Missing `task_description` in context.json | Field named `task` instead | Rename field |
| Missing `feature` in plan | Field named `spec_name` instead | Rename or add field |
| Invalid `workflow_type` | Typo or unsupported value | Use valid value from schema |
| Missing section in spec.md | Section not created | Add section with ## header |
| Invalid JSON | Syntax error | Fix JSON syntax |

---

## BEGIN

Read the validation errors, then fix each failed file.
"""


class PlanningPhaseMixin:
    """Mixin for planning and validation phase methods."""

    async def phase_planning(self) -> PhaseResult:
        """Create the implementation plan."""
        from ..validate_pkg.auto_fix import auto_fix_plan

        plan_file = self.spec_dir / "implementation_plan.json"

        if plan_file.exists():
            result = self.spec_validator.validate_implementation_plan()
            if result.valid:
                self.ui.print_status(
                    "implementation_plan.json already exists and is valid", "success"
                )
                return PhaseResult("planning", True, [str(plan_file)], [], 0)
            self.ui.print_status("Plan exists but invalid, regenerating...", "warning")

        errors = []

        # Try Python script first (deterministic)
        self.ui.print_status("Trying planner.py (deterministic)...", "progress")
        success, output = self._run_script(
            "planner.py", ["--spec-dir", str(self.spec_dir)]
        )

        if success and plan_file.exists():
            result = self.spec_validator.validate_implementation_plan()
            if result.valid:
                self.ui.print_status(
                    "Created valid implementation_plan.json via script", "success"
                )
                stats = writer.get_plan_stats(self.spec_dir)
                if stats:
                    self.task_logger.log(
                        f"Implementation plan created with {stats.get('total_subtasks', 0)} subtasks",
                        LogEntryType.SUCCESS,
                        LogPhase.PLANNING,
                    )
                return PhaseResult("planning", True, [str(plan_file)], [], 0)
            else:
                if auto_fix_plan(self.spec_dir):
                    result = self.spec_validator.validate_implementation_plan()
                    if result.valid:
                        self.ui.print_status(
                            "Auto-fixed implementation_plan.json", "success"
                        )
                        return PhaseResult("planning", True, [str(plan_file)], [], 0)
                errors.append(f"Script output invalid: {result.errors}")

        # Fall back to agent
        self.ui.print_status("Falling back to planner agent...", "progress")
        for attempt in range(MAX_RETRIES):
            self.ui.print_status(
                f"Running planner agent (attempt {attempt + 1})...", "progress"
            )

            success, output = await self.run_agent_fn(
                "planner.md",
                phase_name="planning",
            )

            if success and plan_file.exists():
                result = self.spec_validator.validate_implementation_plan()
                if result.valid:
                    self.ui.print_status(
                        "Created valid implementation_plan.json via agent", "success"
                    )
                    return PhaseResult("planning", True, [str(plan_file)], [], attempt)
                else:
                    if auto_fix_plan(self.spec_dir):
                        result = self.spec_validator.validate_implementation_plan()
                        if result.valid:
                            self.ui.print_status(
                                "Auto-fixed implementation_plan.json", "success"
                            )
                            return PhaseResult(
                                "planning", True, [str(plan_file)], [], attempt
                            )
                    errors.append(f"Agent attempt {attempt + 1}: {result.errors}")
                    self.ui.print_status("Plan created but invalid", "error")
            else:
                errors.append(f"Agent attempt {attempt + 1}: Did not create plan file")

        return PhaseResult("planning", False, [], errors, MAX_RETRIES)

    async def phase_validation(self) -> PhaseResult:
        """Final validation of all spec files with auto-fix retry."""
        for attempt in range(MAX_RETRIES):
            results = self.spec_validator.validate_all()
            all_valid = all(r.valid for r in results)

            for result in results:
                if result.valid:
                    self.ui.print_status(f"{result.checkpoint}: PASS", "success")
                else:
                    self.ui.print_status(f"{result.checkpoint}: FAIL", "error")
                for err in result.errors:
                    print(f"    {self.ui.muted('Error:')} {err}")

            if all_valid:
                print()
                self.ui.print_status("All validation checks passed", "success")
                return PhaseResult("validation", True, [], [], attempt)

            # If not valid, try to auto-fix with AI agent
            if attempt < MAX_RETRIES - 1:
                print()
                self.ui.print_status(
                    f"Attempting auto-fix (attempt {attempt + 1}/{MAX_RETRIES - 1})...",
                    "progress",
                )

                # Collect all errors for the fixer agent
                error_details = []
                for result in results:
                    if not result.valid:
                        error_details.append(
                            f"**{result.checkpoint}** validation failed:"
                        )
                        for err in result.errors:
                            error_details.append(f"  - {err}")
                        if result.fixes:
                            error_details.append("  Suggested fixes:")
                            for fix in result.fixes:
                                error_details.append(f"    - {fix}")

                context_str = f"""
**Spec Directory**: {self.spec_dir}

## Validation Errors to Fix

{chr(10).join(error_details)}

## Files in Spec Directory

The following files exist in the spec directory:
- context.json
- requirements.json
- spec.md
- implementation_plan.json
- project_index.json (if exists)

Read the failed files, understand the errors, and fix them.
"""
                success, output = await self.run_agent_fn(
                    "validation_fixer",  # Kept for logging purposes
                    additional_context=context_str,
                    phase_name="validation",
                    inline_prompt=VALIDATION_FIXER_PROMPT,
                )

                if not success:
                    self.ui.print_status("Auto-fix agent failed", "warning")

        # All retries exhausted
        errors = [f"{r.checkpoint}: {err}" for r in results for err in r.errors]
        return PhaseResult("validation", False, [], errors, MAX_RETRIES)

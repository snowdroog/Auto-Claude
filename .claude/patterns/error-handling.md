# Error Handling Pattern

Auto-Claude's approach to graceful error handling, recovery, and user guidance.

## Pattern Overview

```
Error Occurs → Detect → Log → Recover → Guide User → Learn
```

## Error Categories

### 1. Recoverable Errors

Errors the agent can fix automatically.

**Examples:**
- Missing dependencies → Install them
- File not found → Create it
- Syntax error → Fix it
- Test failure → Debug and fix

**Response Pattern:**
```
1. Detect error
2. Log to appropriate channel
3. Attempt automatic fix
4. Verify fix worked
5. Continue execution
```

### 2. Actionable Errors

Errors requiring user intervention but with clear fix.

**Examples:**
- Missing API key → Prompt user to add it
- Permission denied → Guide user to grant access
- Port already in use → Suggest alternative port
- Git conflict → Provide resolution steps

**Response Pattern:**
```
1. Detect error
2. Log with context
3. Explain the problem clearly
4. Provide step-by-step fix
5. Wait for user action
6. Verify resolution
```

### 3. Fatal Errors

Errors that require stopping execution.

**Examples:**
- Critical dependency missing
- File system full
- Network timeout (persistent)
- Corrupted data

**Response Pattern:**
```
1. Detect error
2. Log full context
3. Explain what happened
4. Explain why we must stop
5. Suggest recovery path
6. Exit gracefully
```

## Error Detection

### Early Detection

Catch errors before they cause damage:

```python
# Preflight checks in spec_runner.py
def validate_environment():
    """Run before starting spec creation."""
    checks = [
        check_python_version(),
        check_required_tools(),
        check_api_keys(),
        check_disk_space(),
        check_git_status()
    ]

    for check in checks:
        if not check.passed:
            raise PreflightError(check.message, check.fix_steps)
```

### Contextual Detection

Capture context when error occurs:

```python
try:
    result = execute_command(cmd)
except CommandError as e:
    error_context = {
        "command": cmd,
        "cwd": os.getcwd(),
        "env": relevant_env_vars(),
        "spec_id": current_spec_id,
        "phase": current_phase,
        "timestamp": datetime.now(),
        "stack_trace": traceback.format_exc()
    }
    log_error(e, context=error_context)
    handle_command_error(e, error_context)
```

## Error Logging

### Log Levels

| Level | Use Case | Example |
|-------|----------|---------|
| DEBUG | Verbose info for troubleshooting | `Checking file: config.json` |
| INFO | Normal operations | `Starting spec creation for: auth` |
| WARNING | Potential issues | `Using cached dependency, may be stale` |
| ERROR | Errors but execution continues | `Test failed, attempting retry` |
| CRITICAL | Fatal errors, execution stops | `Cannot connect to required service` |

### Log Destinations

**Auto-Claude Logging Strategy:**

```python
# .auto-claude/logs/
├── agent_{session_id}.log         # Agent execution logs
├── hooks.log                       # Hook execution logs
├── errors_{date}.log               # Error-only logs
├── qa_{spec_id}.log                # QA validation logs
└── build_{spec_id}_{timestamp}.log # Build session logs
```

**Hook Logging:**

```python
# .claude/hooks/utils/logging.py
import logging
from pathlib import Path

def get_hook_logger(hook_name: str):
    logger = logging.getLogger(f"hook.{hook_name}")
    handler = logging.FileHandler(".claude/hooks/hooks.log")
    handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    logger.addHandler(handler)
    return logger
```

### Structured Logging

```python
# Log with structured data
logger.error("Command failed", extra={
    "command": cmd,
    "exit_code": result.returncode,
    "stdout": result.stdout[:500],  # Truncate for logs
    "stderr": result.stderr[:500],
    "spec_id": spec_id,
    "recoverable": is_recoverable(result)
})
```

## Recovery Strategies

### Retry with Backoff

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def call_api_with_retry(endpoint):
    """Retry API calls with exponential backoff."""
    response = requests.post(endpoint, ...)
    response.raise_for_status()
    return response.json()
```

### Fallback Strategies

```python
def get_dependencies():
    """Try multiple sources for dependencies."""
    strategies = [
        lambda: install_from_pypi(),
        lambda: install_from_cache(),
        lambda: install_from_vendored()
    ]

    for strategy in strategies:
        try:
            return strategy()
        except Exception as e:
            logger.warning(f"Strategy failed: {strategy.__name__}, {e}")
            continue

    raise DependencyError("All dependency strategies failed")
```

### Graceful Degradation

```python
def analyze_with_telemetry():
    """Analysis with optional telemetry."""
    results = run_analysis()

    try:
        send_to_telemetry(results)
    except TelemetryError:
        logger.warning("Telemetry unavailable, continuing without it")
        # Analysis still completes successfully

    return results
```

## User Guidance

### Error Messages

**Bad Error Message:**
```
Error: Command failed with exit code 1
```

**Good Error Message:**
```
❌ Build Failed: TypeScript Compilation Error

The TypeScript compiler found 3 errors in src/auth/login.ts:

  Line 42: Type 'string | undefined' is not assignable to type 'string'
  Line 58: Property 'username' does not exist on type 'User'
  Line 73: Cannot find module './utils/crypto'

🔧 How to Fix:
1. Add null checks for optional properties (line 42)
2. Use correct property name 'userName' (line 58)
3. Install missing crypto utility: npm install crypto-js

💡 Tip: Run 'npm run type-check' to see all type errors before building.

📄 Build log: .auto-claude/logs/build_001_20260112_143022.log
```

### Recovery Suggestions

**Pattern:**
```
1. What happened (clear description)
2. Why it happened (root cause if known)
3. How to fix it (step-by-step)
4. How to prevent it (optional)
5. Where to get help (links/docs)
```

**Example:**

```markdown
## ⚠️ API Key Missing

**What happened:**
Cannot authenticate with Claude API. The ANTHROPIC_API_KEY environment variable is not set.

**Why this matters:**
Auto-Claude requires Claude API access for spec creation, planning, and QA validation.

**How to fix:**
1. Get your API key from: https://console.anthropic.com/
2. Add it to your environment:
   ```bash
   echo 'export ANTHROPIC_API_KEY="sk-ant-..."' >> ~/.bashrc
   source ~/.bashrc
   ```
3. Or add it to `apps/backend/.env`:
   ```
   ANTHROPIC_API_KEY=sk-ant-...
   ```
4. Restart the session

**Verify it works:**
```bash
python -c "import os; print('✓ API key set' if os.getenv('ANTHROPIC_API_KEY') else '✗ API key missing')"
```

**Need help?** See [Setup Guide](../../README.md#setup)
```

## Error Categories in Auto-Claude

### Build Errors

**Detection Point:** During autonomous build (coder agent)

**Common Errors:**
- Compilation failures
- Import errors
- Type mismatches
- Missing dependencies

**Recovery:**
```
1. coder_recovery.md provides guidance
2. Agent attempts fix (up to 3 tries)
3. If unfixable, escalate to user with context
```

### QA Errors

**Detection Point:** QA validation phase

**Common Errors:**
- Test failures
- Acceptance criteria not met
- Build failures
- Runtime errors

**Recovery:**
```
1. QA reviewer creates detailed QA_FIX_REQUEST.md
2. QA fixer agent addresses issues
3. Re-run QA validation
4. Loop up to max iterations (default: 3)
```

### Integration Errors

**Detection Point:** External service integration

**Common Errors:**
- API rate limits
- Network timeouts
- Authentication failures
- Service unavailable

**Recovery:**
```
1. Retry with exponential backoff
2. Use fallback services if available
3. Cache partial results
4. Gracefully degrade to local-only mode
```

### Spec Creation Errors

**Detection Point:** During spec pipeline

**Common Errors:**
- Unclear requirements
- Missing context
- Invalid spec format
- Research failures

**Recovery:**
```
1. Ask clarifying questions (spec_gatherer)
2. Search alternative sources (spec_researcher)
3. Use spec templates (spec_writer)
4. Fallback to simpler spec format
```

## Integration with Hooks

### PreToolUse Hook

Prevent errors before they occur:

```python
# .claude/hooks/pre_tool_use.py
def validate_tool_use(tool_name, tool_input):
    """Catch dangerous operations early."""

    # Prevent destructive Bash commands
    if tool_name == "Bash":
        command = tool_input.get("command", "")
        if any(dangerous in command for dangerous in ["rm -rf /", "dd if=", "mkfs"]):
            raise SecurityError(f"Dangerous command blocked: {command}")

    # Prevent writing to protected files
    if tool_name == "Write":
        path = tool_input.get("file_path", "")
        if is_protected_file(path):
            raise PermissionError(f"Cannot write to protected file: {path}")

    return True
```

### PostToolUse Hook

Handle errors after tool execution:

```python
# .claude/hooks/post_tool_use.py
def handle_tool_errors(tool_name, tool_result):
    """Process errors from tool execution."""

    if tool_result.get("error"):
        error = tool_result["error"]

        # Log error with context
        log_tool_error(tool_name, error)

        # Extract learnings
        if is_recurring_error(error):
            store_error_pattern(error, resolution=get_past_resolution(error))

        # Suggest fixes
        if error_type == "FileNotFoundError":
            suggest_file_creation(error)
        elif error_type == "ImportError":
            suggest_dependency_install(error)
```

### Stop Hook

Quality gates before completion:

```python
# .claude/hooks/stop.py
def validate_before_stop():
    """Ensure build quality before marking complete."""

    checks = [
        ("Tests pass", run_tests()),
        ("Build succeeds", run_build()),
        ("No critical errors", check_error_log()),
        ("QA approved", check_qa_status())
    ]

    failures = [name for name, passed in checks if not passed]

    if failures:
        raise QualityGateError(
            f"Cannot complete: {', '.join(failures)} failed\n"
            f"See QA report for details: {qa_report_path}"
        )
```

## Learning from Errors

### Pattern Extraction

```python
# .claude/hooks/post_tool_use.py
def extract_error_patterns(errors):
    """Learn from recurring errors."""

    patterns = analyze_error_patterns(errors)

    for pattern in patterns:
        # Store in Graphiti for future builds
        graphiti.add_insight(
            entity_name=f"error_pattern_{pattern.id}",
            content=f"Error: {pattern.description}\n"
                   f"Context: {pattern.context}\n"
                   f"Solution: {pattern.resolution}"
        )

        # Store in Archon for cross-project learning
        archon.add_document(
            project_id=archon_project_id,
            title=f"Error Pattern: {pattern.description}",
            document_type="note",
            content=pattern.to_dict()
        )
```

### Error Analytics

```python
# Single-File Agent for error analysis
# apps/backend/single-file-agents/agents/sfa_error_analyzer.py

def analyze_session_errors(session_id):
    """Generate insights from session errors."""

    errors = load_session_errors(session_id)

    analysis = {
        "total_errors": len(errors),
        "error_types": count_by_type(errors),
        "recoverable": count_recoverable(errors),
        "patterns": detect_patterns(errors),
        "recommendations": generate_recommendations(errors)
    }

    return analysis
```

## Best Practices

1. **Fail Fast**: Detect errors early in the pipeline
2. **Provide Context**: Include what, why, and how to fix
3. **Be Specific**: "Missing ANTHROPIC_API_KEY" not "Configuration error"
4. **Enable Recovery**: Offer automated fixes when possible
5. **Document Patterns**: Store solutions for recurring issues
6. **Test Error Paths**: Ensure error handlers work
7. **Log Strategically**: Debug logs for developers, clear messages for users

## Metrics

**Target Metrics:**
- Error recovery rate: > 70%
- Time to resolution: < 5 minutes
- Recurring errors: < 10% of total
- User-reported errors: < 5% of builds

**Red Flags:**
- Same error recurring (poor pattern learning)
- Long error messages (unclear guidance)
- Silent failures (poor detection)
- Cryptic error codes (user confusion)

## Resources

- [Python Error Handling Best Practices](https://realpython.com/python-exceptions/)
- [Tenacity Retry Library](https://github.com/jd/tenacity)
- Auto-Claude: [coder_recovery.md](../../apps/backend/prompts/coder_recovery.md)
- Pattern: [QA Loop](./qa-loop.md)

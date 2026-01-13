"""Error handling utilities for Auto-Claude hooks."""

import functools
import logging
import time
from pathlib import Path
from typing import Any, Callable, Optional, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class HookError(Exception):
    """Base exception for hook errors."""
    pass


class RecoverableError(HookError):
    """Error that can be automatically recovered from."""
    pass


class FatalError(HookError):
    """Error that requires user intervention."""
    pass


def retry_with_backoff(
    max_attempts: int = 3,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator to retry functions with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts
        backoff_factor: Multiplier for wait time between retries
        exceptions: Tuple of exceptions to catch and retry

    Example:
        @retry_with_backoff(max_attempts=3, exceptions=(ConnectionError,))
        def call_api():
            return requests.get("https://api.example.com")
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            wait_time = 1.0

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        logger.error(
                            f"{func.__name__} failed after {max_attempts} attempts: {e}"
                        )
                        raise

                    logger.warning(
                        f"{func.__name__} attempt {attempt}/{max_attempts} failed: {e}. "
                        f"Retrying in {wait_time:.1f}s..."
                    )
                    time.sleep(wait_time)
                    wait_time *= backoff_factor

        return wrapper
    return decorator


def safe_execute(
    func: Callable[..., T],
    fallback: Optional[T] = None,
    log_errors: bool = True
) -> Optional[T]:
    """
    Safely execute a function, returning fallback on error.

    Args:
        func: Function to execute
        fallback: Value to return on error (default: None)
        log_errors: Whether to log errors (default: True)

    Returns:
        Function result or fallback value

    Example:
        result = safe_execute(
            lambda: json.loads(file.read_text()),
            fallback={},
            log_errors=True
        )
    """
    try:
        return func()
    except Exception as e:
        if log_errors:
            logger.error(f"Error executing {func.__name__}: {e}")
        return fallback


def log_error_with_context(
    error: Exception,
    context: dict[str, Any],
    log_file: Optional[Path] = None
):
    """
    Log error with contextual information.

    Args:
        error: The exception that occurred
        context: Dictionary of contextual information
        log_file: Optional specific log file to write to

    Example:
        try:
            process_spec(spec_id)
        except Exception as e:
            log_error_with_context(e, {
                "spec_id": spec_id,
                "phase": "planning",
                "agent": "planner"
            })
    """
    error_details = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context
    }

    log_message = (
        f"Error occurred: {error_details['error_type']}\n"
        f"Message: {error_details['error_message']}\n"
        f"Context: {error_details['context']}"
    )

    logger.error(log_message)

    if log_file:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        with log_file.open("a") as f:
            f.write(f"\n{'='*80}\n")
            f.write(f"{log_message}\n")


def classify_error(error: Exception) -> str:
    """
    Classify error as recoverable, actionable, or fatal.

    Args:
        error: The exception to classify

    Returns:
        Classification string: "recoverable", "actionable", or "fatal"

    Example:
        error_type = classify_error(FileNotFoundError("config.json"))
        # Returns: "recoverable"
    """
    # Recoverable errors (can fix automatically)
    recoverable_types = (
        FileNotFoundError,
        ModuleNotFoundError,
        ImportError,
    )

    # Actionable errors (need user input but fixable)
    actionable_types = (
        PermissionError,
        ConnectionError,
        TimeoutError,
    )

    # Fatal errors (require stopping execution)
    fatal_types = (
        MemoryError,
        KeyboardInterrupt,
        SystemExit,
    )

    if isinstance(error, recoverable_types):
        return "recoverable"
    elif isinstance(error, actionable_types):
        return "actionable"
    elif isinstance(error, fatal_types):
        return "fatal"
    else:
        # Default to actionable for unknown errors
        return "actionable"


def create_error_report(
    error: Exception,
    context: dict[str, Any],
    spec_dir: Optional[Path] = None
) -> str:
    """
    Create user-friendly error report with recovery suggestions.

    Args:
        error: The exception that occurred
        context: Contextual information about the error
        spec_dir: Optional spec directory to save report

    Returns:
        Formatted error report string

    Example:
        report = create_error_report(
            error=FileNotFoundError("requirements.txt"),
            context={"phase": "build", "spec_id": "001"},
            spec_dir=Path(".auto-claude/specs/001")
        )
    """
    error_type = classify_error(error)
    error_name = type(error).__name__

    report_lines = [
        "# Error Report",
        "",
        f"## Error: {error_name}",
        "",
        f"**Type:** {error_type}",
        f"**Message:** {error}",
        "",
        "## Context",
        ""
    ]

    for key, value in context.items():
        report_lines.append(f"- **{key}:** {value}")

    report_lines.extend([
        "",
        "## Recovery Suggestions",
        ""
    ])

    # Add type-specific recovery suggestions
    if isinstance(error, FileNotFoundError):
        report_lines.extend([
            "The file mentioned above could not be found.",
            "",
            "**How to fix:**",
            f"1. Check if the file path is correct: `{error.filename}`",
            "2. Ensure the file exists in the expected location",
            "3. If it's a generated file, run the generation step first",
            "4. Check file permissions"
        ])
    elif isinstance(error, ModuleNotFoundError):
        module_name = str(error).split("'")[1] if "'" in str(error) else "unknown"
        report_lines.extend([
            f"Python module '{module_name}' is not installed.",
            "",
            "**How to fix:**",
            f"1. Install the module: `uv pip install {module_name}`",
            "2. Or install all requirements: `uv pip install -r requirements.txt`",
            "3. Verify installation: `python -c 'import {module_name}'`"
        ])
    elif isinstance(error, PermissionError):
        report_lines.extend([
            "Permission denied for the requested operation.",
            "",
            "**How to fix:**",
            "1. Check file/directory permissions",
            "2. Ensure you have write access to the project directory",
            "3. Try running with appropriate permissions",
            "4. Check if file is locked by another process"
        ])
    else:
        report_lines.extend([
            "An unexpected error occurred.",
            "",
            "**How to fix:**",
            "1. Review the error message above",
            "2. Check the context information",
            "3. Consult logs for more details",
            "4. If the issue persists, file an issue on GitHub"
        ])

    report = "\n".join(report_lines)

    # Save to spec directory if provided
    if spec_dir:
        spec_dir = Path(spec_dir)
        error_file = spec_dir / "ERROR_REPORT.md"
        error_file.write_text(report)
        logger.info(f"Error report saved to: {error_file}")

    return report


def handle_hook_error(error: Exception, hook_name: str, context: dict[str, Any]):
    """
    Centralized error handling for hooks.

    Args:
        error: The exception that occurred
        hook_name: Name of the hook where error occurred
        context: Contextual information

    Example:
        try:
            # Hook logic
            process_data()
        except Exception as e:
            handle_hook_error(e, "post_tool_use", {
                "tool": tool_name,
                "spec_id": spec_id
            })
            raise
    """
    error_type = classify_error(error)

    # Log with context
    log_error_with_context(error, context)

    # Create user report for actionable/fatal errors
    if error_type in ("actionable", "fatal"):
        report = create_error_report(error, context)
        print(f"\n{'='*80}")
        print(report)
        print(f"{'='*80}\n")

    # Store pattern for learning
    try:
        from .context import store_error_pattern
        store_error_pattern(
            error_name=type(error).__name__,
            error_message=str(error),
            context=context,
            hook_name=hook_name
        )
    except ImportError:
        pass  # Gracefully continue if pattern storage unavailable

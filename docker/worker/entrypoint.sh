#!/bin/bash
set -e

# Auto-Claude Headless Worker Entrypoint
#
# This script initializes the worker environment and runs Auto-Claude
# in headless mode (no Electron GUI).

echo "=== Auto-Claude Headless Worker ==="
echo "Started at: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"

# Validate required environment variables
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "ERROR: ANTHROPIC_API_KEY environment variable is required"
    exit 1
fi

# Optional: Claude Code OAuth token for SDK features
if [ -z "$CLAUDE_CODE_OAUTH_TOKEN" ]; then
    echo "WARNING: CLAUDE_CODE_OAUTH_TOKEN not set - some features may be limited"
fi

# Configure git for worktree operations
git config --global user.email "auto-claude-worker@localhost"
git config --global user.name "Auto-Claude Worker"
git config --global init.defaultBranch main
git config --global --add safe.directory '*'

# Set up workspace
WORKSPACE=${AUTO_CLAUDE_WORKSPACE:-/workspace}
OUTPUT_DIR=${AUTO_CLAUDE_OUTPUT_DIR:-/output}
SPECS_DIR=${SPECS_DIR:-/specs}

echo "Workspace: $WORKSPACE"
echo "Output: $OUTPUT_DIR"
echo "Specs: $SPECS_DIR"

# If a project repo URL is provided, clone it
if [ -n "$PROJECT_REPO_URL" ]; then
    echo "Cloning project repository: $PROJECT_REPO_URL"
    if [ -d "$WORKSPACE/.git" ]; then
        echo "Workspace already has a git repo, pulling latest..."
        cd "$WORKSPACE"
        git fetch origin
        git reset --hard origin/$(git rev-parse --abbrev-ref HEAD)
    else
        git clone "$PROJECT_REPO_URL" "$WORKSPACE"
        cd "$WORKSPACE"
    fi

    # Checkout specific branch if specified
    if [ -n "$PROJECT_BRANCH" ]; then
        echo "Checking out branch: $PROJECT_BRANCH"
        git checkout "$PROJECT_BRANCH" 2>/dev/null || git checkout -b "$PROJECT_BRANCH"
    fi
else
    echo "No PROJECT_REPO_URL set, using local workspace"
    cd "$WORKSPACE"

    # Initialize git repo if not exists
    if [ ! -d ".git" ]; then
        git init
        echo "# Auto-Claude Workspace" > README.md
        git add README.md
        git commit -m "Initial commit"
    fi
fi

# Copy specs from mounted volume to workspace if they exist
if [ -d "$SPECS_DIR" ] && [ "$(ls -A $SPECS_DIR 2>/dev/null)" ]; then
    echo "Copying specs from $SPECS_DIR to workspace..."
    mkdir -p "$WORKSPACE/.auto-claude/specs"
    cp -r "$SPECS_DIR"/* "$WORKSPACE/.auto-claude/specs/" 2>/dev/null || true
fi

# Create output directories
mkdir -p "$OUTPUT_DIR/logs"
mkdir -p "$OUTPUT_DIR/artifacts"
mkdir -p "$OUTPUT_DIR/qa-reports"

# Log file for this run
TIMESTAMP=$(date -u '+%Y%m%d_%H%M%S')
LOG_FILE="$OUTPUT_DIR/logs/run_${TIMESTAMP}.log"

echo "Log file: $LOG_FILE"
echo ""

# Function to copy artifacts after build
copy_artifacts() {
    echo "Copying build artifacts to output..."

    # Copy spec artifacts
    if [ -d "$WORKSPACE/.auto-claude/specs" ]; then
        cp -r "$WORKSPACE/.auto-claude/specs" "$OUTPUT_DIR/artifacts/" 2>/dev/null || true
    fi

    # Copy QA reports
    find "$WORKSPACE" -name "qa_report.md" -exec cp {} "$OUTPUT_DIR/qa-reports/" \; 2>/dev/null || true
    find "$WORKSPACE" -name "QA_FIX_REQUEST.md" -exec cp {} "$OUTPUT_DIR/qa-reports/" \; 2>/dev/null || true

    # Copy implementation plans
    find "$WORKSPACE" -name "implementation_plan.json" -exec cp {} "$OUTPUT_DIR/artifacts/" \; 2>/dev/null || true

    echo "Artifacts copied to $OUTPUT_DIR"
}

# Trap to ensure artifacts are copied even on failure
trap copy_artifacts EXIT

# Run Auto-Claude with all arguments passed to this script
echo "Running: python /app/backend/run.py --project-dir $WORKSPACE $@"
echo "=========================================="

cd /app/backend
python run.py --project-dir "$WORKSPACE" --auto-continue "$@" 2>&1 | tee "$LOG_FILE"

EXIT_CODE=${PIPESTATUS[0]}

echo "=========================================="
echo "Build completed with exit code: $EXIT_CODE"
echo "Finished at: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"

exit $EXIT_CODE

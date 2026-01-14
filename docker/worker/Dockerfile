# Auto-Claude Headless Worker
# Runs Auto-Claude builds without Electron GUI
#
# Build:
#   docker build -t auto-claude-worker -f docker/worker/Dockerfile .
#
# Run:
#   docker run -v $(pwd)/specs:/specs -v $(pwd)/output:/output \
#     -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
#     auto-claude-worker --spec 001

FROM python:3.12-slim-bookworm

LABEL org.opencontainers.image.title="Auto-Claude Headless Worker"
LABEL org.opencontainers.image.description="Headless Auto-Claude build worker for control plane"
LABEL org.opencontainers.image.source="https://github.com/snowdroog/Auto-Claude"

# Prevent Python from writing pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*

# Install UV (fast Python package manager)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Install Node.js (required for Claude CLI)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Claude CLI globally
RUN npm install -g @anthropic-ai/claude-code

# Copy requirements first for better layer caching
COPY apps/backend/requirements.txt /app/requirements.txt

# Create virtual environment and install dependencies
RUN uv venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"
ENV VIRTUAL_ENV="/app/.venv"

RUN uv pip install -r requirements.txt

# Copy backend code
COPY apps/backend /app/backend

# Copy .claude framework (hooks, skills, agents, patterns)
COPY .claude /app/.claude

# Copy prompts
COPY apps/backend/prompts /app/backend/prompts

# Create directories for specs and output
RUN mkdir -p /specs /output /workspace

# Set PYTHONPATH
ENV PYTHONPATH="/app/backend:$PYTHONPATH"

# Copy entrypoint script
COPY docker/worker/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Volume mounts
# /specs    - Input: spec directories to build
# /output   - Output: build artifacts, logs, QA reports
# /workspace - Working directory for builds
VOLUME ["/specs", "/output", "/workspace"]

# Default environment variables
ENV AUTO_CLAUDE_HEADLESS=1
ENV AUTO_CLAUDE_OUTPUT_DIR=/output
ENV AUTO_CLAUDE_WORKSPACE=/workspace

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["--help"]

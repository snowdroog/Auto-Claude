# Auto-Claude Control Plane - Docker

Headless Auto-Claude worker for running builds without the Electron GUI.

## Quick Start

### 1. Build the Worker Image

```bash
cd docker
docker-compose build worker
```

### 2. Set Environment Variables

```bash
# Required: Anthropic API key
export ANTHROPIC_API_KEY=sk-ant-xxx

# Optional: Claude Code OAuth token for SDK features
export CLAUDE_CODE_OAUTH_TOKEN=xxx

# Optional: Clone a project repo into workspace
export PROJECT_REPO_URL=https://github.com/user/repo.git
export PROJECT_BRANCH=main
```

### 3. Run a Build

```bash
# List available specs
docker-compose run --rm worker --list

# Run a specific spec
docker-compose run --rm worker --spec 001

# Run with verbose output
docker-compose run --rm worker --spec 001 --verbose

# Run QA validation
docker-compose run --rm worker --spec 001 --qa
```

## Directory Structure

```
docker/
├── data/
│   ├── specs/          # Input: spec directories
│   ├── output/         # Output: logs, artifacts, QA reports
│   │   ├── logs/
│   │   ├── artifacts/
│   │   └── qa-reports/
│   └── workspace/      # Build workspace (git repo)
├── worker/
│   ├── Dockerfile
│   └── entrypoint.sh
├── docker-compose.yml
└── README.md
```

## Volume Mounts

| Mount | Purpose | Mode |
|-------|---------|------|
| `/specs` | Input specs to build | Read-only |
| `/output` | Build artifacts and logs | Read-write |
| `/workspace` | Git workspace for builds | Read-write |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | Anthropic API key for Claude |
| `CLAUDE_CODE_OAUTH_TOKEN` | No | Claude Code OAuth token |
| `PROJECT_REPO_URL` | No | Git repo to clone into workspace |
| `PROJECT_BRANCH` | No | Branch to checkout |

## Running Without Docker Compose

```bash
# Build image
docker build -t auto-claude-worker -f docker/worker/Dockerfile .

# Run with explicit mounts
docker run --rm \
  -v $(pwd)/docker/data/specs:/specs:ro \
  -v $(pwd)/docker/data/output:/output \
  -v $(pwd)/docker/data/workspace:/workspace \
  -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
  auto-claude-worker --spec 001
```

## Deploying to Remote Server (Appbox/Hetzner)

### 1. Copy to Server

```bash
# From your local machine
rsync -avz --exclude 'data/' docker/ user@server:/opt/auto-claude/
```

### 2. Build on Server

```bash
ssh user@server
cd /opt/auto-claude
docker-compose build worker
```

### 3. Create Data Directories

```bash
mkdir -p data/{specs,output,workspace}
```

### 4. Set API Key

```bash
# Add to ~/.bashrc or /etc/environment
export ANTHROPIC_API_KEY=sk-ant-xxx
```

### 5. Run Builds

```bash
# Copy a spec to build
scp -r .auto-claude/specs/001-feature user@server:/opt/auto-claude/data/specs/

# Run the build
docker-compose run --rm worker --spec 001
```

## Output Artifacts

After a build completes, find outputs in `data/output/`:

- `logs/run_YYYYMMDD_HHMMSS.log` - Full build log
- `artifacts/specs/` - Completed spec files
- `qa-reports/` - QA validation reports

## Resource Limits

Default limits (configurable in docker-compose.yml):

- CPU: 2 cores (limit), 1 core (reserved)
- Memory: 4GB (limit), 2GB (reserved)

## Troubleshooting

### Build Fails with "ANTHROPIC_API_KEY required"

```bash
# Ensure the variable is exported
export ANTHROPIC_API_KEY=sk-ant-xxx

# Verify it's set
echo $ANTHROPIC_API_KEY
```

### Git Operations Fail

```bash
# Mount SSH keys for private repos
docker run -v ~/.ssh:/root/.ssh:ro ...

# Or use HTTPS with token
export PROJECT_REPO_URL=https://token@github.com/user/repo.git
```

### Out of Memory

Increase memory limit in docker-compose.yml:

```yaml
deploy:
  resources:
    limits:
      memory: 8G
```

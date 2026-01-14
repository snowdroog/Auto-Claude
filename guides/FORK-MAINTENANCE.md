# Fork Maintenance Guide

This guide covers maintaining your fork of Auto-Claude, including syncing with upstream changes.

## Automated Upstream Monitoring

The repository includes a GitHub Actions workflow that automatically monitors the upstream repository (`AndyMik90/Auto-Claude:develop`) for new commits.

### How It Works

1. **Daily Check**: The workflow runs at 6am UTC daily
2. **Comparison**: Compares your fork's `develop` branch with upstream
3. **Issue Creation**: Creates a GitHub issue labeled `upstream-sync` if new commits exist
4. **Issue Updates**: If an open sync issue exists, adds a comment with new commit details

### Manual Trigger

You can manually run the workflow from the Actions tab:

1. Go to **Actions** > **Upstream Monitor**
2. Click **Run workflow**
3. Select branch (default: `develop`)
4. Click **Run workflow**

### Workflow File

Location: `.github/workflows/upstream-monitor.yml`

### Issue Format

When new upstream commits are detected, the created issue includes:
- Number of new commits
- Commit list with authors and dates
- Files changed summary
- Sync instructions (rebase vs merge)

## Syncing with Upstream

When you receive an upstream sync notification:

### Option 1: Cherry-Pick Specific Commits (Recommended)

```bash
# Fetch latest from origin (which points to upstream)
git fetch origin main

# View available commits
git log --oneline origin/main ^HEAD

# Cherry-pick specific commits you want
git cherry-pick <commit-hash>

# Push to fork
git push myfork snowdroog-clean
```

### Option 2: Merge All Upstream Changes

```bash
# Fetch latest
git fetch origin main

# Merge upstream changes into your branch
git checkout snowdroog-clean
git merge origin/main

# Push to fork
git push myfork snowdroog-clean
```

### Resolving Conflicts

If conflicts arise during sync:

```bash
# For rebase
git rebase --continue  # after resolving
git rebase --abort     # to cancel

# For merge
git merge --continue   # after resolving
git merge --abort      # to cancel
```

## Remote Configuration

Standard fork setup uses these remotes:

| Remote | Repository | Purpose |
|--------|------------|---------|
| `origin` | AndyMik90/Auto-Claude | Upstream source |
| `myfork` | snowdroog/Auto-Claude | Your fork |

Check your remotes:
```bash
git remote -v
```

## Contributing Back

When contributing fixes to upstream:

1. Create feature branch from `origin/develop`
2. Make changes and commit with sign-off
3. Push to your fork
4. Create PR targeting `develop` branch (NOT `main`)

```bash
# Create feature branch
git checkout -b fix/my-fix origin/develop

# Make changes, then commit
git commit -s -m "fix: description"

# Push to fork
git push myfork fix/my-fix

# Create PR to upstream develop branch
gh pr create --repo AndyMik90/Auto-Claude --base develop
```

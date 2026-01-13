---
name: git-helper
version: 1.0.0
description: Common git workflows for Auto-Claude development - commit, branch management, and sync operations
model: haiku
triggers:
  - create commit
  - git commit
  - commit changes
  - create branch
  - sync with upstream
  - merge branch
  - git workflow
---

# Git Helper Skill

Provides natural language interface to common git operations for Auto-Claude development.

## What This Skill Does

The git-helper skill assists with:
- Creating properly formatted commits
- Branch management and cleanup
- Syncing with upstream repositories
- Merge operations
- Commit history review

## Usage Examples

**Creating Commits:**
- "create a commit with the SFA changes"
- "commit these changes with message 'feat: add new feature'"
- "git commit the modified files"

**Branch Operations:**
- "create a new branch for feature X"
- "switch to the develop branch"
- "delete the old feature branch"
- "list all branches"

**Sync Operations:**
- "sync with upstream develop"
- "pull latest changes from origin"
- "push to my fork"

**Merge Operations:**
- "merge feature branch into main"
- "squash merge the PR changes"

## How It Works

This skill uses the Bash tool to execute git commands based on your natural language requests. It:

1. **Understands Intent** - Parses your request to determine the git operation
2. **Validates Context** - Checks current git state before proceeding
3. **Executes Safely** - Runs git commands with appropriate options
4. **Provides Feedback** - Shows results and next steps

## Git Commands Reference

### Commit Operations

**Standard Commit:**
```bash
git add <files>
git commit -m "type(scope): subject

body

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

**Amend Last Commit:**
```bash
git commit --amend --no-edit
```

**Interactive Staging:**
```bash
git add -p  # Stage hunks interactively
```

### Branch Operations

**Create Branch:**
```bash
git checkout -b feature/new-feature
```

**List Branches:**
```bash
git branch -vv  # With tracking info
```

**Delete Branch:**
```bash
git branch -d feature/old-feature  # Safe delete
git branch -D feature/old-feature  # Force delete
```

**Rename Branch:**
```bash
git branch -m old-name new-name
```

### Sync Operations

**Pull from Upstream:**
```bash
git fetch origin
git merge origin/develop
```

**Push to Fork:**
```bash
git push myfork branch-name
```

**Sync Fork with Upstream:**
```bash
git fetch origin
git checkout develop
git merge --ff-only origin/develop
git push myfork develop
```

### Merge Operations

**Standard Merge:**
```bash
git merge feature-branch --no-ff
```

**Squash Merge:**
```bash
git merge --squash feature-branch
git commit
```

**Rebase:**
```bash
git rebase main
```

## Safety Features

This skill includes safety checks:

- **Uncommitted Changes** - Warns if working directory is dirty
- **Branch Protection** - Prevents force push to main/develop
- **Merge Conflicts** - Detects and guides through resolution
- **Backup Suggestions** - Recommends creating backup branches

## Commit Message Format

Follows Conventional Commits:

```
<type>(<scope>): <subject>

[optional body]

[optional footer]

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation
- `refactor` - Code refactoring
- `test` - Tests
- `chore` - Maintenance
- `perf` - Performance
- `style` - Formatting

**Examples:**
```
feat(sfa): add dependency analyzer agent
fix(hooks): handle missing context gracefully
docs(patterns): add git workflow pattern
```

## Integration with Auto-Claude

### Hook Integration

The skill can be invoked from hooks:

```python
# In .claude/hooks/stop.py
if changes_to_commit:
    # User can say "commit the changes"
    # git-helper skill will handle it
    pass
```

### Pattern References

See related patterns:
- [Git Workflow Pattern](../../patterns/git-workflow.md)
- [Worktree Isolation Pattern](../../patterns/worktree-isolation.md)

## Troubleshooting

**Issue: Merge conflicts**
```bash
# Check conflict status
git status

# View conflicting files
git diff --name-only --diff-filter=U

# After resolving
git add <resolved-files>
git commit
```

**Issue: Detached HEAD**
```bash
# Create branch from current state
git checkout -b recovery-branch

# Or discard and return to branch
git checkout main
```

**Issue: Wrong commit**
```bash
# Undo last commit (keep changes)
git reset HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1
```

## Best Practices

1. **Commit Often** - Small, focused commits are easier to review
2. **Descriptive Messages** - Future you will thank you
3. **Test Before Commit** - Run tests before committing
4. **Review Diff** - Always check `git diff` before committing
5. **Use Branches** - One feature = one branch
6. **Sync Regularly** - Pull from upstream frequently

## Related Skills

- **auto-claude-build** - Autonomous builds that may need commits
- **archon** - Project tracking that references commits

## Resources

- [Git Documentation](https://git-scm.com/doc)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Git Workflow Pattern](../../patterns/git-workflow.md)

## Examples

### Example 1: Create Feature Commit

**User:** "commit the new SFA agents with a feature message"

**Skill Actions:**
1. Check git status for staged/unstaged files
2. Stage relevant files
3. Create commit with feat type
4. Show commit hash and summary

### Example 2: Sync with Upstream

**User:** "sync my fork with upstream develop"

**Skill Actions:**
1. Fetch from origin (upstream)
2. Checkout develop branch
3. Fast-forward merge origin/develop
4. Push to myfork
5. Confirm sync complete

### Example 3: Clean Branch Management

**User:** "delete the completed feature branches"

**Skill Actions:**
1. List merged branches
2. Confirm which to delete
3. Delete local branches
4. Optionally delete remote branches
5. Run `git branch -d` safely

## Tips

- Use `git status` frequently to understand current state
- Create backup branches before risky operations
- Use `--dry-run` flag to preview operations
- Check `git log` to verify commits
- Use `git reflog` to recover lost commits

# Git Helper Skill

Natural language interface for common git operations in Auto-Claude development.

## Quick Start

Just ask in natural language:
- "commit these changes"
- "create a new feature branch"
- "sync with upstream"
- "merge my feature branch"

## Common Commands

### Committing Changes

```
"commit the SFA changes"
"create a commit for the new patterns"
"amend the last commit"
```

### Branch Management

```
"create a branch for feature X"
"switch to develop branch"
"list all branches"
"delete old feature branches"
```

### Syncing

```
"sync with upstream develop"
"pull latest changes"
"push to my fork"
```

### Merging

```
"merge feature branch into main"
"squash merge the PR"
"rebase on main"
```

## Safety Features

- Warns about uncommitted changes
- Prevents force push to protected branches
- Detects merge conflicts
- Suggests backups before risky operations

## Commit Format

Follows Conventional Commits with Auto-Claude co-authorship:

```
feat(scope): add new feature

Detailed description of changes

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

## Related

- [Git Workflow Pattern](../../patterns/git-workflow.md) - Comprehensive git patterns
- [Worktree Isolation](../../patterns/worktree-isolation.md) - Branch isolation strategy

## Examples

**Example 1: Create and Commit**
```
User: "add the new files and commit them as a feature"
Assistant: [Stages files, creates feat commit, shows summary]
```

**Example 2: Sync Fork**
```
User: "sync my fork with upstream"
Assistant: [Fetches, merges, pushes to fork, confirms sync]
```

**Example 3: Clean Branches**
```
User: "delete merged feature branches"
Assistant: [Lists merged branches, confirms, deletes safely]
```

## Tips

- Check `git status` frequently
- Review `git diff` before committing
- Use descriptive commit messages
- Sync with upstream regularly
- Create branches for new work

## Troubleshooting

**Merge Conflicts:**
- Skill will detect conflicts
- Follow guidance to resolve
- Use `git status` to check progress

**Detached HEAD:**
- Create branch from current state
- Or checkout an existing branch

**Wrong Commit:**
- Use `git reset` to undo
- Amend if just committed
- Check `git reflog` for recovery

For more details, see [SKILL.md](./SKILL.md).

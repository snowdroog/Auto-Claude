# Git Workflow Pattern

Auto-Claude's branch management and commit patterns for safe, isolated feature development.

## Pattern Overview

```
main/develop (user's branch)
└── auto-claude/{spec-name}  ← Isolated feature branch
    ├── Worktree at .worktrees/{spec-name}/
    ├── All changes contained
    └── Merge back when approved
```

## Branch Isolation

### Why Worktrees?

**Benefits:**
- Work on multiple specs simultaneously
- Each spec has dedicated directory
- No branch switching interruptions
- Clean separation of concerns
- Easy to delete if spec fails

**Location:**
```
.worktrees/
├── 001-auth-feature/     # Spec 001 worktree
├── 002-dark-mode/        # Spec 002 worktree
└── 003-api-refactor/     # Spec 003 worktree
```

### Branch Naming

**Convention:**
```
auto-claude/{spec-id}-{short-name}
```

**Examples:**
- `auto-claude/001-auth-feature`
- `auto-claude/002-dark-mode`
- `auto-claude/003-api-refactor`

## Commit Patterns

### Commit Message Format

Follow Conventional Commits:

```
<type>(<scope>): <subject>

[optional body]

[optional footer]

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

### Types

| Type | Use Case | Example |
|------|----------|---------|
| `feat` | New feature | `feat(auth): add OAuth login` |
| `fix` | Bug fix | `fix(api): handle null user response` |
| `docs` | Documentation | `docs(readme): add setup guide` |
| `refactor` | Code refactoring | `refactor(db): extract query builder` |
| `test` | Add/update tests | `test(auth): add login flow tests` |
| `chore` | Maintenance | `chore(deps): update dependencies` |
| `perf` | Performance improvement | `perf(api): cache user queries` |
| `style` | Code style changes | `style(lint): fix formatting` |

### Commit Workflow

```bash
# 1. Stage relevant files
git add <files>

# 2. Check diff
git diff --staged

# 3. Commit with message
git commit -m "feat(auth): add JWT token validation

Implement JWT validation middleware for API endpoints:
- Verify token signature
- Check expiration
- Extract user claims
- Handle refresh tokens

Closes #42

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

## Merge Workflow

### Pre-Merge Checklist

Before merging spec branch to main:

- [ ] All tests pass
- [ ] QA report shows acceptance
- [ ] Build succeeds
- [ ] No merge conflicts
- [ ] User reviewed changes
- [ ] Documentation updated

### Merge Process

**Option 1: Squash Merge (Recommended for Clean History)**

```bash
# From main branch
git merge --squash auto-claude/001-auth-feature
git commit -m "feat(auth): implement OAuth authentication system

Complete OAuth 2.0 authentication flow with JWT:
- OAuth provider integration
- Token management
- Session persistence
- User profile sync

QA Report: PASSED (all 8 acceptance criteria met)
Spec: .auto-claude/specs/001-auth-feature/

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

**Option 2: Standard Merge (Preserve History)**

```bash
# From main branch
git merge auto-claude/001-auth-feature --no-ff
```

**Option 3: Rebase (Clean Linear History)**

```bash
# From spec branch
git rebase main

# Then from main
git merge auto-claude/001-auth-feature --ff-only
```

### Post-Merge Cleanup

```bash
# Delete spec branch
git branch -d auto-claude/001-auth-feature

# Delete worktree
git worktree remove .worktrees/001-auth-feature

# Or using Auto-Claude CLI
python run.py --spec 001 --discard
```

## Conflict Resolution

### Common Conflicts

**Scenario 1: Parallel Specs Modify Same File**

```bash
# Merge one spec first
git merge auto-claude/001-auth-feature

# Resolve conflicts in second spec
cd .worktrees/002-user-profile/
git fetch origin main
git rebase main

# Fix conflicts
# Continue build with resolved conflicts
```

**Scenario 2: Upstream Changes During Build**

```bash
# Sync main with upstream
git pull origin main

# Rebase spec branch
cd .worktrees/001-auth-feature/
git rebase main

# Let QA reviewer re-validate after rebase
```

### Conflict Markers

```python
<<<<<<< HEAD (main branch)
def authenticate_user(username, password):
    # Old implementation
    return legacy_auth(username, password)
=======
def authenticate_user(username: str, password: str) -> User:
    # New implementation with OAuth
    return oauth_provider.authenticate(username, password)
>>>>>>> auto-claude/001-auth-feature
```

**Resolution Strategy:**
1. Understand both versions
2. Keep main's bug fixes if any
3. Apply spec's enhancements
4. Test merged result
5. Document in commit message

## Safety Patterns

### Never Force Push to Main

```bash
# ❌ NEVER do this
git push origin main --force

# ✅ Always use pull + merge
git pull origin main
git merge auto-claude/001-feature
git push origin main
```

### Always Review Before Push

```bash
# Check what will be pushed
git log origin/main..HEAD --oneline

# See the diff
git diff origin/main..HEAD

# Then push
git push origin main
```

### Backup Before Risky Operations

```bash
# Create backup branch
git branch backup/before-merge-001

# Perform operation
git merge auto-claude/001-feature

# If something goes wrong
git reset --hard backup/before-merge-001
```

## Integration with Auto-Claude

### Automated Branch Creation

```python
# In spec_runner.py
def create_spec_worktree(spec_id, spec_name):
    branch_name = f"auto-claude/{spec_id}-{spec_name}"
    worktree_path = f".worktrees/{spec_id}-{spec_name}"

    subprocess.run(["git", "worktree", "add", "-b", branch_name, worktree_path])
    return worktree_path
```

### Commit Hook Integration

```python
# In .claude/hooks/stop.py
def create_commit_on_success():
    if build_successful and qa_passed:
        git_commit_with_qa_report()
```

### Branch Cleanup Hook

```python
# In .claude/hooks/post_merge.py
def cleanup_after_merge(spec_id):
    remove_worktree(spec_id)
    delete_branch(spec_id)
    archive_spec_data(spec_id)
```

## Best Practices

1. **One Spec = One Branch**: Never mix multiple specs in one branch
2. **Commit Often**: Small, focused commits are easier to review
3. **Descriptive Messages**: Future you will thank you
4. **Test Before Commit**: Run tests before committing
5. **Review Before Merge**: Always review the full diff
6. **Clean History**: Squash fixup commits before merging
7. **Document Decisions**: Use commit body for context

## Troubleshooting

### Orphaned Worktrees

```bash
# List all worktrees
git worktree list

# Remove dead worktrees
git worktree prune

# Force remove stuck worktree
rm -rf .worktrees/001-auth-feature
git worktree prune
```

### Detached HEAD in Worktree

```bash
cd .worktrees/001-auth-feature
git checkout auto-claude/001-auth-feature
```

### Lost Commits

```bash
# Find lost commit
git reflog

# Recover commit
git cherry-pick <commit-hash>
```

## Metrics

**Target Metrics:**
- Merge conflicts: < 5% of builds
- Average commits per spec: 5-15
- Time to merge: < 1 day after QA approval
- Abandoned branches: < 10%

**Red Flags:**
- Frequent merge conflicts (poor spec isolation)
- Huge commits (lack of incremental progress)
- Many abandoned branches (specs too ambitious)
- Force pushes to main (dangerous workflow)

## Resources

- [Git Worktrees Documentation](https://git-scm.com/docs/git-worktree)
- [Conventional Commits Spec](https://www.conventionalcommits.org/)
- [Auto-Claude Worktree Manager](../cli/worktree.py)
- Pattern: [Worktree Isolation](./worktree-isolation.md)

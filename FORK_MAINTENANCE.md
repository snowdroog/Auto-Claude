# Fork Maintenance Strategy

This document explains how we maintain our downstream fork of Auto-Claude with our custom enhancements.

## Philosophy

**snowdroog/Auto-Claude** is a downstream fork of **AndyMik90/Auto-Claude** with our own vision:
- ✅ Pull all upstream improvements regularly
- ✅ Overlay our enhancements on top
- ❌ Never contribute back to upstream (separate evolution paths)
- ✅ Document what we change and why

## Branch Structure

```
snowdroog/Auto-Claude
├── develop           → Tracks AndyMik90:develop (fast-forward only, no custom commits)
├── snowdroog-main    → OUR production branch (develop + enhancements)
└── feature/*         → Experimental enhancements before merging to snowdroog-main
```

### Branch Purposes

**`develop`** - Upstream tracking branch
- ONLY contains upstream commits
- Fast-forward merged from `origin/develop` (AndyMik90/Auto-Claude)
- Never contains our custom commits
- Acts as the "clean slate" for rebasing

**`snowdroog-main`** - Our production branch
- Contains ALL our enhancements rebased on top of `develop`
- This is what we deploy/use/distribute
- Regularly rebased onto updated `develop`

**`feature/*`** - Enhancement development
- New features we're adding
- Testing ground before merging to `snowdroog-main`

## Our Enhancements

See [ENHANCEMENTS.md](ENHANCEMENTS.md) for detailed documentation.

**Summary:**
1. **`.claude/` Framework** - Hooks, skills, agents, patterns for Claude Code
2. **Prompt Modernization** - YAML frontmatter + XML structure (v2.0.0)
3. **Single-File Agents (SFA)** - UV-based standalone tools with PEP 723
4. **IndyDevDan Patterns** - Best practices from IndyDevDan template
5. **UV-First Paradigm** - Prefer UV over pip/poetry for dependency management

## Regular Sync Workflow

When upstream (AndyMik90/Auto-Claude) releases updates:

### Step 1: Update develop branch

```bash
git checkout develop
git fetch origin                    # origin = AndyMik90/Auto-Claude
git merge --ff-only origin/develop  # Fast-forward only (no merge commits)
```

### Step 2: Rebase our enhancements

```bash
git checkout snowdroog-main
git rebase develop                  # Overlay our commits on new base
```

### Step 3: Resolve conflicts (if any)

If rebasing conflicts (rare, since we modify different files):
```bash
# Fix conflicts in affected files
git add <resolved-files>
git rebase --continue
```

### Step 4: Push to our fork

```bash
git push myfork snowdroog-main --force-with-lease
```

**Note:** Use `--force-with-lease` because rebase rewrites history. This is safe for our production branch.

### Step 5: Review what changed upstream

```bash
git log develop~10..develop --oneline  # See last 10 upstream commits
git diff develop~10..develop --stat    # See what files changed
```

### Step 6: Update feature branches (if needed)

```bash
git checkout feature/my-enhancement
git rebase snowdroog-main
```

## Conflict Prevention

Our enhancements focus on areas upstream rarely touches:
- ✅ `.claude/` directory (doesn't exist upstream)
- ✅ `apps/backend/prompts/*` (we modernize structure, they change content)
- ✅ `apps/backend/single-file-agents/` (doesn't exist upstream)
- ⚠️  `apps/backend/spec/` (we modify, they modify - potential conflicts)
- ⚠️  `apps/backend/core/` (we extend, they fix - potential conflicts)

## When Conflicts Occur

1. **Understand what changed**: Read upstream commit messages
2. **Preserve their bug fixes**: Accept their logic changes
3. **Reapply our enhancements**: Keep our structural improvements
4. **Document in commit**: Note what was merged and why

## Testing After Sync

After rebasing on upstream changes:

```bash
# 1. Run tests
cd apps/backend && uv run pytest

# 2. Test spec creation
python spec_runner.py --task "test task" --complexity simple

# 3. Test our enhancements
python single-file-agents/agents/sfa_spec_query_anthropic_v1.py --help

# 4. Verify .claude/ hooks work
# (Create a test session with Claude Code)
```

## Emergency: Rollback Bad Upstream Change

If upstream introduces a breaking change:

```bash
# Rollback develop to previous commit
git checkout develop
git reset --hard <previous-commit>

# Rebase snowdroog-main on safe version
git checkout snowdroog-main
git rebase develop

# Document why in ENHANCEMENTS.md under "Divergences from Upstream"
```

## GitHub Remote Configuration

```bash
# Check current remotes
git remote -v

# Should show:
# origin  https://github.com/AndyMik90/Auto-Claude.git (fetch)
# origin  https://github.com/AndyMik90/Auto-Claude.git (push)
# myfork  https://github.com/snowdroog/Auto-Claude.git (fetch)
# myfork  https://github.com/snowdroog/Auto-Claude.git (push)
```

## Archon Project Tracking

This maintenance work is tracked in Archon:
- **Project**: Auto-Claude Fork Maintenance & Enhancement
- **Project ID**: 24e20808-303f-4c64-95e8-248d8095518c

Regular tasks:
- Monitor upstream for updates
- Review and integrate changes
- Extend SFA framework
- Refine .claude/ patterns
- Document divergences

## Quick Reference

```bash
# Sync from upstream
git checkout develop && git fetch origin && git merge --ff-only origin/develop
git checkout snowdroog-main && git rebase develop
git push myfork snowdroog-main --force-with-lease

# See our enhancements vs upstream
git diff develop..snowdroog-main --stat

# See commits we added
git log develop..snowdroog-main --oneline

# See what changed upstream recently
git log origin/develop --oneline -10
```

## Questions?

See:
- [ENHANCEMENTS.md](ENHANCEMENTS.md) - What we've enhanced and why
- [.claude/README.md](.claude/README.md) - Claude Code integration
- [apps/backend/single-file-agents/README.md](apps/backend/single-file-agents/README.md) - SFA framework

---

**Last Updated**: 2026-01-12
**Current Base**: AndyMik90/Auto-Claude@5e84912 (v2.7.3 + bug fixes)
**Our Commits**: 5 enhancement commits on top

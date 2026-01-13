# Fork Maintenance Strategy

This document explains how we maintain our downstream fork of Auto-Claude with our custom enhancements.

## Current Status

**Active Branch:** `snowdroog-clean` ✅
- **GitHub**: https://github.com/snowdroog/Auto-Claude/tree/snowdroog-clean
- **Base Commit**: 6dc538c (upstream v2.7.3 + bug fixes)
- **Our Enhancement Commits**: 7 commits
- **Status**: Stable, pushed to GitHub, ready to use

**Recent Enhancements Added** (Jan 2026):
1. ✅ Complete `.claude/` framework (agents, skills, hooks, patterns)
2. ✅ Prompt modernization (YAML frontmatter + XML structure v2.0.0)
3. ✅ Single-File Agents framework (UV + PEP 723)
4. ✅ 4 observability SFAs (events analyzer, cost tracker, loop detector, failure investigator)
5. ✅ Session analytics agent integration
6. ✅ Documentation (FORK_MAINTENANCE.md, FORK_STATUS.md, ENHANCEMENTS.md)

**Archon Tracking:**
- Project: Auto-Claude Fork Maintenance & Enhancement
- Project ID: `24e20808-303f-4c64-95e8-248d8095518c`
- All Phase 4 tasks complete (Sub-Agent System)

## Philosophy

**snowdroog/Auto-Claude** is a downstream fork of **AndyMik90/Auto-Claude** with our own vision:
- ✅ Pull all upstream improvements regularly
- ✅ Overlay our enhancements on top
- ❌ Never contribute back to upstream (separate evolution paths)
- ✅ Document what we change and why

## Branch Structure

```
snowdroog/Auto-Claude
├── develop              → Tracks AndyMik90:develop (fast-forward only, no custom commits)
├── snowdroog-clean      → OUR production branch (currently active) ✅
├── snowdroog-main       → Legacy production (has workflow OAuth issues, deprecated)
└── feature/*            → Experimental enhancements before merging to production
```

### Branch Purposes

**`develop`** - Upstream tracking branch
- ONLY contains upstream commits
- Fast-forward merged from `origin/develop` (AndyMik90/Auto-Claude)
- Never contains our custom commits
- Acts as the "clean slate" for rebasing

**`snowdroog-clean`** - Our production branch (CURRENT) ✅
- Contains ALL our enhancements
- Based on stable upstream commit (before workflow file changes)
- Can be pushed to GitHub without OAuth scope issues
- This is what we currently deploy/use/distribute
- **GitHub**: `myfork/snowdroog-clean`

**`snowdroog-main`** - Legacy production (DEPRECATED)
- Contains upstream's workflow file commits (can't push without workflow scope)
- Use `snowdroog-clean` instead until upstream workflow lands on main

**`feature/*`** - Enhancement development
- New features we're adding
- Testing ground before merging to production branch

## Our Enhancements

See [ENHANCEMENTS.md](ENHANCEMENTS.md) for detailed documentation.

**Summary:**
1. **`.claude/` Framework** - Hooks, skills, agents, patterns for Claude Code
2. **Prompt Modernization** - YAML frontmatter + XML structure (v2.0.0)
3. **Single-File Agents (SFA)** - UV-based standalone tools with PEP 723
4. **IndyDevDan Patterns** - Best practices from IndyDevDan template
5. **UV-First Paradigm** - Prefer UV over pip/poetry for dependency management

### Enhancement Commit History (snowdroog-clean)

Our 7 enhancement commits on top of upstream:

```
4b9cb83 - docs: add fork status summary and troubleshooting
3c7b5ba - docs: add fork maintenance and enhancement documentation
78495dc - feat(prompts): modernize phase 3 prompts and inline standalone helpers
6f5084f - feat(sfa): add single-file-agents framework
30952aa - feat(prompts): add standardized prompt template system
42179e4 - feat(claude-code): add Claude Code integration framework
1e2d2cc - chore(gitignore): commit .claude/ directory with local overrides
```

**Base upstream commit:** `6dc538c` - fix: properly quote Windows .cmd/.bat paths

**Files Added/Modified:**
- `.claude/` - Complete framework (35+ files: agents, skills, hooks, patterns, docs)
- `apps/backend/single-file-agents/` - SFA framework + 5 agents
- `apps/backend/prompts/` - Modernized prompt templates (5 files)
- `FORK_MAINTENANCE.md`, `FORK_STATUS.md`, `ENHANCEMENTS.md` - Documentation

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
git checkout snowdroog-clean
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
git push myfork snowdroog-clean --force-with-lease
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
git rebase snowdroog-clean
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

# Rebase snowdroog-clean on safe version
git checkout snowdroog-clean
git rebase develop

# Document why in ENHANCEMENTS.md under "Divergences from Upstream"
```

## GitHub Workflow OAuth Issue

**Why `snowdroog-clean` instead of `snowdroog-main`?**

GitHub's OAuth security prevents pushing commits that modify `.github/workflows/` without the `workflow` scope. This affects our ability to push branches that include upstream's workflow file changes.

**Impact:**
- ✅ `snowdroog-clean` - Based on stable commit before workflow changes (can push)
- ❌ `snowdroog-main` - Includes workflow commits from rebase (can't push)
- ❌ `develop` - Tracks upstream including workflow changes (can't push)

**Solution:**
We use `snowdroog-clean` as our production branch until upstream's workflow changes land on their `main` branch (which doesn't require workflow scope to pull).

**When this resolves:**
```bash
# Once workflow changes are on upstream main
git checkout develop
git fetch origin
git reset --hard origin/develop  # Clean slate

# Rebase our enhancements
git checkout snowdroog-clean
git rebase develop
git push myfork snowdroog-clean --force-with-lease
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
git checkout snowdroog-clean && git rebase develop
git push myfork snowdroog-clean --force-with-lease

# See our enhancements vs upstream
git diff develop..snowdroog-clean --stat

# See commits we added
git log develop..snowdroog-clean --oneline

# See what changed upstream recently
git log origin/develop --oneline -10
```

## Questions?

See:
- [ENHANCEMENTS.md](ENHANCEMENTS.md) - What we've enhanced and why
- [.claude/README.md](.claude/README.md) - Claude Code integration
- [apps/backend/single-file-agents/README.md](apps/backend/single-file-agents/README.md) - SFA framework

---

**Last Updated**: 2026-01-13
**Active Branch**: `snowdroog-clean` (myfork/snowdroog-clean)
**Current Base**: AndyMik90/Auto-Claude@6dc538c (v2.7.3 + bug fixes)
**Our Enhancement Commits**: 7 commits (complete .claude/ framework, SFAs, observability agents)
**GitHub URL**: https://github.com/snowdroog/Auto-Claude/tree/snowdroog-clean

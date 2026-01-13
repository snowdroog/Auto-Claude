# Archon Best Practices for Auto-Claude

This guide provides best practices for using Archon's knowledge base (RAG) integration to make Auto-Claude agents more effective through knowledge-driven development.

## Table of Contents

- [Overview](#overview)
- [When to Use Archon](#when-to-use-archon)
- [Query Best Practices](#query-best-practices)
- [Agent-Specific Guidance](#agent-specific-guidance)
- [Common Patterns](#common-patterns)
- [Troubleshooting](#troubleshooting)

---

## Overview

Archon provides RAG (Retrieval-Augmented Generation) search across past builds, code examples, and learnings. When properly integrated, it helps agents:

- **Learn from past implementations** - Reference proven patterns
- **Avoid known pitfalls** - Query for gotchas before implementing
- **Ask better questions** - See what worked in similar specs
- **Validate comprehensively** - Reference acceptance criteria patterns

**Key Principle**: Archon supplements (not replaces) codebase investigation and external documentation.

---

## When to Use Archon

### ✅ Good Use Cases

**Planning Phase:**
- Finding similar features implemented before
- Learning from past architectural decisions
- Discovering integration patterns

**Coding Phase:**
- Implementing unfamiliar technologies
- Security-sensitive code (auth, payments, crypto)
- Complex integrations (databases, caches, APIs)
- Performance-critical operations

**Spec Creation:**
- Learning from similar past requirements
- Discovering common edge cases
- Referencing acceptance criteria patterns

**QA Phase:**
- Finding test scenarios for similar features
- Discovering edge cases from past QA cycles
- Learning about common failure modes

### ❌ When NOT to Use Archon

- **Archon tools aren't available** - Check your available tools first
- **Looking for THIS project's patterns** - Use Read/Grep instead
- **Need latest library docs** - Use Context7 or WebSearch
- **Brand new features** - No past data to learn from
- **Time-sensitive work** - Skip if under tight deadlines
- **Trivial implementations** - Don't query for obvious patterns

---

## Query Best Practices

### The Golden Rule: Keep Queries SHORT

**Archon uses vector search, which works best with 2-5 focused keywords.**

#### ❌ Bad Queries (Too Long)

```python
# TOO LONG - performs worse
mcp__archon__rag_search_knowledge_base(
    query="how to implement user authentication with JWT tokens in FastAPI application with password hashing and session management"
)

# TOO VERBOSE
mcp__archon__rag_search_code_examples(
    query="React hooks useState useEffect useContext useReducer useMemo useCallback"
)
```

#### ✅ Good Queries (Concise & Focused)

```python
# GOOD - concise, focused
mcp__archon__rag_search_knowledge_base(
    query="FastAPI JWT authentication"
)

# GOOD - specific technology + feature
mcp__archon__rag_search_code_examples(
    query="React useState"
)

# GOOD - technology + pattern type
mcp__archon__rag_search_knowledge_base(
    query="PostgreSQL migration patterns"
)
```

### Query Patterns

| Scenario | Query Pattern | Example |
|----------|---------------|---------|
| Code examples | `[Technology] [Feature]` | `"FastAPI middleware"` |
| Integration patterns | `[Library] integration` | `"Stripe integration"` |
| Known issues | `[Technology] gotchas` | `"Redis cache gotchas"` |
| Best practices | `[Feature] patterns` | `"authentication patterns"` |
| Test scenarios | `[Feature] QA validation` | `"payment QA validation"` |
| Requirements | `[Feature] requirements` | `"API rate limiting requirements"` |

### Match Count Guidelines

```python
# For broad exploration - more results
mcp__archon__rag_search_knowledge_base(
    query="authentication patterns",
    match_count=5  # Get diverse patterns
)

# For specific examples - fewer results
mcp__archon__rag_search_code_examples(
    query="WebSocket server",
    match_count=3  # Get focused examples
)
```

**Recommendations:**
- `match_count=3` - Specific code examples
- `match_count=5` - Patterns, gotchas, requirements
- `match_count=1-2` - Very specific lookups

---

## Agent-Specific Guidance

### Planner Agent

**Use Archon BEFORE grepping the codebase.**

```python
# Query for similar implementations first
mcp__archon__rag_search_knowledge_base(
    query="authentication implementation",
    match_count=5
)

# Then grep THIS codebase
grep -r "auth" --include="*.py" . | head -30
```

**What to query:**
- Similar features from past builds
- Proven architectural patterns
- Integration approaches

**Integration point:** Phase 0 (Deep Codebase Investigation)

### Coder Agent

**Query BEFORE implementing unfamiliar patterns.**

```python
# Before implementing Redis cache
mcp__archon__rag_search_code_examples(
    query="Redis cache FastAPI",
    match_count=3
)

# Before implementing security features
mcp__archon__rag_search_knowledge_base(
    query="password hashing bcrypt",
    match_count=5
)
```

**What to query:**
- Code examples for specific technologies
- Known gotchas and edge cases
- Security best practices
- Performance patterns

**Integration point:** Phase 6.5 (After Context7, before implementation)

### Spec Gatherer Agent

**Query for similar specs to ask better questions.**

```python
# Before gathering requirements
mcp__archon__rag_search_knowledge_base(
    query="authentication requirements",
    match_count=3
)
```

**What to query:**
- Similar feature requirements
- Common edge cases
- Acceptance criteria patterns

**Integration point:** Phase 3.5 (Before gathering requirements)

### Spec Researcher Agent

**Query for integration patterns AFTER Context7.**

```python
# After getting official docs
mcp__archon__rag_search_knowledge_base(
    query="Stripe integration patterns",
    match_count=5
)
```

**What to query:**
- Integration gotchas
- Configuration patterns
- Known issues with libraries

**Integration point:** Phase 1.3 (After Context7 research)

### QA Reviewer Agent

**Query for test scenarios BEFORE validation.**

```python
# Before starting QA
mcp__archon__rag_search_knowledge_base(
    query="authentication QA validation",
    match_count=3
)
```

**What to query:**
- Test scenarios for similar features
- Edge cases from past QA
- Common failure modes

**Integration point:** Phase 0 (After loading context)

---

## Common Patterns

### Pattern 1: The Three-Source Approach

Combine Archon with other sources for comprehensive research:

```
1. Archon → Past patterns and gotchas
2. Context7 → Latest official documentation
3. Local grep → THIS project's patterns
```

**Example: Implementing Redis caching**

```python
# Step 1: Query Archon for patterns
mcp__archon__rag_search_code_examples(
    query="Redis cache FastAPI",
    match_count=3
)
# → Learn: Use connection pooling, handle reconnection

# Step 2: Get latest Redis-py docs
mcp__context7__get-library-docs(
    context7CompatibleLibraryID="/redis/redis-py",
    topic="connection pooling"
)
# → Learn: Current API signatures

# Step 3: Grep THIS codebase
grep -r "redis" --include="*.py" .
# → Learn: Project-specific configuration
```

### Pattern 2: Iterative Refinement

Start broad, then narrow based on results:

```python
# Start broad
results = mcp__archon__rag_search_knowledge_base(
    query="authentication",
    match_count=5
)

# Review results, then refine
results = mcp__archon__rag_search_code_examples(
    query="JWT token validation",  # More specific
    match_count=3
)
```

### Pattern 3: Gotcha Prevention

Query for known issues BEFORE implementing:

```python
# Before database migration
mcp__archon__rag_search_knowledge_base(
    query="PostgreSQL migration pitfalls",
    match_count=5
)

# Before async implementation
mcp__archon__rag_search_knowledge_base(
    query="async await gotchas Python",
    match_count=5
)
```

---

## Troubleshooting

### "No relevant results found"

**Possible causes:**
1. **Query too specific** - Broaden your query
   - Instead of: `"FastAPI OAuth2 JWT with refresh tokens"`
   - Try: `"FastAPI authentication"`

2. **Feature too new** - No past implementations
   - Use Context7 or WebSearch instead

3. **Wrong terminology** - Try alternative terms
   - Instead of: `"caching"`
   - Try: `"cache"` or `"Redis"`

### "Results not relevant to my use case"

**Solutions:**
1. **Refine query** - Add technology name
   - Instead of: `"authentication"`
   - Try: `"FastAPI authentication"`

2. **Filter by source** - If Archon supports source filtering
   ```python
   mcp__archon__rag_search_knowledge_base(
       query="authentication",
       source_id="backend-projects-source"  # If available
   )
   ```

3. **Increase match_count** - See more diverse results
   ```python
   match_count=10  # Instead of 5
   ```

### "Archon tools not available"

**Check:**
1. `.auto-claude/.env` has `ARCHON_MCP_ENABLED=true`
2. Archon MCP server is running at configured URL
3. Agent type is in the allowed list (planner, coder, etc.)

**Fallback:**
- Proceed with grep-based investigation
- Use Context7 for documentation
- All prompts are designed to work without Archon

### "Query taking too long"

**Solutions:**
1. **Reduce match_count** - Fewer results = faster
2. **Shorten query** - Fewer keywords = faster search
3. **Check Archon server** - May be overloaded

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ ARCHON QUICK REFERENCE                                  │
├─────────────────────────────────────────────────────────┤
│ QUERY LENGTH:  2-5 keywords max                         │
│ MATCH COUNT:   3 (examples) or 5 (patterns)             │
│                                                          │
│ GOOD QUERY:    "FastAPI middleware"                     │
│ BAD QUERY:     "how to implement middleware in FastAPI" │
│                                                          │
│ USE FOR:       Past patterns, gotchas, examples         │
│ DON'T USE FOR: Latest docs, THIS project's code         │
│                                                          │
│ FALLBACK:      Always works without Archon available    │
└─────────────────────────────────────────────────────────┘
```

---

## Summary

**Key Takeaways:**

1. ✅ **Keep queries SHORT** - 2-5 keywords perform best
2. ✅ **Use strategically** - Supplement, don't replace other research
3. ✅ **Query early** - Before implementing, not after getting stuck
4. ✅ **Combine sources** - Archon + Context7 + Local grep
5. ✅ **Graceful degradation** - Always have a non-Archon fallback

**Remember:** Archon helps you learn from the past, but you still need to adapt patterns to THIS codebase and current requirements.

---

For more information, see:
- [ARCHON_INTEGRATION_PLAN.md](../ARCHON_INTEGRATION_PLAN.md) - Technical implementation details
- Agent prompts in `apps/backend/prompts/` - Context-specific Archon usage

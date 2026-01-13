# Sub-Agent Test Validation Guide

Comprehensive test scenarios for validating Auto-Claude's 5 sub-agents with natural language triggers.

## Overview

This document provides test cases for each sub-agent to verify they respond correctly to natural language triggers. Each test includes trigger phrases, expected behavior, and validation criteria.

---

## 1. Spec Creator Agent

**Agent File:** `.claude/agents/spec-creator-agent.md`
**Skill Integration:** `auto-claude-spec`
**Model:** Sonnet
**CLI Wrapper:** `apps/backend/spec_runner.py`

### Triggers

**Explicit Keywords:**
- `create spec`
- `new specification`
- `define feature`
- `spec creation`
- `requirements gathering`

**Description (Implicit):**
"Creates feature specifications through multi-phase discovery process. PROACTIVELY use when user wants to define a new feature, enhancement, or bug fix."

### Test Cases

#### Test 1.1: Simple Feature Request
**User Input:**
```
"Create a spec for adding a dark mode toggle"
```

**Expected Behavior:**
- Claude recognizes spec creation intent
- Delegates to spec-creator-agent OR executes directly
- Agent asks whether to use interactive mode or quick mode
- Agent executes: `cd apps/backend && python spec_runner.py --task "adding a dark mode toggle"`
- Agent reports complexity assessment (likely SIMPLE)
- Agent shows discovery phases in progress

**Validation Criteria:**
- ✅ Agent starts spec_runner.py
- ✅ Spec created in `.auto-claude/specs/NNN-dark-mode/`
- ✅ spec.md contains acceptance criteria
- ✅ No errors in execution

#### Test 1.2: Interactive Mode Request
**User Input:**
```
"I want to create a new spec interactively"
```

**Expected Behavior:**
- Agent recognizes interactive mode preference
- Agent executes: `python spec_runner.py --interactive`
- Agent guides user through question-answer flow
- Agent collects requirements step-by-step

**Validation Criteria:**
- ✅ Interactive mode activated
- ✅ Agent asks clarifying questions
- ✅ Spec created with user inputs

#### Test 1.3: Complex Feature Request
**User Input:**
```
"Define a new feature for implementing real-time collaborative editing with WebSockets and CRDT conflict resolution"
```

**Expected Behavior:**
- Agent recognizes complex feature
- Agent executes spec_runner.py with task description
- Agent assesses as COMPLEX (8 phases)
- Agent includes Research phase for WebSocket and CRDT patterns

**Validation Criteria:**
- ✅ Complexity correctly assessed as COMPLEX
- ✅ Research phase executed
- ✅ spec.md includes technical details on WebSockets and CRDT

---

## 2. Autonomous Builder Agent

**Agent File:** `.claude/agents/autonomous-builder-agent.md`
**Skill Integration:** `auto-claude-build`
**Model:** Sonnet
**CLI Wrapper:** `apps/backend/run.py`

### Triggers

**Explicit Keywords:**
- `autonomous build`
- `run auto-claude`
- `implement spec`
- `build feature`
- `start build`

**Description (Implicit):**
"Executes autonomous builds using Auto-Claude's multi-phase implementation pipeline. PROACTIVELY use when user wants to implement a spec, build a feature, or run autonomous development."

### Test Cases

#### Test 2.1: Simple Build Request
**User Input:**
```
"Build spec 001 autonomously"
```

**Expected Behavior:**
- Claude recognizes build intent
- Delegates to autonomous-builder-agent
- Agent executes: `cd apps/backend && python run.py --spec 001`
- Agent reports progress through phases:
  - Planning (creates subtasks)
  - Coding (implements subtasks)
  - QA (validates acceptance criteria)
- Agent reports success/failure with summary

**Validation Criteria:**
- ✅ Build starts in isolated worktree
- ✅ All phases execute (plan → code → QA)
- ✅ Changes isolated in `.worktrees/001-spec-name/`
- ✅ No modifications to main project

#### Test 2.2: Build with Review
**User Input:**
```
"Implement spec 002 and then let me review it"
```

**Expected Behavior:**
- Agent executes build
- After completion, agent suggests: `python run.py --spec 002 --review`
- Agent guides user to worktree location for testing

**Validation Criteria:**
- ✅ Build completes successfully
- ✅ Review instructions provided
- ✅ Worktree location clearly stated

#### Test 2.3: Resume Failed Build
**User Input:**
```
"Run auto-claude on spec 003, it failed last time during QA"
```

**Expected Behavior:**
- Agent recognizes previous failure context
- Agent executes build from last checkpoint
- Agent may check QA report from previous run
- Agent continues where it left off

**Validation Criteria:**
- ✅ Agent resumes from correct checkpoint
- ✅ Previous failure context considered
- ✅ QA issues from previous run addressed

---

## 3. QA Loop Agent

**Agent File:** `.claude/agents/qa-loop-agent.md`
**Skill Integration:** Invoked by `auto-claude-build` or directly
**Model:** Sonnet
**CLI Wrapper:** `apps/backend/run.py --qa`

### Triggers

**Explicit Keywords:**
- `run qa`
- `run QA`
- `validate build`
- `test spec`
- `qa validation`
- `quality assurance`

**Description (Implicit):**
"Quality assurance validation and fix loop coordination. PROACTIVELY use when user wants to validate a build, run QA manually, or resolve QA issues."

### Test Cases

#### Test 3.1: Manual QA Request
**User Input:**
```
"Run QA on spec 001"
```

**Expected Behavior:**
- Claude delegates to qa-loop-agent
- Agent executes: `python run.py --spec 001 --qa`
- Agent runs qa_reviewer to validate acceptance criteria
- Agent generates qa_report.md
- If failures: Agent runs qa_fixer in loop until resolved

**Validation Criteria:**
- ✅ QA reviewer executes
- ✅ qa_report.md created
- ✅ If failures detected, fix loop activates
- ✅ Final status (PASS/FAIL) reported

#### Test 3.2: Validate After Manual Changes
**User Input:**
```
"I made some changes to the code, validate the build now"
```

**Expected Behavior:**
- Agent recognizes need for re-validation
- Agent executes QA on current spec
- Agent checks acceptance criteria against current code state

**Validation Criteria:**
- ✅ QA runs on current code state
- ✅ Results reflect manual changes
- ✅ Clear pass/fail status

#### Test 3.3: QA with E2E Testing
**User Input:**
```
"Test spec 004 (frontend changes) with E2E validation"
```

**Expected Behavior:**
- Agent recognizes frontend changes
- Agent uses Electron MCP tools for E2E testing (if enabled)
- Agent validates UI interactions, not just code

**Validation Criteria:**
- ✅ E2E testing performed (if Electron app running)
- ✅ UI validation included in QA report
- ✅ Screenshots captured for visual confirmation

---

## 4. Archon Sync Agent

**Agent File:** `.claude/agents/archon-sync-agent.md`
**Skill Integration:** `archon`
**Model:** Haiku
**Tools:** `[Read, Glob, Grep, Write, mcp__archon__*]`

### Triggers

**Explicit Keywords:**
- `sync to archon`
- `sync archon`
- `update archon`
- `archon sync`
- `store insights`
- `archon project`

**Description (Implicit):**
"Synchronizes Auto-Claude specs, tasks, and insights with Archon for cross-session learning and project tracking. PROACTIVELY use when user wants to sync to archon, update project tracking, or store session insights."

### Test Cases

#### Test 4.1: Sync New Spec
**User Input:**
```
"Sync spec 001 to Archon"
```

**Expected Behavior:**
- Claude delegates to archon-sync-agent
- Agent reads spec.md and implementation_plan.json
- Agent creates Archon project
- Agent creates Archon tasks from subtasks
- Agent stores spec.md as document
- Agent saves project ID to `.archon_project_id`

**Validation Criteria:**
- ✅ Archon project created
- ✅ Project ID saved locally
- ✅ Tasks created in Archon
- ✅ Spec document stored

#### Test 4.2: Update Task Status
**User Input:**
```
"Update Archon task status for completed subtasks in spec 002"
```

**Expected Behavior:**
- Agent reads implementation_plan.json
- Agent updates task status in Archon for completed subtasks
- Agent reports sync summary

**Validation Criteria:**
- ✅ Task statuses updated in Archon
- ✅ Sync summary provided
- ✅ No duplicate tasks created

#### Test 4.3: Store Session Insights
**User Input:**
```
"Store the insights from this build session to Archon"
```

**Expected Behavior:**
- Agent extracts insights from Graphiti memory
- Agent creates Archon document with insights
- Agent tags for discoverability
- Agent confirms storage

**Validation Criteria:**
- ✅ Insights extracted from session
- ✅ Document created in Archon
- ✅ Proper tags applied
- ✅ Searchable via RAG

---

## 5. Session Analytics Agent

**Agent File:** `.claude/agents/session-analytics-agent.md`
**Skill Integration:** `observability`
**Model:** Haiku
**Tools:** `[Read, Glob, Grep, Bash]`

### Triggers

**Explicit Keywords:**
- `analyze session`
- `session costs`
- `cost tracking`
- `detect patterns`
- `investigate failure`
- `session performance`
- `session analytics`
- `loop detection`
- `failure analysis`

**Description (Implicit):**
"Analyzes Auto-Claude session data for cost tracking, performance metrics, pattern detection, and failure investigation. PROACTIVELY use when user wants to analyze costs, detect patterns, investigate failures, or review session performance."

### Test Cases

#### Test 5.1: Cost Analysis
**User Input:**
```
"How much did spec 001 cost to build?"
```

**Expected Behavior:**
- Claude delegates to session-analytics-agent
- Agent executes: `sfa_session_cost_tracker_anthropic_v1.py --spec-id 001`
- Agent parses events database
- Agent provides cost breakdown by phase
- Agent compares to average costs

**Validation Criteria:**
- ✅ Cost report generated
- ✅ Breakdown by phase (planner, coder, QA)
- ✅ Token usage shown (input/output)
- ✅ Comparison to averages included

#### Test 5.2: Pattern Detection
**User Input:**
```
"Did we hit any loops during the last build?"
```

**Expected Behavior:**
- Agent executes: `sfa_loop_detector_report_anthropic_v1.py`
- Agent analyzes recent sessions for loop patterns
- Agent reports detected loops with severity
- Agent provides prevention tips

**Validation Criteria:**
- ✅ Loop detection executed
- ✅ Patterns identified (if any)
- ✅ Severity assessment provided
- ✅ Prevention recommendations included

#### Test 5.3: Failure Investigation
**User Input:**
```
"Why did spec 003 fail during QA?"
```

**Expected Behavior:**
- Agent finds failed session ID
- Agent executes: `sfa_failure_investigator_anthropic_v1.py --session-id <id>`
- Agent provides failure timeline
- Agent shows root cause hypothesis
- Agent suggests recovery steps

**Validation Criteria:**
- ✅ Failed session identified
- ✅ Failure timeline constructed
- ✅ Root cause analysis provided
- ✅ Recovery steps suggested

#### Test 5.4: Performance Comparison
**User Input:**
```
"Compare spec 004 performance to previous builds"
```

**Expected Behavior:**
- Agent executes: `sfa_events_analyzer_anthropic_v1.py` with comparison query
- Agent provides metrics table (duration, tokens, cost, success rate)
- Agent identifies positives and concerns
- Agent provides recommendations

**Validation Criteria:**
- ✅ Comparison metrics generated
- ✅ Trend analysis included
- ✅ Actionable recommendations provided

#### Test 5.5: Weekly Summary
**User Input:**
```
"Give me a summary of all builds from the past week"
```

**Expected Behavior:**
- Agent queries events database for 7-day period
- Agent generates comprehensive report:
  - Total specs, sessions, success rate, cost
  - Phase-by-phase breakdown
  - Highlights and issues
  - Trends and recommendations

**Validation Criteria:**
- ✅ Weekly summary report generated
- ✅ All key metrics included
- ✅ Trends identified
- ✅ Actionable recommendations provided

---

## Integration Testing

### Cross-Agent Workflows

#### Workflow 1: Full Spec-to-Build-to-Sync Pipeline
**Test Scenario:**
```
User: "Create a spec for user profile page"
→ spec-creator-agent creates spec

User: "Build it autonomously"
→ autonomous-builder-agent executes build

User: "Sync everything to Archon"
→ archon-sync-agent syncs spec, tasks, insights
```

**Validation:**
- ✅ All 3 agents execute in sequence
- ✅ Data flows between agents correctly
- ✅ No duplicate work or conflicts

#### Workflow 2: Build → QA Failure → Analytics → Fix
**Test Scenario:**
```
User: "Implement spec 005"
→ autonomous-builder-agent runs, QA fails

User: "Why did the build fail?"
→ session-analytics-agent investigates failure

User: "Run QA again after I fix the issue"
→ qa-loop-agent re-validates
```

**Validation:**
- ✅ Failure properly detected
- ✅ Analytics provides actionable insights
- ✅ Re-validation works correctly

---

## Testing Checklist

### Pre-Testing Setup
- [ ] Python 3.12+ installed
- [ ] UV installed for SFA execution
- [ ] Backend dependencies installed (`uv pip install -r requirements.txt`)
- [ ] ANTHROPIC_API_KEY configured
- [ ] Graphiti memory configured
- [ ] Archon MCP enabled (optional, for sync tests)
- [ ] Events database exists (`.auto-claude/events.db`)

### Agent Trigger Tests
- [ ] Spec Creator: Responds to "create a spec for X"
- [ ] Spec Creator: Responds to "new specification for Y"
- [ ] Autonomous Builder: Responds to "build spec NNN"
- [ ] Autonomous Builder: Responds to "implement this autonomously"
- [ ] QA Loop: Responds to "run QA on spec NNN"
- [ ] QA Loop: Responds to "validate the build"
- [ ] Archon Sync: Responds to "sync to archon"
- [ ] Archon Sync: Responds to "update archon tasks"
- [ ] Session Analytics: Responds to "analyze session costs"
- [ ] Session Analytics: Responds to "investigate failure"

### Integration Tests
- [ ] Spec creation → Build execution flow works
- [ ] Build completion → Archon sync works
- [ ] Build failure → Analytics investigation works
- [ ] QA failure → Fix loop → Re-validation works
- [ ] Analytics → Store insights in Archon works

### UX Validation
- [ ] Trigger phrases feel natural
- [ ] Agent responses are clear and helpful
- [ ] Progress reporting is informative
- [ ] Error messages are actionable
- [ ] Handoffs between agents are smooth

---

## Known Issues & Improvements

### Current Limitations
1. **SFAs Not Yet Implemented**: Some observability SFAs referenced but not yet created
   - `sfa_session_cost_tracker_anthropic_v1.py` - TODO
   - `sfa_loop_detector_report_anthropic_v1.py` - TODO
   - `sfa_failure_investigator_anthropic_v1.py` - TODO
   - `sfa_events_analyzer_anthropic_v1.py` - TODO

2. **Events Database**: Not yet populated with session data
   - Need to implement events tracking in core/client.py
   - Database schema needs to be created

3. **Archon Sync**: Requires Archon MCP server running
   - Optional dependency, some users may not have it
   - Need graceful fallback if unavailable

### Suggested Improvements
1. **Trigger Expansion**: Add more natural language variations
   - "start building X" → autonomous-builder-agent
   - "how's the cost looking?" → session-analytics-agent
   - "check if it passes QA" → qa-loop-agent

2. **Context Awareness**: Agents should detect context from conversation
   - If spec was just created, "build it" should use that spec
   - If build just failed, "analyze it" should investigate that failure

3. **Progress Indicators**: Add real-time progress updates
   - "Phase 2/8: Requirements gathering..."
   - "Subtask 3/12: Implementing authentication..."

4. **Error Recovery**: Better handling of partial failures
   - Resume from checkpoints
   - Clear recovery instructions
   - Automatic retry logic for transient errors

---

## Test Execution Log

Use this section to record test results:

### Test Date: YYYY-MM-DD
**Tester:** [Name]
**Environment:** [OS, Python version, etc.]

| Test Case | Status | Notes |
|-----------|--------|-------|
| 1.1 - Simple Feature | ⏳ | Not yet tested |
| 1.2 - Interactive Mode | ⏳ | Not yet tested |
| 1.3 - Complex Feature | ⏳ | Not yet tested |
| 2.1 - Simple Build | ⏳ | Not yet tested |
| 2.2 - Build with Review | ⏳ | Not yet tested |
| 2.3 - Resume Failed Build | ⏳ | Not yet tested |
| 3.1 - Manual QA | ⏳ | Not yet tested |
| 3.2 - Validate After Changes | ⏳ | Not yet tested |
| 3.3 - QA with E2E | ⏳ | Not yet tested |
| 4.1 - Sync New Spec | ⏳ | Not yet tested |
| 4.2 - Update Task Status | ⏳ | Not yet tested |
| 4.3 - Store Insights | ⏳ | Not yet tested |
| 5.1 - Cost Analysis | ⏳ | Not yet tested |
| 5.2 - Pattern Detection | ⏳ | Not yet tested |
| 5.3 - Failure Investigation | ⏳ | Not yet tested |
| 5.4 - Performance Comparison | ⏳ | Not yet tested |
| 5.5 - Weekly Summary | ⏳ | Not yet tested |

**Overall Status:** ⏳ Pending Testing
**Critical Issues:** None yet
**Recommendations:** Test with real Auto-Claude sessions to validate

---

## Conclusion

This validation guide provides comprehensive test scenarios for all 5 Auto-Claude sub-agents. Once testing is complete, update the test log and document any issues or UX improvements in the "Known Issues & Improvements" section.

**Next Steps:**
1. Execute test cases in actual Claude Code sessions
2. Document results in Test Execution Log
3. File issues for any failures or UX concerns
4. Update agent definitions based on learnings
5. Create user-facing documentation highlighting successful patterns

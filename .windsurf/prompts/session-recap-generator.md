---
title: Session Recap Generator Prompt
description: AI prompt for generating end-of-session/day development work summaries
created: 2025-12-08
tags: [prompt, session-recap, development-workflow]
---

# Session Recap Generator Prompt

Use this prompt at the end of a development session/day/iteration to generate a comprehensive recap of your work.

## How to Use

1. Run the git log command to capture recent commits
2. Copy the commit history into the prompt below
3. Paste any additional context (open issues, current branch, test results, etc.)
4. Run the prompt with your AI assistant

## The Prompt

```
You are a development work summarizer. Your job is to create a clear, actionable recap of development work from git commits and project context.

## Context

I'm working on an InnerOS Zettelkasten project - an AI-powered note-taking and automation system.

Recent git commits (last 2 days):
[PASTE GIT LOG HERE]

Current development context:
- Active branch: [CURRENT BRANCH]
- Open issues: [ANY OPEN ISSUES]
- Test results: [PASS/FAIL COUNTS]
- Current focus: [WHAT YOU'RE WORKING ON]

## Task

Generate a comprehensive session recap that includes:

### 1. **Work Summary (2-3 sentences)**
   - What was accomplished in this session/day
   - Key deliverables or milestones reached
   - Overall progress toward sprint goals

### 2. **TDD Iterations Completed**
   For each TDD iteration (RED → GREEN → REFACTOR):
   - Iteration name/number
   - What tests were added (RED phase)
   - What implementation was done (GREEN phase)
   - What was refactored (REFACTOR phase)
   - Test results (X/Y passing, any regressions)
   - Key learning or insight

### 3. **Features Implemented**
   - List each feature with:
     - Feature name
     - Files changed
     - Lines of code added
     - Status (complete, in-progress, blocked)

### 4. **Bugs Fixed**
   - Bug description
   - Root cause
   - Solution applied
   - How it was validated

### 5. **Documentation Added**
   - What documentation was created/updated
   - Purpose and audience
   - Location in repo

### 6. **Test Coverage Impact**
   - Total tests added
   - Total tests passing
   - Any regressions or failures
   - Coverage areas (unit, integration, E2E)

### 7. **Architecture Decisions Made**
   - Any new patterns introduced
   - Any existing patterns reinforced
   - Rationale for decisions
   - Impact on future development

### 8. **Next Steps (P0/P1/P2 Priority)**
   - P0 (blocking): What must be done next
   - P1 (high): What should be done soon
   - P2 (nice-to-have): What could be done later
   - Dependencies or blockers

### 9. **Key Metrics**
   - Session duration (estimate)
   - Commits made
   - Files changed
   - Tests added
   - Code quality (any lint issues, regressions)

### 10. **Lessons Learned**
   - What worked well
   - What was challenging
   - Patterns to repeat
   - Anti-patterns to avoid
   - Insights for future iterations

## Output Format

Use clear markdown with:
- Bold headers for sections
- Bullet points for lists
- Code blocks for technical details
- Tables for metrics
- Links to relevant files or commits when possible

## Tone

- Professional but conversational
- Highlight wins and progress
- Be honest about challenges
- Focus on actionable insights
- Avoid jargon where possible
```

## Example Output Structure

```markdown
# Session Recap: Smart Link Performance & Cache Validation (Dec 8, 2025)

## Work Summary
Completed TDD Iteration 4 for Smart Link automation, adding performance instrumentation and cache validation. All 9 new tests passing with zero regressions. Ready for P1 review queue integration.

## TDD Iterations Completed

### TDD Iteration 4: Smart Link Performance & Cache Instrumentation
**RED Phase**: 9 tests for performance tracking
- test_process_note_returns_timing_metrics
- test_process_note_returns_cache_metrics
- test_second_run_shows_cache_improvement
- test_integrator_accepts_metrics_tracker
- test_integrator_metrics_available_for_health_check
- (+ 4 more ProcessingMetricsTracker tests)

**GREEN Phase**: Minimal implementation
- Added time.perf_counter() timing
- Added cache_metrics dict to results
- Added optional metrics_tracker parameter
- Added get_performance_metrics() method

**REFACTOR Phase**: Documentation
- Updated docstrings
- Consistent naming with ProcessingMetricsTracker

**Results**: 9/9 tests passing, 31 existing handler tests passing, zero regressions

## Features Implemented
- **Performance Instrumentation**: Processing time tracking in milliseconds
- **Cache Metrics**: Hit/miss/embedding operation counts
- **Health Check Integration**: get_performance_metrics() for daemon monitoring
- **Metrics Tracker Integration**: Optional ProcessingMetricsTracker parameter

## Test Coverage Impact
- Tests added: 9
- Tests passing: 40 (9 new + 31 existing)
- Coverage areas: Unit (performance), Integration (handler), E2E (daemon)
- Regressions: 0

## Next Steps
**P0**: Implement suggestion review queue adapter for .automation/review_queue/links/
**P1**: Add JSONL parsing helper for suggestion entries
**P2**: Incremental corpus updates, background embedding indexer

## Key Metrics
- Session duration: ~25 minutes
- Commits: 2
- Files changed: 2
- Lines added: ~60
- Test execution time: 0.09s
```

## Tips for Better Recaps

1. **Run this immediately after work** - Details are fresh
2. **Include test output** - Paste actual test results
3. **Link to commits** - Reference specific commit hashes
4. **Note blockers** - Call out anything preventing progress
5. **Celebrate wins** - Highlight what went well
6. **Be specific** - Use file names, function names, line counts
7. **Connect to goals** - Relate work back to sprint/project goals
8. **Include metrics** - Time spent, tests added, coverage impact

## Customization

Adapt this prompt for your specific project by:
- Changing project name and description
- Adding custom sections relevant to your work
- Adjusting priority levels (P0/P1/P2)
- Including team-specific metrics
- Adding links to your project management tools

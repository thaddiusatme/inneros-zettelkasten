---
title: Windsurf Prompts Directory
description: AI prompts for development workflows
created: 2025-12-08
---

# Windsurf Prompts Directory

Collection of AI prompts optimized for development workflows in this project.

## Available Prompts

### 1. Session Recap Generator
**File**: `session-recap-generator.md`  
**Purpose**: Generate comprehensive end-of-session/day development work summaries  
**When to use**: At the end of a development session, day, or sprint iteration

**Quick Start**:
```bash
# 1. Get recent git commits
cd /Users/thaddius/repos/inneros-zettelkasten
git log --oneline -20

# 2. Open the prompt template
cat .windsurf/prompts/session-recap-generator.md

# 3. Fill in the [PASTE GIT LOG HERE] section with your commits
# 4. Add any additional context (branch, issues, test results)
# 5. Run with your AI assistant

# 6. Review the generated recap
# 7. Save to Projects/ACTIVE/ or root directory as SESSION-RECAP-YYYY-MM-DD.md
```

**Output**: Comprehensive markdown document with:
- Work summary
- TDD iterations completed
- Features implemented
- Bugs fixed
- Documentation added
- Test coverage impact
- Architecture decisions
- Next steps (P0/P1/P2)
- Key metrics
- Lessons learned

**Example Output**: See `SESSION-RECAP-2025-12-08-SMART-LINK-PERF.md` in repo root

## How to Use These Prompts

### Option 1: Copy-Paste (Simplest)
1. Open the prompt file in your editor
2. Copy the entire prompt text
3. Paste into your AI assistant (Claude, ChatGPT, etc.)
4. Fill in the bracketed sections with your specific context
5. Run and review the output

### Option 2: Command-Line (Fastest)
```bash
# Display prompt in terminal
cat .windsurf/prompts/session-recap-generator.md

# Copy to clipboard (macOS)
cat .windsurf/prompts/session-recap-generator.md | pbcopy

# Then paste into your AI assistant
```

### Option 3: IDE Integration
If using an IDE with AI assistant integration:
1. Open the prompt file in your IDE
2. Select all text
3. Send to AI assistant via IDE command
4. Fill in context sections
5. Review output

## Customizing Prompts

Each prompt is designed to be customizable. Common customizations:

### Change Project Context
Find this section in the prompt:
```
I'm working on an InnerOS Zettelkasten project - an AI-powered note-taking and automation system.
```

Replace with your project description.

### Add Custom Sections
Add new sections to the task list:
```
### 11. **Custom Metric Name**
   - Description of what to include
   - How to measure it
   - Why it matters
```

### Adjust Priority Levels
Change P0/P1/P2 to match your workflow:
- P0 = Blocking/Critical
- P1 = High Priority
- P2 = Nice-to-Have

Or use your own system (Critical/Important/Backlog, etc.)

## Tips for Best Results

### 1. Provide Complete Context
The more context you provide, the better the output:
- Full git log (not just commit messages)
- Current branch name
- Open issues or blockers
- Test results
- What you're currently working on

### 2. Be Specific About Scope
Specify the time period:
- "Last 2 hours of work"
- "Today's development"
- "This sprint iteration"
- "Last 2 days"

### 3. Include Test Results
Provide actual test output:
```
Test Results: 40/40 passing
- 9 new tests added
- 31 existing tests passing
- 0 regressions
- 0.09s execution time
```

### 4. Link to Commits
Reference specific commits:
```
Commits:
- a7c9330: feat(smart-link): Add performance & cache instrumentation
- 5115a30: docs: Add TDD Iteration 4 lessons learned
```

### 5. Note Any Blockers
Call out anything preventing progress:
```
Blockers:
- Waiting for API key for external service
- Dependency version conflict in requirements.txt
- Test environment setup incomplete
```

## Example Workflow

Here's how to use the Session Recap Generator in your daily workflow:

### Morning (Start of Session)
```bash
# Check current branch
git branch

# See recent work
git log --oneline -5
```

### End of Session
```bash
# Get all commits since start of day
git log --since="8 hours ago" --oneline

# Get all commits for this iteration
git log --grep="TDD Iter" --oneline

# Generate recap
cat .windsurf/prompts/session-recap-generator.md
# ... fill in context and run with AI assistant
```

### Save the Output
```bash
# Save to repo root with date
cp SESSION-RECAP-2025-12-08-SMART-LINK-PERF.md SESSION-RECAP-$(date +%Y-%m-%d).md

# Or save to Projects/ACTIVE/
cp SESSION-RECAP-2025-12-08-SMART-LINK-PERF.md Projects/ACTIVE/session-recap-$(date +%Y-%m-%d).md

# Commit to git
git add SESSION-RECAP-*.md
git commit -m "docs: Add session recap for $(date +%Y-%m-%d)"
```

## Prompt Maintenance

### When to Update Prompts
- When you discover a new useful section to include
- When your project structure changes
- When you want to track new metrics
- When you find a better way to phrase instructions

### How to Update
1. Edit the `.md` file in `.windsurf/prompts/`
2. Test the updated prompt with a real session
3. Commit changes: `git commit -m "docs(prompts): Update session-recap-generator"`
4. Document the change in this README

### Version Control
Keep prompts in git so you can:
- Track improvements over time
- Revert to previous versions if needed
- Share with team members
- Review prompt evolution

## Related Documentation

- **TDD Methodology**: See `.windsurf/guides/tdd-methodology-patterns.md`
- **AI Integration Patterns**: See `.windsurf/guides/ai-integration-patterns.md`
- **Development Workflow**: See `.windsurf/rules/updated-development-workflow.md`

## Troubleshooting

### Prompt is too long
- The AI assistant has token limits
- Try splitting into multiple prompts
- Focus on most recent commits (last 20 instead of 50)
- Remove verbose commit messages

### Output is too generic
- Provide more specific context
- Include actual test output
- Reference specific files and functions
- Mention blockers and challenges

### Missing important details
- Add custom sections to the prompt
- Provide more git history
- Include links to related issues/PRs
- Mention architectural decisions

## Contributing

To improve these prompts:
1. Use them in your workflow
2. Note what works well and what doesn't
3. Experiment with variations
4. Document improvements
5. Update the prompt files with better versions

---

**Last Updated**: 2025-12-08  
**Prompts Available**: 1 (Session Recap Generator)  
**Status**: Active and maintained

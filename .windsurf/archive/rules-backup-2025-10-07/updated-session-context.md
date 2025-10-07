# Session Context & Core Principles

> **Purpose**: Session management, required reads, and critical path guidance  
> **Updated**: 2025-09-24

## 🎯 Core Session Principles

### Context-First Development
Required Reads (Priority Order):
1. Projects/REFERENCE/inneros-manifest-v3.md - Comprehensive project overview and architecture
2. Projects/ACTIVE/project-todo-v3.md - Current priorities and next development steps  
3. Projects/ACTIVE/current-priorities-summary.md - 2-week focus areas and active projects
4. README.md - Updated project structure and AI features documentation
5. Projects/REFERENCE/windsurf-project-changelog.md - Detailed development history

Session Actions:
- Always ground actions in project context using ACTIVE/ and REFERENCE/ directories
- Check Projects/ACTIVE/ for current priorities before starting development
- Reference completed work in Projects/COMPLETED-2025-XX/ for patterns and lessons
- Consult Projects/DEPRECATED/ only for historical context on superseded approaches
- When in doubt, prioritize ACTIVE manifests over deprecated integration analyses

### Critical Path Management
- Template Processing System: RESOLVED (2025-09-17) - Verify template health in reviews
- Integration-First: New features must leverage existing AI workflows, not duplicate them
- Compatibility: All changes must preserve existing functionality and test coverage
- Performance: Maintain or improve current benchmarks (<10s summarization, <5s similarity)
- Project Organization: Maintain clean ACTIVE/REFERENCE/COMPLETED/DEPRECATED structure

### Data Preservation & Ethics
- Never overwrite or destructively edit notes unless explicitly instructed
- Always retain metadata and maintain complete audit trail
- Backup considerations before any structural changes
- Respect privacy and visibility tags at all times
- Preserve user decision-making in AI workflows
- Confirm destructive actions with user
- Provide rollback options for structural changes

### Workflow Compliance
- Follow note promotion and triage flows as defined in templates and manifest
- Use Templater scripts and LLM/AI integration points as described in manifest
- Respect all privacy and visibility tags (private/shared/team/public)
- Maintain backward compatibility with existing workflows
- Log all major actions in Changelog and notify user
- Follow project lifecycle management: ACTIVE → Implementation → COMPLETED → DEPRECATED

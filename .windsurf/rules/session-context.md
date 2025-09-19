# Session Context & Core Principles

> **Purpose**: Session management, required reads, and critical path guidance  
> **Updated**: 2025-09-18

## 🎯 Core Session Principles

### Context-First Development
Required Reads (Priority Order):
1. Projects/inneros-manifest-v3.md - Comprehensive project overview and architecture
2. Projects/project-todo-v3.md - Current priorities and next development steps  
3. Projects/reading-intake-integration-analysis.md - Integration analysis and solution architecture
4. README.md - Quick start and AI features documentation
5. Projects/windsurf-project-changelog.md - Detailed development history

Session Actions:
- Always ground actions in project context, schema, and requirements
- Summarize project goals, structure, and recent changes before proceeding
- Check for critical bugs and dependencies before starting development
- Reference integration analysis for Phase extension projects
- When in doubt, consult Manifest and Integration Analysis before asking user

### Critical Path Management
- Template Processing System: RESOLVED (2025-09-17) - Verify template health in reviews
- Integration-First: New features must leverage existing AI workflows, not duplicate them
- Compatibility: All changes must preserve existing functionality and test coverage
- Performance: Maintain or improve current benchmarks (<10s summarization, <5s similarity)

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

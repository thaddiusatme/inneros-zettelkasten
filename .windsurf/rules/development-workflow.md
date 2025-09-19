# Development Workflow & Guidelines

> **Purpose**: TDD methodology, integration guidelines, Git standards  
> **Updated**: 2025-09-18

## 🏗️ Development Guidelines

### Critical Path Management
- Template Processing System: RESOLVED (2025-09-17) - Verify template health in reviews
- Always run system health check before beginning work
- Integration projects must preserve existing functionality
- Phase extensions preferred over standalone replacements

### TDD Methodology
- Red → Green → Refactor cycles for all new features
- Maintain 66/66 test coverage (current target)
- Real user data validation before production deployment
- Performance benchmarking against established targets
- Integration testing with existing AI workflows

### Integration-First Development
- Extend vs. Replace: Build on existing Phase 5 AI capabilities
- Schema Compatibility: New metadata fields extend existing ones
- Workflow Preservation: Existing CLI commands must remain functional
- Performance Maintenance: New features cannot degrade existing performance
- Use workflows: `/integration-project-workflow` for Phase extensions

### Code Organization
- CLI Tools: `src/cli/` - User-facing commands and demos
- AI Engine: `src/ai/` - Core AI processing and workflows
- Tests: `tests/` - Comprehensive unit and integration tests
- Templates: `Templates/` - Dynamic content generation (Production Ready)

## 🔗 Git Integration

### Branch Strategy for Integration Projects
- `reading-pipeline-integration-analysis` - Current branch for Reading Intake Pipeline
- `bug-fix/template-processing` - Recommended for critical template bug
- `integration/phase-5-extension` - For Phase extension work

### Commit Standards
- Include change rationale in commit messages
- Reference affected workflow components  
- Maintain backwards compatibility
- Document bug fixes with clear before/after
- Include integration impact assessment

## 🚨 Error Handling & Recovery

### Error Prevention
- Always confirm destructive actions with user
- Provide rollback options for structural changes
- Log errors and recovery steps in Changelog
- Maintain system state consistency

### Recovery Procedures
- Backup validation before structural changes
- Rollback capabilities for all operations
- Error logging with actionable recovery steps
- System state validation and repair

# Development Workflow & Guidelines

> **Purpose**: TDD methodology, integration guidelines, Git standards  
> **Updated**: 2025-09-24

## 🏗️ Development Guidelines

### Critical Path Management
- Template Processing System: RESOLVED (2025-09-17) - Verify template health in reviews
- Always run system health check before beginning work
- Integration projects must preserve existing functionality
- Phase extensions preferred over standalone replacements
- Project Organization: Maintain clean ACTIVE/REFERENCE/COMPLETED/DEPRECATED structure

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
- CLI Tools: `development/src/cli/` - User-facing commands and demos
- AI Engine: `development/src/ai/` - Core AI processing and workflows
- Tests: `development/tests/` - Comprehensive unit and integration tests
- Templates: `knowledge/Templates/` - Dynamic content generation (Production Ready)
- Project Docs: `Projects/ACTIVE/` - Current manifests and specifications

### Project Lifecycle Integration
- New Projects: Start manifests in Projects/ACTIVE/
- Implementation: All code in development/ with connection to ACTIVE/ manifest
- Completion: Archive lessons learned to Projects/COMPLETED-2025-XX/
- Maintenance: Keep essential docs updated in Projects/REFERENCE/

## 🔗 Git Integration

### Branch Strategy for Integration Projects
- `feat/intelligent-tag-management-tdd-iteration-X` - For tag management system development
- `feat/visual-knowledge-capture-mvp` - For mobile workflow implementation
- `bug-fix/image-linking-system` - For critical image linking investigation
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
- Use production-ready DirectoryOrganizer for file operations

### Recovery Procedures
- Backup validation before structural changes
- Rollback capabilities for all operations
- Error logging with actionable recovery steps
- System state validation and repair

## 🎯 Current Development Patterns (September 2025)

### TDD Success Patterns
- **4-Iteration Methodology**: Proven through Smart Link Management and Advanced Tag Enhancement
- **Utility Extraction**: Modular architecture enables rapid development and reusability
- **Real Data Validation**: Testing with production data proves immediate user value
- **Integration Excellence**: Building on existing infrastructure delivers 80% faster development

### Performance Excellence
- **Smart Link Management**: TDD Iteration 4 complete with link insertion system
- **Advanced Tag Enhancement**: 100% suggestion coverage (7.3% → 100% improvement)
- **Fleeting Note Lifecycle**: 1,394 notes/second processing (257x faster than targets)
- **Directory Organization**: Safety-first with comprehensive backup/rollback (17/17 tests)

### AI Integration Patterns
- **WorkflowManager Reuse**: Leveraging existing AI infrastructure for 80% development acceleration
- **CLI Consistency**: Emoji-enhanced interfaces with export functionality
- **Quality Scoring**: Realistic 0-1 assessment with actionable feedback
- **Connection Discovery**: Semantic similarity with relationship analysis

## 📊 Quality Assurance

### Pre-Development Checklist
- [ ] Review Projects/ACTIVE/ for current priorities
- [ ] Verify all existing tests pass (66/66 target)
- [ ] Check Projects/COMPLETED-2025-XX/ for similar patterns
- [ ] Confirm integration opportunities with existing systems
- [ ] Validate performance benchmarks are maintained

### Development Validation
- [ ] TDD methodology followed (RED → GREEN → REFACTOR)
- [ ] Real user data testing completed
- [ ] Performance targets met or exceeded
- [ ] Integration with existing workflows verified
- [ ] Documentation updated to reflect changes

### Completion Checklist
- [ ] Lessons learned documented and archived
- [ ] Project manifests updated or moved to DEPRECATED/
- [ ] Essential documentation moved to REFERENCE/
- [ ] Git commit includes comprehensive change description
- [ ] Next development priorities updated in ACTIVE/

## 🔄 Maintenance Guidelines

### Monthly Review Process
1. **Review ACTIVE/**: Identify completed projects and stale manifests
2. **Archive Lessons**: Move TDD lessons learned to appropriate COMPLETED-2025-XX/
3. **Update References**: Ensure REFERENCE/ reflects current system capabilities
4. **Clean Deprecated**: Verify DEPRECATED/ contains only historical context
5. **Validate Tests**: Ensure test coverage maintains 66/66 target

### Project Health Indicators
- **ACTIVE/ Size**: ≤10 files (current priority projects)
- **Test Coverage**: 66/66 tests passing consistently
- **Performance**: All AI workflows meet established benchmarks
- **Documentation**: REFERENCE/ contains up-to-date essential docs
- **Integration**: New features build on existing infrastructure

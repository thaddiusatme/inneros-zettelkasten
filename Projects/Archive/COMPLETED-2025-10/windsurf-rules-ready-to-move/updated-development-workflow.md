# Development Workflow & Guidelines

> **Purpose**: TDD methodology, integration guidelines, Git standards  
> **Updated**: 2025-10-05 (Added architectural safeguards)

## 🏗️ Development Guidelines

### Critical Path Management
- Template Processing System: RESOLVED (2025-09-17) - Verify template health in reviews
- Always run system health check before beginning work
- Integration projects must preserve existing functionality
- Phase extensions preferred over standalone replacements
- Project Organization: Maintain clean ACTIVE/REFERENCE/COMPLETED/DEPRECATED structure
- **Architectural Health**: Check class sizes before adding features (see Architectural Constraints)

### TDD Methodology

#### Core Principles
- Red → Green → Refactor cycles for all new features
- Maintain 66/66 test coverage (current target)
- Real user data validation before production deployment
- Performance benchmarking against established targets
- Integration testing with existing AI workflows
- **Architectural testing**: Prevent god classes through size constraints

#### TDD with Architectural Safeguards

**RED Phase - Architectural Checks**

BEFORE writing failing tests for new features:

**Step 1: Target Class Assessment**
```bash
# Check current size
wc -l development/src/ai/target_class.py

# Check method count
grep -c "^    def " development/src/ai/target_class.py

# Check coupling
grep -r "from.*target_class import" development/ | wc -l
```

**Step 2: Decision Point**

If >400 LOC or >15 methods:
- ❌ DO NOT add to existing class
- ✅ Propose extracting utility class FIRST
- ✅ OR propose new manager class
- ✅ Document decision in iteration plan

If <400 LOC and <15 methods:
- ✅ Proceed with feature addition
- 📝 Document: "Adding to [ClassName] (current: XXX LOC, XX methods)"

**Step 3: Write Architectural Test**

Always include:
```python
def test_[class]_size_constraint():
    """Prevent god class - fail if too large."""
    from pathlib import Path
    
    source = Path("src/ai/[class].py").read_text()
    loc = len(source.split('\n'))
    methods = source.count('\n    def ')
    
    assert loc < 500, f"[Class] too large: {loc} LOC (max 500)"
    assert methods < 20, f"[Class] too many methods: {methods} (max 20)"
```

**GREEN Phase - Size Monitoring**

AFTER implementing to pass tests:

1. **Re-check class size** (may have grown during implementation)
   ```bash
   wc -l development/src/ai/target_class.py
   ```

2. **If exceeded threshold**:
   - Extract utilities immediately
   - Update tests for new architecture
   - DO NOT commit bloated class

3. **If approaching threshold** (>400 LOC):
   - Add TODO comment: `# TODO: Extract [domain] logic to utility class (approaching 500 LOC limit)`
   - Create refactoring ticket
   - Schedule extraction within 2 iterations

**REFACTOR Phase - Mandatory Architecture Review**

AFTER passing tests, BEFORE committing:

Checklist:
- [ ] Class size within limits (<500 LOC, <20 methods)
- [ ] Single responsibility maintained
- [ ] If >3 helpers added: Extract to utility class
- [ ] If responsibilities mixed: Consider domain separation
- [ ] Architectural tests passing
- [ ] ADR updated if architectural decisions made

**Utility Extraction Pattern**

If added >3 helper methods:

```python
# BEFORE (in main class)
class WorkflowManager:
    def process_note(self):
        result = self._helper1()
        result = self._helper2()
        result = self._helper3()
        return result
    
    def _helper1(self): ...
    def _helper2(self): ...
    def _helper3(self): ...

# AFTER (extracted to utility)
# File: workflow_manager_utils.py
class WorkflowProcessorUtils:
    @staticmethod
    def helper1(): ...
    
    @staticmethod
    def helper2(): ...
    
    @staticmethod
    def helper3(): ...

# File: workflow_manager.py
from .workflow_manager_utils import WorkflowProcessorUtils

class WorkflowManager:
    def process_note(self):
        result = WorkflowProcessorUtils.helper1()
        result = WorkflowProcessorUtils.helper2()
        result = WorkflowProcessorUtils.helper3()
        return result
```

**Post-Iteration Review**

Required questions:

1. **Size**: Is target class within limits?
2. **Responsibility**: Can you state class purpose in <10 words?
3. **Coupling**: Is class imported by <10 files?
4. **Tests**: Do architectural tests pass?
5. **Documentation**: Is ADR updated if needed?

If any answer is NO:
- [ ] Create refactoring ticket
- [ ] Add to architectural review queue
- [ ] Schedule fix within 2 iterations

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
- `feat/workflow-manager-refactor-tdd-X` - For architectural refactoring work
- `bug-fix/image-linking-system` - For critical image linking investigation
- `integration/phase-5-extension` - For Phase extension work

### Commit Standards
- Include change rationale in commit messages
- Reference affected workflow components  
- Maintain backwards compatibility
- Document bug fixes with clear before/after
- Include integration impact assessment
- **Note architectural decisions** made during development

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

## 🎯 Current Development Patterns (October 2025)

### TDD Success Patterns
- **4-Iteration Methodology**: Proven through Smart Link Management and Advanced Tag Enhancement
- **Utility Extraction**: Modular architecture enables rapid development and reusability
- **Real Data Validation**: Testing with production data proves immediate user value
- **Integration Excellence**: Building on existing infrastructure delivers 80% faster development
- **Architectural Testing**: Prevent god classes through size constraints and regular reviews

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
- [ ] **Check target class size** (use Pre-Development Checklist from Architectural Constraints)

### Development Validation
- [ ] TDD methodology followed (RED → GREEN → REFACTOR)
- [ ] Real user data testing completed
- [ ] Performance targets met or exceeded
- [ ] Integration with existing workflows verified
- [ ] Documentation updated to reflect changes
- [ ] **Architectural constraints maintained** (<500 LOC, <20 methods per class)

### Completion Checklist
- [ ] Lessons learned documented and archived
- [ ] Project manifests updated or moved to DEPRECATED/
- [ ] Essential documentation moved to REFERENCE/
- [ ] Git commit includes comprehensive change description
- [ ] Next development priorities updated in ACTIVE/
- [ ] **ADR created** if architectural decisions were made

## 🔄 Maintenance Guidelines

### Monthly Review Process
1. **Review ACTIVE/**: Identify completed projects and stale manifests
2. **Archive Lessons**: Move TDD lessons learned to appropriate COMPLETED-2025-XX/
3. **Update References**: Ensure REFERENCE/ reflects current system capabilities
4. **Clean Deprecated**: Verify DEPRECATED/ contains only historical context
5. **Validate Tests**: Ensure test coverage maintains 66/66 target
6. **Architectural Review**: Run class size audit, identify refactoring candidates (First Monday)

### Project Health Indicators
- **ACTIVE/ Size**: ≤10 files (current priority projects)
- **Test Coverage**: 66/66 tests passing consistently
- **Performance**: All AI workflows meet established benchmarks
- **Documentation**: REFERENCE/ contains up-to-date essential docs
- **Integration**: New features build on existing infrastructure
- **Architecture**: Zero classes >500 LOC, zero classes >20 methods

## 🏗️ Architectural Health

### Monthly Architectural Review
- **Schedule**: First Monday of each month
- **Duration**: 30 minutes
- **Output**: `Projects/ACTIVE/architectural-review-YYYY-MM.md`
- **Process**: See `.windsurf/rules/architectural-constraints.md`

### Refactoring Queue Management
- Track classes approaching limits in project-todo
- Prioritize refactoring based on growth rate and impact
- Schedule refactoring sprints before adding new features
- Document refactoring decisions in ADRs

---

**See Also**:
- `.windsurf/rules/architectural-constraints.md` - Detailed architectural limits and enforcement
- `Projects/COMPLETED-2025-10/god-class-prevention-lessons-learned.md` - Lessons from WorkflowManager god class
- `Projects/ACTIVE/workflow-manager-refactor-tdd-manifest.md` - Example refactoring project

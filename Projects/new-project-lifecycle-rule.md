# Project Lifecycle Management Rules

> **Purpose**: Systematic project organization and maintenance  
> **Updated**: 2025-09-24

## 🔄 Project Lifecycle Stages

### **1. Planning → ACTIVE/**
- New project manifests start in ACTIVE/
- Include clear success criteria and completion definition
- Reference existing systems for integration opportunities
- Follow TDD iteration planning patterns
- Limit ACTIVE/ to ≤10 files for cognitive load management

### **2. Implementation → development/**
- All code, tests, and technical artifacts in development/
- Maintain connection to ACTIVE/ manifest
- Document lessons learned during implementation
- Follow established TDD methodology patterns
- Preserve backward compatibility with existing workflows

### **3. Completion → COMPLETED-2025-XX/**
- Move lessons learned to monthly completion archive immediately
- Archive manifests to DEPRECATED/ if superseded by new versions
- Update ACTIVE/project-todo-v3.md to reflect completion status
- Maintain references in REFERENCE/windsurf-project-changelog.md

### **4. Maintenance → REFERENCE/**
- Keep essential documentation updated and easily accessible
- Archive outdated versions to DEPRECATED/
- Maintain clear paths to active work
- Ensure documentation reflects current system state

## 📊 Organization Maintenance

### **Monthly Review Process:**
1. **Review ACTIVE/**: Identify completed projects and stale manifests
2. **Archive Lessons**: Move TDD lessons learned to appropriate COMPLETED-2025-XX/
3. **Update References**: Ensure REFERENCE/ reflects current system capabilities
4. **Clean Deprecated**: Verify DEPRECATED/ contains only historical context
5. **Update TODO**: Reflect completions and new priorities in project-todo-v3.md

### **Cognitive Load Targets:**
- **ACTIVE/**: ≤10 files (current priority projects and manifests)
- **Main Directory**: ≤5 files (essential navigation only)
- **REFERENCE/**: ≤10 files (frequently accessed essential docs)
- **Archives**: Unlimited (organized chronologically by completion date)

## 🎯 Integration with AI Workflows

### **TDD Project Patterns:**
- Follow established 4-iteration TDD methodology
- Archive lessons learned immediately upon iteration completion
- Reference previous iterations for acceleration patterns and utility reuse
- Maintain modular utility architecture approaches
- Build on existing infrastructure vs creating duplicate systems

### **AI System Integration:**
- New features must leverage existing AI infrastructure (WorkflowManager, CLI patterns)
- Preserve backward compatibility with established workflows
- Follow established CLI patterns and user experience design
- Maintain performance targets and test coverage standards
- Integrate with existing weekly review and promotion systems

## 📁 File Movement Guidelines

### **Safe Movement Practices:**
- Always preserve git history when moving files
- Update internal references after file moves
- Maintain backward compatibility where possible
- Document significant organizational changes in changelog
- Use safety-first principles with backup/rollback options

### **Validation Checklist:**
- [ ] All ACTIVE/ files represent current priorities
- [ ] REFERENCE/ contains only essential, updated documentation
- [ ] Completed work properly archived by completion date
- [ ] DEPRECATED/ clearly separated from active planning
- [ ] Main directory maintains minimal cognitive load
- [ ] File paths in documentation and rules are accurate

## 🚀 Project Success Patterns

### **TDD Integration Success Factors:**
- **Utility Extraction**: Modular architecture enables rapid development
- **Integration-First**: Building on existing infrastructure accelerates delivery
- **Real Data Validation**: Testing with production data proves immediate value
- **Performance Excellence**: Exceed targets through systematic optimization

### **Workflow Management Excellence:**
- **Safety-First**: Comprehensive backup/rollback systems prevent data loss
- **Link Preservation**: Maintain knowledge graph integrity during file moves
- **AI Enhancement**: Leverage existing quality scoring and connection discovery
- **User Experience**: Consistent CLI patterns and emoji-enhanced interfaces

## 📋 Action Items for New Projects

### **Project Initiation:**
1. Create manifest in ACTIVE/ with clear success criteria
2. Reference existing systems for integration opportunities
3. Plan TDD iterations with utility extraction strategy
4. Establish performance targets and test coverage goals

### **During Implementation:**
1. Maintain connection between code and ACTIVE/ manifest
2. Document lessons learned in real-time
3. Follow established TDD RED → GREEN → REFACTOR cycles
4. Build on existing infrastructure patterns

### **Project Completion:**
1. Move lessons learned to COMPLETED-2025-XX/ immediately
2. Archive superseded manifests to DEPRECATED/
3. Update project-todo-v3.md with completion status
4. Document achievements in windsurf-project-changelog.md

---

**This rule ensures systematic project organization that maintains cognitive clarity while preserving complete historical context and supporting rapid development through proven patterns.**

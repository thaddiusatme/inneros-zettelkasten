# InnerOS Context Engineering Bug Reporting Template

> **Version**: 1.0  
> **Updated**: 2025-10-03  
> **Purpose**: Standardized bug reporting for AI-enhanced knowledge management systems

## 🎯 Quick Bug Report

**Use this section for rapid bug capture. Complete details can be filled in later.**

- **Bug ID**: `BUG-YYYYMMDD-HHMM-short-description`
- **Severity**: 🔴 CRITICAL | 🟠 HIGH | 🟡 MEDIUM | 🟢 LOW
- **Status**: 🆕 NEW | 🔍 INVESTIGATING | 🔧 IN PROGRESS | ✅ RESOLVED | 🚫 CLOSED
- **One-Line Summary**: 
- **Affected System**: 
- **Discovered**: YYYY-MM-DD HH:MM

---

## 📋 Bug Details

### System Context
- **Component**: (e.g., AI Workflow, Template Processing, Image Linking, CLI Tools)
- **InnerOS Version**: 
- **Branch**: 
- **Last Commit**: 
- **Environment**: Development | Production | Testing

### Issue Description

**What happened?**
<!-- Clear description of the unexpected behavior -->

**What was expected?**
<!-- Description of the correct/expected behavior -->

**What actually occurred?**
<!-- Detailed description of what went wrong -->

### Reproduction Steps

1. 
2. 
3. 
4. 

**Reproducibility**: Always | Sometimes | Rare | Unable to reproduce

### Impact Assessment

**System Integrity**: ❌ Compromised | ⚠️ At Risk | ✅ Maintained

**Affected Workflows**:
- [ ] Capture Processing
- [ ] Note Promotion
- [ ] AI Enhancement
- [ ] Template Processing
- [ ] Image Linking
- [ ] Connection Discovery
- [ ] Weekly Review
- [ ] Directory Organization
- [ ] Other: _____________

**User Impact**:
- **Severity**: Data Loss | Workflow Blocked | Degraded Performance | Minor Inconvenience
- **Scope**: Single Note | Collection | Entire System
- **Workaround Available**: Yes | No
- **Estimated Users Affected**: 

### Technical Details

**Error Messages**:
```
[Paste any error messages, stack traces, or logs here]
```

**File Paths**:
- Affected files: 
- Log location: 
- Backup location: 

**System State**:
- Notes in collection: 
- Processing queue size: 
- Disk space available: 
- Memory usage: 

### Evidence & Artifacts

**Screenshots**: 
<!-- Link to screenshots showing the issue -->

**Log Files**:
<!-- Link to relevant logs -->

**Example Files**:
<!-- Link to affected notes or files that demonstrate the issue -->

**Before/After Comparison**:
<!-- If applicable, show state before and after the bug occurred -->

---

## 🔍 Investigation

### Root Cause Analysis

**Suspected Cause**:
<!-- Initial hypothesis about what's causing the issue -->

**Investigation Steps Taken**:
1. 
2. 
3. 

**Findings**:
<!-- What was discovered during investigation -->

**Root Cause**:
<!-- Confirmed underlying cause, if identified -->

### Related Issues

**Similar Bugs**: 
- Link to related bug reports

**Known Patterns**:
- Is this part of a larger pattern of issues?

**Dependencies**:
- What other systems or components are involved?

---

## 🔧 Resolution

### Proposed Fix

**Approach**:
<!-- Description of the proposed solution -->

**Implementation Plan**:
1. 
2. 
3. 

**Testing Strategy**:
- [ ] Unit tests created
- [ ] Integration tests updated
- [ ] Real data validation
- [ ] Regression testing completed

### Code Changes

**Files Modified**:
- 
- 
- 

**Pull Request**: #___

**Branch**: `fix/bug-description`

**Commit Hash**: 

### Validation

**Test Results**:
- [ ] All existing tests passing
- [ ] New tests created and passing
- [ ] Real-world scenario validated
- [ ] Performance impact assessed

**Deployment Notes**:
<!-- Any special considerations for deploying this fix -->

---

## 📚 Prevention

### Lessons Learned

**What went wrong?**
<!-- Analysis of how this bug was introduced -->

**What could prevent this in the future?**
<!-- Suggestions for preventing similar issues -->

### Action Items

**Code Improvements**:
- [ ] Add validation for ___
- [ ] Improve error handling in ___
- [ ] Update documentation for ___

**Process Improvements**:
- [ ] Add to testing checklist
- [ ] Update review criteria
- [ ] Create new workflow guard

**Documentation Updates**:
- [ ] Update user guide
- [ ] Add to known issues
- [ ] Update troubleshooting guide

---

## 📝 Timeline

| Date | Activity | Owner | Notes |
|------|----------|-------|-------|
| YYYY-MM-DD | Reported | | Initial bug report |
| YYYY-MM-DD | Triaged | | Severity and priority assigned |
| YYYY-MM-DD | Investigation | | Root cause analysis completed |
| YYYY-MM-DD | Fix Implemented | | Code changes merged |
| YYYY-MM-DD | Validated | | Testing completed |
| YYYY-MM-DD | Resolved | | Bug closed |

---

## 🔗 References

**Related Documentation**:
- 

**External Resources**:
- 

**Stakeholder Communication**:
- 

---

## 🏷️ Metadata

```yaml
bug_id: BUG-YYYYMMDD-HHMM-description
severity: critical|high|medium|low
status: new|investigating|in-progress|resolved|closed
component: [system-component]
tags: [relevant, tags, for, searchability]
reported_by: 
assigned_to: 
created: YYYY-MM-DD HH:MM
updated: YYYY-MM-DD HH:MM
resolved: YYYY-MM-DD HH:MM
```

---

## 💡 Usage Guidelines

### Severity Classification

- **🔴 CRITICAL**: System integrity compromised, data loss risk, complete workflow blockage
- **🟠 HIGH**: Major functionality broken, significant workflow impact, workaround difficult
- **🟡 MEDIUM**: Feature degraded, workflow inconvenience, workaround available
- **🟢 LOW**: Minor issue, cosmetic problem, minimal impact

### Status Workflow

1. **🆕 NEW**: Bug reported, awaiting triage
2. **🔍 INVESTIGATING**: Root cause analysis in progress
3. **🔧 IN PROGRESS**: Fix implementation underway
4. **✅ RESOLVED**: Fix implemented and validated
5. **🚫 CLOSED**: Bug confirmed resolved in production

### Critical Bug Protocol

For 🔴 CRITICAL bugs:
1. Immediately create backup before investigation
2. Document current system state
3. Notify all stakeholders
4. Use `/bug-triage-workflow` for systematic resolution
5. Prioritize over all other work
6. Create rollback plan before implementing fix

---

*Template maintained by InnerOS Development Team*
*Last Updated: 2025-10-03*

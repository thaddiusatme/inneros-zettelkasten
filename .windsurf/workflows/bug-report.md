---
description: Standardized bug reporting workflow for InnerOS context engineering environment
---

# Bug Report Workflow

This workflow ensures all bug reports follow the standardized template and include all necessary information for investigation and resolution.

## When to Use This Workflow

- Screenshot images not displaying or linking correctly
- AI automation processes causing data loss or corruption
- Template processing failures
- System integrity issues
- Performance degradation
- Workflow blockages
- Any unexpected behavior affecting knowledge management

## Workflow Steps

### 1. Initial Bug Identification

**AI Action**: Gather initial context
- What is the unexpected behavior?
- What was the expected behavior?
- When was this discovered?
- What files/workflows are affected?

**Output**: One-line bug summary

### 2. Generate Bug ID and File

**AI Action**: Create standardized bug report file
```bash
# Format: BUG-YYYYMMDD-HHMM-short-description.md
# Location: Projects/ACTIVE/BUG-{timestamp}-{description}.md
```

**Template Source**: `Projects/REFERENCE/bug-reporting-template.md`

**Required**: Copy ENTIRE template structure, fill in all sections

### 3. Severity Classification

**AI Action**: Assess severity using these criteria

- **🔴 CRITICAL**: System integrity compromised, data loss risk, complete workflow blockage
- **🟠 HIGH**: Major functionality broken, significant workflow impact, difficult workaround
- **🟡 MEDIUM**: Feature degraded, workflow inconvenience, workaround available
- **🟢 LOW**: Minor issue, cosmetic problem, minimal impact

**Required**: Document reasoning for severity level

### 4. Evidence Collection

**AI Action**: Gather and document evidence

**Required Artifacts**:
- [ ] Read affected files and capture current state
- [ ] Include error messages or logs (if applicable)
- [ ] Take screenshots or collect user-provided images
- [ ] Identify file paths for all affected resources
- [ ] Document system state (notes count, processing queue, etc.)

### 5. Impact Assessment

**AI Action**: Evaluate complete impact

**Required Analysis**:
- [ ] System Integrity status (Compromised/At Risk/Maintained)
- [ ] List ALL affected workflows (check against standard workflows)
- [ ] Identify scope (Single Note/Collection/Entire System)
- [ ] Determine if workaround exists
- [ ] Estimate user impact

### 6. Investigation Planning

**AI Action**: Document investigation approach

**Required Sections**:
- [ ] Suspected cause (initial hypothesis)
- [ ] Investigation steps to take
- [ ] Related issues or similar bugs
- [ ] Dependencies (other systems/components involved)

### 7. Proposed Resolution

**AI Action**: Design fix approach

**Required Planning**:
- [ ] Describe proposed solution approach
- [ ] Create implementation plan (numbered steps)
- [ ] Define testing strategy
- [ ] List files that will be modified
- [ ] Suggest branch name: `fix/bug-description`

### 8. Prevention Measures

**AI Action**: Identify lessons learned

**Required Analysis**:
- [ ] What went wrong? (how bug was introduced)
- [ ] What could prevent this in future?
- [ ] Code improvement action items
- [ ] Process improvement action items
- [ ] Documentation updates needed

### 9. Timeline Initialization

**AI Action**: Create timeline table with initial entries

**Required Entries**:
- Reported date/time
- Status: NEW
- Next planned action

### 10. Update Project Tracking

**AI Action**: Link bug report to project management

**Required Updates**:
- [ ] Update `Projects/ACTIVE/project-todo-v3.md` with bug status
- [ ] Add to relevant Active Project section
- [ ] Update roadmap if this affects priorities
- [ ] Mark timestamp as current

### 11. Metadata Completion

**AI Action**: Fill complete YAML metadata block

**Required Fields**:
```yaml
bug_id: BUG-YYYYMMDD-HHMM-description
severity: critical|high|medium|low
status: new
component: [system-component]
tags: [searchable, tags]
reported_by: [user or system]
created: YYYY-MM-DD HH:MM
updated: YYYY-MM-DD HH:MM
```

### 12. Validation Checklist

**AI Action**: Verify report completeness before finalizing

**Required Validation**:
- [ ] All template sections filled (no empty sections)
- [ ] Severity classification justified
- [ ] Evidence artifacts linked or embedded
- [ ] Impact assessment complete
- [ ] Investigation plan documented
- [ ] Proposed fix described
- [ ] Prevention measures identified
- [ ] Timeline initialized
- [ ] Project tracking updated
- [ ] Metadata complete and accurate

## Critical Bug Protocol

For **🔴 CRITICAL** severity bugs, **IMMEDIATELY** execute these additional steps:

// turbo
### 1. Create Emergency Backup
```bash
# Before any investigation that might touch affected files
cd /Users/thaddius/repos/inneros-zettelkasten
python3 development/src/utils/directory_organizer.py --backup
```

### 2. Document Current System State
**AI Action**: Capture comprehensive system snapshot
- Total notes in collection
- Processing queue status
- Disk space available
- Recent operations log
- All affected file paths

### 3. Stakeholder Notification
**AI Action**: Add prominent warning to bug report
```markdown
## ⚠️ CRITICAL BUG - IMMEDIATE ATTENTION REQUIRED

This bug has CRITICAL severity and requires immediate resolution:
- System Integrity: [status]
- Data Loss Risk: [yes/no]
- Workflow Impact: [description]
- Recommended Action: [immediate next steps]
```

### 4. Prioritize Over All Other Work
**AI Action**: Update project-todo-v3.md
- Mark as Priority 1
- Add to "Next 2 Weeks Roadmap" at top
- Update status line to reflect critical bug

### 5. Create Rollback Plan
**AI Action**: Document rollback strategy before implementing fix
- Backup location documented
- Rollback steps numbered
- Validation criteria defined
- Emergency contact information

## Output Checklist

Before completing this workflow, verify:

- [x] Bug report file created in `Projects/ACTIVE/`
- [x] ALL template sections completed (not just populated)
- [x] Evidence collected and linked
- [x] Severity justified with reasoning
- [x] Impact fully assessed
- [x] Investigation plan documented
- [x] Proposed fix described
- [x] Prevention measures identified
- [x] Project tracking updated
- [x] Metadata complete
- [x] For CRITICAL bugs: Emergency protocol executed

## Integration with Existing Workflows

**Related Workflows**:
- Use `/bug-triage-workflow` for systematic resolution after report creation
- Use existing TDD workflows for fix implementation
- Use `/directory-organization-tdd` if bug involves file operations
- Use `/fleeting-note-lifecycle-workflow` if bug affects note processing

**Template Reference**: 
- Master template: `Projects/REFERENCE/bug-reporting-template.md`
- Always copy FULL template, never create abbreviated versions
- Keep template updated as bug reporting evolves

## Success Criteria

A successful bug report:
1. **Complete**: Every section of template filled with meaningful content
2. **Actionable**: Clear next steps for investigation and resolution
3. **Documented**: All evidence and context captured
4. **Tracked**: Linked to project management and roadmap
5. **Preventive**: Includes lessons learned and prevention measures

---

**Workflow Version**: 1.0  
**Created**: 2025-10-03  
**Template Source**: `Projects/REFERENCE/bug-reporting-template.md`  
**Last Updated**: 2025-10-03

# Bug Reporting Quick Start Guide

## How to Create a Bug Report with Windsurf

### Simple Method: Use the Workflow Command

When you encounter a bug, simply tell Windsurf:

```
I found a bug: [brief description]
```

Or trigger the workflow directly:

```
Use /bug-report workflow for [issue description]
```

Windsurf will automatically:
1. ✅ Use the standardized template from `Projects/REFERENCE/bug-reporting-template.md`
2. ✅ Follow all 12 workflow steps systematically
3. ✅ Ensure every section is completed
4. ✅ Update project tracking automatically
5. ✅ Apply critical bug protocol if severity is CRITICAL

### What Windsurf Will Do Automatically

**Step 1-2**: Generate Bug ID and create file
- Format: `BUG-YYYYMMDD-HHMM-description.md`
- Location: `Projects/ACTIVE/`

**Step 3**: Classify severity
- 🔴 CRITICAL: System integrity compromised
- 🟠 HIGH: Major functionality broken
- 🟡 MEDIUM: Feature degraded
- 🟢 LOW: Minor issue

**Step 4**: Collect evidence
- Read affected files
- Capture error messages
- Document system state

**Step 5**: Assess impact
- System integrity status
- Affected workflows
- User impact scope

**Step 6-9**: Plan investigation and resolution
- Root cause hypothesis
- Implementation plan
- Prevention measures

**Step 10**: Update project tracking
- Link to `project-todo-v3.md`
- Update roadmap if needed

**Step 11-12**: Complete metadata and validate
- Full YAML frontmatter
- Comprehensive checklist verification

### For Critical Bugs

Windsurf will **automatically execute** these additional steps:

1. ⚠️ Create emergency backup
2. 📊 Document complete system state
3. 🚨 Add critical bug warning banner
4. 📌 Prioritize in project tracking
5. 🔙 Create rollback plan

### Examples

#### Example 1: Screenshot Not Displaying
```
I found a bug: The screenshot in capture-20250926-0954-visual-content.md 
is not showing in Obsidian. The file path points to OneDrive instead of 
the repository.
```

**Result**: Windsurf creates `BUG-20251003-0906-screenshot-image-linking.md` with:
- Severity: 🔴 CRITICAL (system integrity issue)
- Complete investigation plan
- Proposed MediaAssetManager solution
- Project tracking updated

#### Example 2: Template Processing Issue
```
Use /bug-report workflow for templater placeholders not processing
```

**Result**: Windsurf creates comprehensive bug report with:
- Evidence from affected templates
- Impact on Reading Intake Pipeline
- Root cause analysis
- TDD-based fix approach

#### Example 3: Performance Degradation
```
I'm seeing slow performance in the weekly review command. It's taking 
over 2 minutes for 50 notes.
```

**Result**: Windsurf creates bug report with:
- Performance benchmarks
- System state analysis
- Optimization suggestions
- Testing strategy

### Workflow Integration

The bug reporting workflow integrates with:

- **`/bug-triage-workflow`**: Use after creation for systematic resolution
- **TDD workflows**: For test-driven fix implementation
- **`/directory-organization-tdd`**: If bug involves file operations
- **`/fleeting-note-lifecycle-workflow`**: If bug affects note processing

### Quality Assurance

Every bug report includes **automatic validation**:

- ✅ All template sections completed (not just populated)
- ✅ Evidence collected and linked
- ✅ Severity justified with reasoning
- ✅ Impact fully assessed
- ✅ Investigation plan documented
- ✅ Proposed fix described
- ✅ Prevention measures identified
- ✅ Project tracking updated
- ✅ Metadata complete

### File Locations

- **Workflow**: `.windsurf/workflows/bug-report.md`
- **Template**: `Projects/REFERENCE/bug-reporting-template.md`
- **Bug Reports**: `Projects/ACTIVE/BUG-*.md`
- **Tracking**: `Projects/ACTIVE/project-todo-v3.md`

### Tips for Effective Bug Reports

**DO**:
- ✅ Describe the unexpected behavior clearly
- ✅ Provide specific file paths and examples
- ✅ Include screenshots if visual issue
- ✅ Mention when you first noticed the issue
- ✅ Note any recent changes that might be related

**DON'T**:
- ❌ Skip evidence collection
- ❌ Guess at severity without analysis
- ❌ Omit impact assessment
- ❌ Forget to update project tracking
- ❌ Create abbreviated bug reports

### Verification Checklist

After Windsurf creates the bug report, verify:

1. **File Created**: Bug report exists in `Projects/ACTIVE/`
2. **Complete Template**: All sections filled with meaningful content
3. **Evidence Linked**: Screenshots, logs, file paths documented
4. **Severity Justified**: Classification reasoning provided
5. **Impact Assessed**: Workflows and scope identified
6. **Plan Documented**: Investigation and resolution steps outlined
7. **Tracking Updated**: `project-todo-v3.md` reflects new bug
8. **Metadata Complete**: YAML frontmatter fully populated

### Continuous Improvement

The bug reporting workflow evolves with the project:

- Template updated based on lessons learned
- Workflow steps refined from bug patterns
- Severity criteria adjusted for accuracy
- Integration points added as system grows

**Template Version**: 1.0  
**Workflow Version**: 1.0  
**Last Updated**: 2025-10-03

---

## Quick Reference Card

| Action | Command |
|--------|---------|
| Report new bug | "I found a bug: [description]" |
| Use workflow | "/bug-report for [issue]" |
| View template | `Projects/REFERENCE/bug-reporting-template.md` |
| Check workflow | `.windsurf/workflows/bug-report.md` |
| Find reports | `Projects/ACTIVE/BUG-*.md` |
| Update tracking | Automatically done by workflow |

**Remember**: The workflow ensures consistency. Just describe the bug clearly, and Windsurf handles the structure.

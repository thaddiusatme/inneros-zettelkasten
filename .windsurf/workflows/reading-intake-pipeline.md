---
description: Reading Intake Pipeline development workflow for Phase 5 extension
---

# Reading Intake Pipeline Development Workflow

> **Phase**: 5 Extension  
> **Timeline**: Sprint 0 (Aug 11-15), MVP (Aug 18), Full System (Aug 29)  
> **Integration**: Leverages existing AI workflows (quality scoring, tagging, weekly review)  

## 🎯 Critical Path Dependencies

### **BLOCKER: Template Processing Bug**
Before implementing new features, fix critical template bug:
- **File**: `knowledge/Inbox/fleeting-20250806-1520-bug-images-dissapear.md.md`
- **Issue**: `created: {{date:YYYY-MM-DD HH:mm}}` not processing to actual timestamp
- **Impact**: Template automation broken, blocking workflow functionality
- **Priority**: 🔴 CRITICAL - Must be resolved first

## 📋 Development Phases

### **Phase 1: Foundation (Aug 11-15)**
1. **Fix template processing bug** (CRITICAL PATH)
   ```bash
   # Test template functionality
   python3 tests/integration/test_template_processing.py
   ```

2. **Create literature note templates**
   ```bash
   # Create templates with claims/quotes sections
   touch Templates/literature-note.md
   touch Templates/saved-article.md
   ```

3. **Design import adapters**
   - CSV/JSON parser for bookmarks export
   - Twitter JSON converter
   - YouTube metadata extractor
   - RSS feed processor

### **Phase 2: AI Integration (Aug 18-22)**
4. **Extend existing AI workflows**
   ```bash
   # Leverage Phase 5 AI features (use dedicated CLIs per ADR-004)
   python3 development/src/cli/reading_intake_cli.py process-imports
   python3 development/src/cli/analytics_demo.py . --import-quality
   ```

5. **Schema integration**
   - Add `source`, `url`, `saved_at` fields to existing metadata
   - Extend quality scoring for imported content
   - Integrate with weekly review automation

### **Phase 3: Advanced Features (Aug 25-29)**
6. **CLI integration**
   ```bash
   # Use dedicated reading_intake_cli.py (ADR-004, October 2025)
   python3 development/src/cli/reading_intake_cli.py import-bookmarks file.html
   python3 development/src/cli/reading_intake_cli.py upgrade-reading-notes
   ```

7. **Performance validation**
   - Target: <30 seconds per item triage
   - Quality: 70% Literature notes have 2+ links + 1 claim
   - Productivity: 5+ Permanent notes promoted per week

## 🧪 TDD Methodology

### **Test-First Development**
```bash
# Red: Write failing test
python3 -m pytest tests/test_reading_intake.py::test_import_bookmarks -v

# Green: Make test pass
# Implement minimal functionality

# Refactor: Improve code quality
# Run full test suite
python3 -m pytest tests/ -v
```

### **Integration Points**
- **Existing AI Features**: Quality scoring, smart tagging, weekly review
- **Template System**: Literature note templates with structured claims/quotes  
- **CLI Tools**: Dedicated `reading_intake_cli.py` (ADR-004) and `analytics_demo.py`
- **Validation**: Link checking, quality thresholds, promotion automation

## 📊 Success Metrics

### **Technical Targets**
- **Performance**: <30 seconds per item triage
- **Quality**: 70% Literature notes have 2+ links + 1 claim  
- **Productivity**: 5+ Permanent notes promoted per week
- **Error Rate**: <1% on importer jobs
- **Test Coverage**: Maintain 66/66 tests passing

### **Integration Success**
- **Schema Compatibility**: No breaking changes to existing metadata
- **AI Workflow Preservation**: All Phase 5 features remain functional
- **Template Reliability**: 100% template processing success rate

## 🚨 Error Prevention

### **Before Starting Development**
1. ✅ Template processing bug resolved
2. ✅ Current test suite passes (66/66)
3. ✅ AI workflows functional (quality scoring, tagging, weekly review)
4. ✅ Integration analysis reviewed (`Projects/reading-intake-integration-analysis.md`)

### **During Development**
- Test template changes immediately
- Validate AI workflow compatibility
- Maintain backward compatibility
- Document all schema additions

## 📝 Documentation Updates

### **Required Updates**
- Update `Projects/inneros-manifest-v3.md` with implementation details
- Add Reading Intake section to `Projects/project-todo-v3.md`
- Document new CLI commands in `README.md`
- Update changelog with feature additions

### **Integration Documentation**
- Schema compatibility guide
- AI workflow integration points
- Template system enhancements
- Performance benchmark results

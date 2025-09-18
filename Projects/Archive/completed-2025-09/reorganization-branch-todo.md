# Project Reorganization Branch - Mini TODO

> **Branch**: `feature/project-reorganization-preparation`  
> **Status**: 🟢 **GREEN BASELINE** - Ready for reorganization  
> **Last Updated**: 2025-08-04 17:47

## 🎯 **Current Session Completed**
- [x] **Achieve 100% GREEN baseline status** - All 182 tests passing
- [x] **Fix 14 test failures systematically** - TDD-driven approach maintained
- [x] **Create git branch and baseline commit** - `4e2aac8` rollback point established  
- [x] **Document reorganization strategy** - Comprehensive manifest created
- [x] **Archive legacy project files** - Clean project structure established

## 🚀 **Immediate Next Actions** (Phase 1)

### **Directory Structure Creation** ⏱️ 15 minutes
- [ ] Create `development/` subdirectory in project root
- [ ] Create `knowledge/` subdirectory in project root  
- [ ] Create `development/docs/` for technical documentation
- [ ] Create basic README files for each new directory

### **Core File Movements** ⏱️ 30 minutes
- [ ] Move `src/` → `development/src/`
- [ ] Move `tests/` → `development/tests/` 
- [ ] Move `demos/` → `development/demos/` (if exists)
- [ ] Move `pytest.ini` → `development/pytest.ini`
- [ ] Move `requirements.txt` → `development/requirements.txt`

### **Knowledge Content Migration** ⏱️ 20 minutes  
- [ ] Move `Inbox/` → `knowledge/Inbox/`
- [ ] Move `Fleeting Notes/` → `knowledge/Fleeting Notes/`
- [ ] Move `Permanent Notes/` → `knowledge/Permanent Notes/`
- [ ] Move `Archive/` → `knowledge/Archive/`
- [ ] Move `Templates/` → `knowledge/Templates/`
- [ ] Move `.obsidian/` → `knowledge/.obsidian/`

### **Configuration Updates** ⏱️ 25 minutes
- [ ] Update `.gitignore` for new directory structure
- [ ] Update root `README.md` with new navigation
- [ ] Create `development/README-dev.md` for developers
- [ ] Create `knowledge/README-knowledge.md` for knowledge workers

## 🧪 **Phase 1 Validation** ⏱️ 15 minutes
- [ ] Run test discovery check: `python3 -m pytest --collect-only`
- [ ] Verify import paths work: `python3 -c "from development.src.ai import *"`
- [ ] Test basic CLI access: Check if scripts run from new paths
- [ ] Validate git status shows clean moves

## 🔧 **Phase 2: Path & Import Updates** (Next Session)

### **Python Import Path Fixes** ⏱️ 45 minutes
- [ ] Update all `from src.` imports → `from development.src.`
- [ ] Update pytest configuration for new test discovery paths
- [ ] Update CLI script shebangs and module imports
- [ ] Test imports: `python3 -c "from development.src.ai.tagger import AITagger"`

### **Configuration File Updates** ⏱️ 30 minutes
- [ ] Update `development/pytest.ini` test paths
- [ ] Update any hardcoded paths in Python code
- [ ] Update Obsidian vault configuration if needed
- [ ] Update any build/deployment scripts

### **CLI Tool Path Updates** ⏱️ 20 minutes
- [ ] Update all demo scripts in `development/src/cli/`
- [ ] Test analytics demo: `python3 development/src/cli/analytics_demo.py`
- [ ] Test workflow demo: `python3 development/src/cli/workflow_demo.py`
- [ ] Test weekly review: `python3 development/src/cli/workflow_demo.py --weekly-review`

## 🎨 **Phase 3: User Experience Enhancement** (Next Session)

### **Wrapper Script Creation** ⏱️ 30 minutes
- [ ] Create `inneros` wrapper script in project root
- [ ] Add analytics command: `inneros analytics [path]`
- [ ] Add workflow command: `inneros workflow [path] [--weekly-review]`
- [ ] Add enhancement command: `inneros enhance [file]`
- [ ] Make wrapper script executable: `chmod +x inneros`

### **Documentation Updates** ⏱️ 45 minutes
- [ ] Update main README with new structure and wrapper usage
- [ ] Create migration guide for existing users
- [ ] Update developer setup instructions
- [ ] Document CLI wrapper commands and examples

### **Template & Workflow Updates** ⏱️ 20 minutes
- [ ] Test Templater scripts work with new structure
- [ ] Update any hardcoded paths in templates
- [ ] Test note creation workflows
- [ ] Validate AI processing workflows

## 🎯 **Phase 4: Final Validation & Polish** (Next Session)

### **Comprehensive Testing** ⏱️ 30 minutes
- [ ] **CRITICAL**: Run full test suite: `python3 -m pytest development/tests/`
- [ ] Test all CLI demos with new paths
- [ ] Test AI workflows (tagging, enhancement, analytics)
- [ ] Test weekly review generation
- [ ] Validate Obsidian vault loads correctly

### **Integration Testing** ⏱️ 20 minutes  
- [ ] Test end-to-end note processing workflow
- [ ] Test inbox → fleeting → permanent note promotion
- [ ] Test AI enhancement and quality scoring
- [ ] Test connection discovery and analytics
- [ ] Verify all Phase 5 features work correctly

### **User Workflow Validation** ⏱️ 15 minutes
- [ ] Create test note in `knowledge/Inbox/`
- [ ] Run AI enhancement: `inneros enhance knowledge/Inbox/test-note.md`
- [ ] Run weekly review: `inneros workflow knowledge/ --weekly-review`
- [ ] Test analytics: `inneros analytics knowledge/`
- [ ] Verify Obsidian can open `knowledge/` as vault

## 🚨 **Rollback Procedures** (If Needed)

### **Emergency Rollback** ⏱️ 5 minutes
```bash
git reset --hard 4e2aac8  # Return to 100% GREEN baseline
git checkout main         # Switch back to main branch
```

### **Partial Rollback** ⏱️ 10 minutes
- Identify last working commit in reorganization branch
- Reset to that commit: `git reset --hard [commit-hash]`
- Continue from last working state

## ✅ **Success Criteria Checklist**

### **Must Pass Before Merge**
- [ ] All 182 tests passing (🟢 GREEN status maintained)
- [ ] All CLI tools accessible and functional
- [ ] Obsidian vault opens and functions normally in `knowledge/`
- [ ] AI workflows (tagging, enhancement, analytics) work correctly
- [ ] Weekly review generates successfully
- [ ] No broken import paths or module errors

### **User Experience Validation**
- [ ] Clear navigation between development and knowledge areas
- [ ] Wrapper script provides easy CLI access
- [ ] Documentation clearly explains new structure
- [ ] Migration path documented for existing users

## 📊 **Time Estimates**

- **Phase 1**: ~1.5 hours (Directory setup and basic moves)
- **Phase 2**: ~1.5 hours (Path updates and configuration)  
- **Phase 3**: ~1.5 hours (User experience and wrapper scripts)
- **Phase 4**: ~1 hour (Testing and validation)

**Total Estimated Time**: ~5-6 hours across multiple sessions

## 🎉 **Completion Criteria**

✅ **Ready for Merge When:**
1. All tests passing (🟢 GREEN status)
2. All CLI tools functional with new structure  
3. Obsidian vault works correctly in `knowledge/`
4. Documentation updated and complete
5. Wrapper script provides easy access
6. User workflows validated end-to-end

---

> **Next Action**: Begin Phase 1 - Directory Structure Creation  
> **Estimated Session Time**: 1.5 hours  
> **Risk Level**: 🟢 LOW (backed by solid baseline commit)

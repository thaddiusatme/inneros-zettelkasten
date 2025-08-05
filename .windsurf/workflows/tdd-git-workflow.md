---
type: permanent
created: 2025-08-04 13:58
status: published
tags: [tdd, git, workflow, development, testing, methodology]
visibility: private
---

# TDD & Git Workflow Rules: InnerOS Development Standards

> **Version**: 3.0  
> **Purpose**: Enforce TDD methodology with proper Git branching and commit practices  
> **Integration**: Works with `inneros-manifest.md` and `windsurfrules.md`  

## 🎯 TDD Philosophy & Standards

### **Core TDD Cycle**
```
Red → Green → Refactor → Commit → Push
  ↓      ↓       ↓        ↓       ↓
Write  Make    Improve  Save    Share
Test   Pass    Code     State   Work
```

### **TDD Rule Hierarchy**
1. **Never write production code without a failing test**
2. **Write the simplest test that forces you to write the code you want**
3. **Write the simplest code that makes the test pass**
4. **Refactor only with passing tests**
5. **Commit after each Green phase**

## 🔄 Branch Strategy

### **Main Branch Protection**
- **main**: Production-ready code only
- **develop**: Integration branch for features
- **feature/***: Individual feature development
- **hotfix/***: Critical bug fixes
- **test/***: Experimental testing branches

### **Branch Naming Convention**
```
feature/phase-6-user-auth
feature/tdd-enhanced-weekly-review
hotfix/fix-failing-tests-phase-5-5
test/experimental-connection-discovery
```

### **Branch Lifecycle**
```
main ← develop ← feature/xyz ← local-dev
              ← hotfix/abc
```

## 📝 Commit Standards

### **Commit Message Format**
```
<type>(<scope>): <subject>

<body>

<footer>
```

### **Commit Types**
- **feat**: New feature (TDD: Green phase)
- **fix**: Bug fix (TDD: Red→Green)
- **refactor**: Code improvement (TDD: Refactor phase)
- **test**: Adding/modifying tests (TDD: Red phase)
- **docs**: Documentation changes
- **style**: Code formatting
- **chore**: Build/tooling changes

### **Commit Examples**
```bash
# TDD Red phase
feat(tdd): add failing test for orphaned note detection

# TDD Green phase  
feat(tdd): implement orphaned note detection with 100% coverage

# TDD Refactor phase
refactor(tdd): extract link graph builder for better testability

# Bug fix with TDD
fix(tdd): resolve weekly review edge case with empty collections
```

## 🧪 Test Structure Standards

### **Test File Organization**
```
tests/
├── unit/
│   ├── test_ai/
│   ├── test_cli/
│   └── test_workflow/
├── integration/
│   ├── test_real_analytics.py
│   └── test_user_journeys.py
└── fixtures/
    ├── sample_notes/
    └── test_data/
```

### **Test Naming Convention**
```python
# Unit tests
test_<function_name>_<scenario>_<expected_behavior>()

# Integration tests
test_<feature>_<workflow>_<end_to_end>()

# Examples:
def test_detect_orphaned_notes_empty_collection_returns_empty_list()
def test_weekly_review_integration_with_real_data()
```

### **Test Coverage Requirements**
- **Unit Tests**: 100% for new features
- **Integration Tests**: All user workflows
- **Edge Cases**: Empty collections, malformed data, API failures
- **Performance Tests**: Benchmark against established targets

## 🔄 TDD Workflow for Features

### **Feature Development Cycle**

#### **1. Planning Phase**
```bash
# Create feature branch
git checkout develop
git pull origin develop
git checkout -b feature/tdd-enhanced-weekly-review

# Create test plan
echo "Test Plan: Enhanced Weekly Review" > tests/plans/tdd-weekly-review.md
```

#### **2. Red Phase (Write Failing Test)**
```python
# tests/unit/test_workflow_manager.py
def test_detect_stale_notes_90_day_threshold():
    """Test that notes not modified in 90+ days are flagged as stale."""
    # Arrange
    workflow = WorkflowManager("/test/path")
    old_note = create_note_with_date(days_ago=91)
    
    # Act
    stale_notes = workflow.detect_stale_notes(days_threshold=90)
    
    # Assert
    assert len(stale_notes) == 1
    assert stale_notes[0].filename == old_note.filename
```

#### **3. Green Phase (Make Test Pass)**
```python
# src/ai/workflow_manager.py
def detect_stale_notes(self, days_threshold: int = 90) -> List[NoteStats]:
    """Detect notes not modified within the specified threshold."""
    stale_notes = []
    cutoff_date = datetime.now() - timedelta(days=days_threshold)
    
    for note in self.note_collection:
        if note.last_modified < cutoff_date:
            stale_notes.append(note)
    
    return stale_notes
```

#### **4. Refactor Phase (Improve Code)**
```python
# Extract helper for better testability
def _calculate_cutoff_date(self, days_threshold: int) -> datetime:
    """Calculate cutoff date for stale note detection."""
    return datetime.now() - timedelta(days=days_threshold)
```

#### **5. Commit Sequence**
```bash
# Red phase commit
git add tests/
git commit -m "test(tdd): add failing test for stale note detection"

# Green phase commit
git add src/ tests/
git commit -m "feat(tdd): implement stale note detection with 90-day threshold"

# Refactor commit
git add src/
git commit -m "refactor(tdd): extract cutoff date calculation for testability"
```

## 🎯 Test Categories & Examples

### **Unit Tests**
```python
class TestWorkflowManager:
    def test_detect_orphaned_notes_no_links_returns_empty(self):
        """Test empty collection returns no orphaned notes."""
        pass
    
    def test_detect_orphaned_notes_single_note_returns_it(self):
        """Test single unlinked note is identified as orphaned."""
        pass
    
    def test_detect_orphaned_notes_linked_notes_not_returned(self):
        """Test properly linked notes are not considered orphaned."""
        pass
```

### **Integration Tests**
```python
class TestWeeklyReviewIntegration:
    def test_weekly_review_with_real_notes(self):
        """Test complete weekly review workflow with real note collection."""
        pass
    
    def test_weekly_review_empty_inbox(self):
        """Test weekly review handles empty inbox gracefully."""
        pass
```

### **Performance Tests**
```python
def test_weekly_review_performance_100_notes():
    """Ensure weekly review completes in <30s for 100 notes."""
    start_time = time.time()
    # ... test implementation
    assert time.time() - start_time < 30
```

## 🚦 Pre-commit Hooks

### **Test Validation**
```bash
#!/bin/bash
# .git/hooks/pre-commit

# Run tests
python -m pytest tests/ -v

# Check coverage
python -m pytest tests/ --cov=src --cov-report=term-missing --cov-fail-under=90

# Validate no failing tests
if [ $? -ne 0 ]; then
    echo "❌ Tests failing. Commit blocked."
    exit 1
fi
```

### **Code Quality Checks**
```bash
# Format check
black --check src/ tests/

# Lint check
flake8 src/ tests/

# Type checking
mypy src/
```

## 🏗️ Branch Workflow Examples

### **Fixing Failing Tests**
```bash
# Create hotfix branch
git checkout main
git checkout -b hotfix/fix-failing-tests-phase-5-5

# TDD cycle for each failing test
# ... write failing test → make pass → refactor → commit ...

# Merge back
git checkout main
git merge hotfix/fix-failing-tests-phase-5-5
git push origin main
```

### **Feature Development**
```bash
# Create feature branch
git checkout develop
git checkout -b feature/tdd-enhanced-analytics

# Complete TDD cycle
# ... multiple commits following TDD pattern ...

# Create PR
git push origin feature/tdd-enhanced-analytics
# Create pull request for review
```

## 📊 Progress Tracking

### **TDD Metrics**
- **Test Count**: Track tests per feature
- **Coverage**: Maintain >90% for new code
- **Red→Green Time**: Target <5 minutes per cycle
- **Refactor Safety**: All refactors must maintain passing tests

### **Git Metrics**
- **Commit Frequency**: Small, frequent commits
- **Branch Lifetime**: Feature branches <1 week
- **PR Review Time**: Target <24 hours
- **Merge Conflicts**: Minimize through small changes

## 🎯 Next TDD Targets

### **Immediate (This Week)**
1. **Fix 13 failing tests** using TDD methodology
2. **Create test plan** for each failing test
3. **Red→Green→Refactor** for each failure
4. **Commit after each fix** with proper messages

### **Phase 5.5 Completion**
1. **Test weekly review** edge cases
2. **Performance benchmarks** for 100+ notes
3. **Integration tests** with real data
4. **Documentation** of test scenarios

### **Phase 6 Foundation**
1. **User authentication tests**
2. **Multi-user workflow tests**
3. **API endpoint tests**
4. **Security and privacy tests**

---

## 🚀 Quick TDD Commands

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/unit/test_workflow_manager.py -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html

# Run performance tests
python -m pytest tests/performance/ -v

# Run specific test
python -m pytest tests/unit/test_workflow_manager.py::TestWorkflowManager::test_detect_orphaned_notes -v
```

---

> **TDD Mantra**: "If it's not tested, it's broken. If it's not committed, it's not done."

**TDD Rules Version**: 3.0  
**Last Updated**: 2025-08-04  
**Next Review**: 2025-09-04

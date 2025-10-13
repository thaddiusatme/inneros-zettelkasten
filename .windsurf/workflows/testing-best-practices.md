---
description: Testing infrastructure best practices for fast, reliable, comprehensive test suites
---

# Testing Best Practices: Fast, Reliable, Comprehensive

> **Purpose**: Prevent slow, brittle tests through proper tier separation and test data management  
> **Created**: 2025-10-12  
> **Updated**: 2025-10-12 (After Week 1 TDD Iterations 1-4)  
> **Validated**: 300x performance improvement achieved, 100% marker coverage

---

## 🎯 Core Principles

### **The Testing Pyramid**
```
        /\
       /  \      Smoke Tests (minutes, nightly)
      /    \     Real vault, production scenarios
     /------\    
    /        \   Integration Tests (<30s, every commit)
   /          \  Controlled test data, component interaction
  /------------\
 /              \ Unit Tests (<10s, every save)
/________________\ Pure logic, mocked dependencies
```

**Rule**: More unit tests, fewer integration tests, minimal smoke tests

---

## 📊 Test Tier Definitions

### **Unit Tests** (`tests/unit/`)
**When**: Testing pure logic, algorithms, utilities  
**Duration**: <1 second per test, <10 seconds total  
**Marker**: `@pytest.mark.fast` (auto-applied if in unit/ directory)  
**Data**: Inline fixtures, mocked dependencies  
**Run**: On every file save, during TDD cycles

**Example**:
```python
@pytest.mark.fast
def test_quality_scorer_calculates_correctly():
    scorer = QualityScorer()
    note = {"title": "Test", "content": "..." }
    score = scorer.calculate(note)
    assert 0 <= score <= 1
```

### **Integration Tests** (`tests/integration/`)
**When**: Testing component interaction (CLI → Engine → File System)  
**Duration**: <5 seconds per test, <30 seconds total  
**Marker**: `@pytest.mark.integration` (**REQUIRED** on all integration tests)  
**Data**: Vault factories (`create_minimal_vault()`, `create_small_vault()`)  
**Run**: Before commit, during PR validation

**Week 1 Achievement**: 300x performance improvement (5-10min → 1.35s) using vault factories

**Example**:
```python
@pytest.mark.integration
def test_cli_processes_test_vault(tmp_path):
    vault = create_small_vault(tmp_path)  # 15 notes
    result = run_cli(['--weekly-review', str(vault)])
    assert result.exit_code == 0
    assert "15 notes processed" in result.output
```

### **Smoke Tests** (`tests/smoke/`)
**When**: Testing with real production vault, edge cases  
**Duration**: Minutes (non-blocking)  
**Marker**: `@pytest.mark.smoke` or `@pytest.mark.slow`  
**Data**: Real vault (`KNOWLEDGE_DIR`)  
**Run**: Nightly, before major releases

**Example**:
```python
@pytest.mark.smoke
@pytest.mark.slow
def test_weekly_review_on_production_vault():
    """Validate against actual 300+ note vault"""
    if not KNOWLEDGE_DIR.exists():
        pytest.skip("Real vault not available")
    
    result = run_cli(['--weekly-review', str(KNOWLEDGE_DIR)])
    assert result.exit_code == 0
    # Validate real-world behavior
```

### **Performance Tests** (`tests/performance/`)
**When**: Benchmarking, regression detection, scalability  
**Duration**: Varies (controlled)  
**Marker**: `@pytest.mark.performance`  
**Data**: Generated test vaults (50/100/500/1000 notes)  
**Run**: Weekly, before releases

---

## 🏭 Test Data Management

### **Problem**: Duplicated Test Data
❌ **Anti-Pattern**:
```python
# tests/test_feature_a.py
def test_something():
    vault = tmp_path / "vault"
    (vault / "Inbox").mkdir(parents=True)
    (vault / "Inbox" / "note.md").write_text("...")
    # 50 lines of setup...

# tests/test_feature_b.py
def test_other_thing():
    vault = tmp_path / "vault"
    (vault / "Inbox").mkdir(parents=True)
    # Same 50 lines repeated!
```

✅ **Best Practice**: Vault Factory Pattern (**Week 1 Proven**)
```python
# tests/fixtures/vault_factory.py (TDD Iteration 2 - Oct 12, 2025)

def create_minimal_vault(tmp_path: Path) -> Path:
    """3 notes, <1s creation, for basic CLI tests
    
    Structure:
    - 1 inbox note
    - 1 fleeting note  
    - 1 permanent note
    """
    vault = tmp_path / "test-vault"
    (vault / "Inbox").mkdir(parents=True)
    (vault / "Fleeting Notes").mkdir(parents=True)
    (vault / "Permanent Notes").mkdir(parents=True)
    
    # Create representative notes with proper YAML
    create_test_note(
        vault / "Inbox" / "test-inbox.md",
        title="Test Inbox Note",
        note_type="fleeting",
        tags=["test"]
    )
    # ... (see vault_factory.py for complete implementation)
    return vault

def create_small_vault(tmp_path: Path) -> Path:
    """15 notes, <5s creation, for integration tests
    
    Representative distribution:
    - 5 inbox notes (various types)
    - 5 fleeting notes (various quality levels)
    - 3 permanent notes (well-formed)
    - 2 literature notes
    """
    # Real implementation: 15 notes across all directories
    # Performance validated: 1.35s for complete integration suite
    
def create_large_vault(tmp_path: Path) -> Path:
    """50 notes, <10s creation, for edge cases
    
    Includes problem cases:
    - Malformed YAML
    - Missing frontmatter
    - Broken links
    - Empty files
    """

# tests/integration/test_feature.py
from fixtures.vault_factory import create_small_vault

def test_cli_command(tmp_path):
    vault = create_small_vault(tmp_path)
    # Test logic only, no setup duplication
```

### **Test Data in Git**
✅ **Commit sample data** to `tests/fixtures/test_data/`:
```
tests/fixtures/test_data/
├── minimal/              # 3 notes committed
│   ├── Inbox/
│   │   └── sample.md
│   ├── Fleeting Notes/
│   └── Permanent Notes/
├── problem_cases/        # Edge cases committed
│   ├── malformed-yaml.md
│   ├── broken-links.md
│   └── empty-frontmatter.md
└── README.md            # Documents test data
```

**Benefits**:
- Reproducible across environments
- Easy to add edge cases
- Version controlled

---

## 🏷️ Test Marker Strategy

### **Auto-Apply Markers** (conftest.py) (**TDD Iteration 1 - Validated**)
```python
# tests/conftest.py (Week 1 implementation)
def pytest_collection_modifyitems(items):
    """Auto-tag tests based on directory
    
    Achievement: Enabled 100% marker coverage without manual decoration.
    Tests can now be filtered reliably by tier.
    """
    for item in items:
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.fast)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "smoke" in str(item.fspath):
            item.add_marker(pytest.mark.smoke)
            item.add_marker(pytest.mark.slow)
        elif "performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)
```

**Week 1 Learning**: Also add explicit `@pytest.mark.integration` to test **classes** for better documentation and IDE support.

### **Running Different Tiers** (**Week 1 Validated Commands**)
```bash
# Fast tests only (development) - <1s
pytest -m "fast or integration" -v --no-cov
# Week 1 Result: 0.21s (unit) + 1.35s (integration) = 1.56s total

# All except smoke (pre-commit) - <30s
pytest -m "not slow" -v
# Week 1 Result: All fast tests complete in 1.56s

# Random order (verify isolation) - Same duration
pytest -m "not slow" --random-order -v
# Week 1 Result: All 140 tests pass in random order ✅

# Smoke tests (nightly) - Minutes
pytest -m smoke -v

# Specific tier
pytest tests/unit/ -v                    # Unit only
pytest tests/integration/ -v             # Integration only
pytest tests/integration/ -m integration -v  # With marker filter
```

---

## 📊 Coverage Profiles

### **Problem**: Coverage Overhead
Coverage calculation adds 20-40% overhead. Don't run it during development!

### **Solution**: Separate Profiles

**Development** (no coverage, fast feedback):
```bash
# pytest.ini
[tool:pytest]
addopts = -v --tb=short
```

Run tests:
```bash
pytest -m "not slow" --no-cov
```

**CI/CD** (with coverage, comprehensive):
```bash
# .github/workflows/tests.yml
- name: Run Tests
  run: |
    pytest -m "not slow" \
      --cov=src \
      --cov-report=xml \
      --cov-report=html \
      --cov-fail-under=80
```

**Local Coverage Check** (when needed):
```bash
pytest tests/unit/test_new_feature.py --cov=src.new_feature --cov-report=term-missing
```

---

## 🎭 Mock Strategy

### **Decision Tree**

**When to Use Real**:
- ✅ File system operations (use tmp_path)
- ✅ Subprocess calls in integration tests (test actual CLI)
- ✅ Fast local operations (<100ms)

**When to Mock**:
- ✅ External APIs (Ollama, YouTube, Perplexity)
- ✅ Expensive operations (OCR, image processing)
- ✅ Network calls
- ✅ Time-dependent operations (use freezegun)

### **Integration Test Pattern**
```python
@pytest.mark.integration
def test_youtube_cli_with_mock_api(tmp_path, mocker):
    # Use real subprocess (test actual CLI execution)
    # But mock expensive API call
    mock_api = mocker.patch('src.ai.youtube_processor.fetch_transcript')
    mock_api.return_value = [{"text": "Sample transcript"}]
    
    result = subprocess.run(['python', 'youtube_cli.py', 'test_video_id'])
    
    assert result.returncode == 0
    mock_api.assert_called_once()
```

---

## 🔍 Test Isolation

### **Problem**: Order-Dependent Tests
Tests pass individually but fail when run together = state leakage

### **Solution**: Verify Isolation (**Week 1 Iteration 4 - Required**)
```bash
# Install pytest-random-order
pip install pytest-random-order

# Run tests in random order (Week 1: 140 tests pass ✅)
pytest -m "not slow" --random-order -v

# If tests fail randomly:
# 1. Check for global state (class variables, singletons)
# 2. Check for file system mutations (temp files not cleaned)
# 3. Check for shared fixtures without proper teardown
# 4. Check vault factories (ensure using tmp_path, not KNOWLEDGE_DIR)
```

**Week 1 Achievement**: All integration tests pass in random order after vault factory migration. Vault factories provide perfect test isolation.

### **Isolation Checklist**
- [ ] No global state modified
- [ ] Temp files cleaned up (use tmp_path fixture)
- [ ] Mocks reset between tests (use mocker fixture)
- [ ] Database/cache cleared (if applicable)
- [ ] Tests pass in random order

---

## 🚨 Common Pitfalls & Solutions

### **Pitfall 1: Using Real Vault in Integration Tests** (**ROOT CAUSE OF WEEK 1 ISSUE**)
❌ **Problem**: Integration tests take 5-10 minutes (300+ notes scanned)

**Real Example** (Oct 12, 2025):
- Test fixture returned `KNOWLEDGE_DIR` instead of `tmp_path`
- Each test initialized `ImageLinkManager` → scanned 300+ notes
- 11 tests × 30s scan = 5-10 minutes total

✅ **Solution**: Use vault factories with controlled data
```python
# BAD: Uses real vault
def test_cli(tmp_path):
    if KNOWLEDGE_DIR.exists():
        return KNOWLEDGE_DIR  # ← SLOW!

# GOOD: Uses factory
def test_cli(tmp_path):
    vault = create_small_vault(tmp_path)  # ← FAST!
    return vault
```

### **Pitfall 2: Expensive Initialization on Every Test**
❌ **Problem**: `DirectoryOrganizer` scans vault in `__init__`

✅ **Solution**: Lazy initialization with @property
```python
class DirectoryOrganizer:
    def __init__(self, vault_root):
        self.vault_root = vault_root
        self._image_manager = None  # Don't initialize yet
    
    @property
    def image_manager(self):
        if self._image_manager is None:
            self._image_manager = ImageLinkManager(self.vault_root)
        return self._image_manager
```

### **Pitfall 3: No Test Markers**
❌ **Problem**: Can't filter fast vs slow tests

✅ **Solution**: Auto-tag in conftest.py (see Marker Strategy above)

### **Pitfall 4: Coverage Always Running**
❌ **Problem**: Tests slow even with --no-cov

✅ **Solution**: Remove coverage from pytest.ini addopts
```ini
# pytest.ini - BEFORE (always runs coverage)
[tool:pytest]
addopts = --cov=src --cov-report=html

# AFTER (coverage only when requested)
[tool:pytest]
addopts = -v --tb=short
```

### **Pitfall 5: No Performance Baselines**
❌ **Problem**: Don't know if tests are getting slower

✅ **Solution**: Track baselines in version control
```json
// tests/performance/baselines.json
{
  "test_weekly_review_cli": {
    "max_seconds": 30,
    "baseline_seconds": 5.2,
    "variance_tolerance": 0.15
  }
}
```

---

## 📋 Quick Reference

### **Starting New Feature**
```bash
# 1. Check target class size
wc -l src/ai/target_class.py

# 2. Create test file with marker
mkdir -p tests/unit/
cat > tests/unit/test_new_feature.py << 'EOF'
import pytest

@pytest.mark.fast
def test_feature_works():
    # RED phase - failing test
    assert False, "Not implemented yet"
EOF

# 3. Run TDD cycle
pytest tests/unit/test_new_feature.py -v  # RED
# ... implement ...
pytest tests/unit/test_new_feature.py -v  # GREEN
# ... refactor ...
pytest tests/unit/test_new_feature.py -v  # Still GREEN
```

### **Adding Integration Test**
```python
# tests/integration/test_feature_cli.py
import pytest
from fixtures.vault_factory import create_small_vault

@pytest.mark.integration
def test_feature_cli_execution(tmp_path):
    vault = create_small_vault(tmp_path)
    result = run_cli(['--new-feature', str(vault)])
    assert result.exit_code == 0
```

### **Running Tests**
```bash
# Development (fast)
pytest -m "fast or integration" --no-cov -x

# Pre-commit (comprehensive)
pytest -m "not slow" -v

# Coverage check
pytest tests/unit/test_new_feature.py --cov=src.new_feature

# Smoke test (manual)
pytest -m smoke -v
```

---

## 🎯 Success Criteria

Your test suite is healthy when:
- ✅ Unit tests: <10 seconds total
- ✅ Integration tests: <30 seconds total
- ✅ Can run fast tests during TDD cycles (no waiting)
- ✅ All tests have markers (can filter by tier)
- ✅ Test data committed to git (reproducible)
- ✅ Tests pass in random order (isolated)
- ✅ Coverage only runs in CI/CD (not blocking dev)
- ✅ Mock strategy documented (clear when to mock)

---

## 📚 Related Resources

- `.windsurf/rules/updated-development-workflow.md` - TDD methodology
- `.windsurf/workflows/complete-feature-development.md` - 4-phase feature development
- `Projects/ACTIVE/testing-infrastructure-revamp-manifest.md` - Implementation details

---

---

## 🎓 Week 1 Lessons Learned (Oct 12, 2025)

### **TDD Iteration Outcomes**

**Iteration 1** (Day 1): Test Organization & Performance
- Auto-tagging via conftest.py → 100% coverage
- Dev mode optimization → 3x faster (no coverage overhead)
- Result: 0.21s unit tests ✅

**Iteration 2** (Day 2): Vault Factory System  
- Built create_minimal_vault(), create_small_vault(), create_large_vault()
- Replaced KNOWLEDGE_DIR references with vault factories
- Result: 300x performance improvement (5-10min → 1.35s) ✅

**Iteration 3** (Day 2-3): Integration Test Migration
- Migrated 37 integration tests to vault factories
- Updated CLI output expectations (human-readable, not JSON)
- Result: 1.35s integration suite, CI/CD ready ✅

**Iteration 4** (Day 3): Test Markers Verification
- Built static AST marker verification (no subprocess!)
- Found 3 files missing markers, fixed
- Result: 100% marker coverage, 0.05s verification ✅

### **Critical Success Patterns**

1. **Vault Factories Are Key**: 300x performance improvement from this single pattern
2. **Static Analysis > Subprocess**: 6,000x faster marker verification (0.05s vs 5-10min)
3. **Random Order Testing**: pytest-random-order catches state leakage immediately
4. **Fast Rewrites > Slow Patches**: Complete rewrite (15min) faster than patching (30+min)
5. **Following Own Practices**: Applied vault factory pattern to marker verification tests

### **Performance Achievements**

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Unit Tests | 0.21s | 0.21s | Maintained ✅ |
| Integration Tests | 5-10 min | 1.35s | **300x faster** |
| Marker Verification | 5-10 min | 0.05s | **6,000x faster** |
| Total Fast Suite | 5-10 min | 1.56s | **200-400x faster** |

**Success**: All P0 targets exceeded, not just met (1.56s << 30s target)

---

**Status**: ✅ Week 1 Complete - Validated through 4 TDD iterations  
**Updated**: 2025-10-12 after completing testing infrastructure Week 1  
**Next**: Week 2 - Smoke Test Infrastructure (P1)

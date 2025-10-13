# Week 2: Smoke Test Infrastructure - TDD Iteration 6

**Date**: 2025-10-12 (Planning)  
**Status**: 📋 **READY TO START** - Week 1 P0 complete  
**Timeline**: Week 2, Days 1-3 (Oct 14-16 or continue Week 1 Days 4-5)  
**Branch**: `feat/testing-week2-tdd-iteration-6-smoke-tests` (to be created)

---

## 🎯 Week 2 Objective

Create **smoke test infrastructure** for real vault validation while keeping fast tests separate.

**Why?**: Integration tests are now fast (1.35s) but use controlled test data. We still need smoke tests to validate against the real production vault (300+ notes) - but these should run **nightly**, not blocking development.

---

## 📊 Week 1 Achievement Review

**Before moving to Week 2**, let's acknowledge what we just accomplished:

### Performance
- Integration: 5-10min → **1.35s** (300x faster) ✅
- Unit: **0.21s** (maintained) ✅
- Total: **1.56s** (200-400x faster) ✅

### Coverage
- Marker coverage: **100%** ✅
- Test isolation: **140 tests pass random order** ✅
- Documentation: **6 lessons learned docs** ✅

### Decision: Lazy Initialization
**Profiling Result**: 0.001s (1ms) initialization overhead  
**Decision**: ✅ Skip - Premature optimization (50x faster than threshold)

---

## 🔬 TDD Iteration 6: Smoke Test Suite

### Objective

Create smoke tests that validate **real-world scenarios** with the production vault without slowing down development.

### Goals

1. **Smoke Test Directory**: Create `tests/smoke/` with real vault tests
2. **Marker Strategy**: `@pytest.mark.smoke` + `@pytest.mark.slow`
3. **Real Vault Validation**: Test against actual KNOWLEDGE_DIR
4. **Performance**: Minutes (not blocking), run nightly
5. **CI/CD Integration**: Separate workflow (not on every commit)

---

## 📋 TDD Iteration 6 Plan

### RED Phase (1-2 hours)

**Create failing tests** that drive smoke test infrastructure:

```python
# tests/smoke/test_real_vault_workflows.py

@pytest.mark.smoke
@pytest.mark.slow
class TestRealVaultWorkflows:
    """Smoke tests validating real production vault scenarios."""
    
    def test_weekly_review_on_production_vault(self):
        """Validate weekly review against actual vault
        
        RED Phase: This test should fail initially because:
        - KNOWLEDGE_DIR might not exist in CI/CD
        - Need skip mechanism if vault unavailable
        - Need performance baselines for real vault
        """
        if not KNOWLEDGE_DIR.exists():
            pytest.skip("Production vault not available")
        
        result = subprocess.run([
            'python', 'workflow_demo.py',
            str(KNOWLEDGE_DIR),
            '--weekly-review'
        ])
        
        assert result.returncode == 0
        # Should handle 300+ notes in production
        
    def test_connection_discovery_real_vault(self):
        """Validate connection discovery finds real semantic links"""
        # RED: Drive real vault connection discovery
        
    def test_orphaned_notes_detection_real_vault(self):
        """Validate orphaned note detection on real vault"""
        # RED: Drive real metrics on 300+ notes
        
    def test_backup_system_real_vault(self):
        """Validate backup system with actual vault size"""
        # RED: Drive backup of 300+ notes
        
    def test_image_link_preservation_real_vault(self):
        """Validate image links preserved in real vault"""
        # RED: Drive image link scanning on production
```

**Architectural Tests**:
```python
def test_smoke_tests_not_in_fast_suite():
    """Smoke tests must not run with fast tests"""
    # Verify smoke tests skipped by default
    
def test_smoke_tests_have_skip_mechanism():
    """Smoke tests must skip gracefully if vault unavailable"""
    # Verify pytest.skip works correctly
```

### GREEN Phase (2-3 hours)

**Minimal implementation**:

1. **Create smoke test directory**:
```bash
mkdir -p tests/smoke
touch tests/smoke/__init__.py
```

2. **Update conftest.py** for smoke tests:
```python
def pytest_collection_modifyitems(items):
    for item in items:
        # ... existing markers ...
        if "smoke" in str(item.fspath):
            item.add_marker(pytest.mark.smoke)
            item.add_marker(pytest.mark.slow)
```

3. **Create smoke test utilities**:
```python
# tests/smoke/smoke_test_utils.py

def get_production_vault() -> Optional[Path]:
    """Get production vault path, skip if unavailable"""
    vault = KNOWLEDGE_DIR
    if not vault.exists():
        pytest.skip("Production vault not available")
    return vault

def measure_smoke_test_performance(test_name: str):
    """Context manager for performance measurement"""
    # Track smoke test performance
```

4. **Implement 5-10 smoke tests**:
   - Weekly review (production vault)
   - Connection discovery (real semantic links)
   - Orphaned notes (300+ note vault)
   - Backup system (actual vault size)
   - Image link preservation (real media)

5. **Verify marker filtering**:
```bash
# Should NOT run smoke tests
pytest -m "not slow" -v
# Result: 140 fast tests, 0 smoke tests

# Should run ONLY smoke tests
pytest -m smoke -v
# Result: 0 fast tests, 5-10 smoke tests
```

### REFACTOR Phase (1-2 hours)

**Improvements**:

1. **Extract smoke test base class**:
```python
class SmokeTestBase:
    """Base class for all smoke tests"""
    
    @pytest.fixture(autouse=True)
    def setup_production_vault(self):
        self.vault = get_production_vault()
        
    @pytest.fixture(autouse=True)
    def measure_performance(self, request):
        # Auto-track smoke test performance
```

2. **Add performance baselines**:
```json
// tests/smoke/smoke_baselines.json
{
  "weekly_review_production": {
    "max_seconds": 300,
    "baseline_seconds": 45,
    "vault_size_notes": 300
  }
}
```

3. **Create smoke test README**:
```markdown
# Smoke Tests

**Purpose**: Validate real-world scenarios with production vault

**Run**: Nightly (not on every commit)

**Duration**: Minutes (5-10 minutes typical)

**Command**: `pytest -m smoke -v`
```

### COMMIT Phase (30 min)

**Deliverables**:
- [ ] `tests/smoke/test_real_vault_workflows.py` (5-10 smoke tests)
- [ ] `tests/smoke/smoke_test_utils.py` (utilities)
- [ ] `tests/smoke/smoke_baselines.json` (performance baselines)
- [ ] `tests/smoke/README.md` (documentation)
- [ ] Updated `tests/conftest.py` (smoke test markers)
- [ ] Lessons learned doc

**Git commit**:
```bash
git commit -m "feat: TDD Iteration 6 - Smoke Test Infrastructure (Week 2, Day 1)

RED Phase: Created 10 failing smoke tests
- Weekly review on production vault
- Connection discovery with real vault
- Orphaned notes detection (300+ notes)
- Backup system with actual vault size
- Image link preservation validation

GREEN Phase: Minimal implementation
- Created tests/smoke/ directory
- Added smoke test utilities
- Implemented marker filtering
- Result: 5-10 smoke tests passing

REFACTOR Phase: Production-ready
- Extracted SmokeTestBase class
- Added performance baselines
- Created smoke test documentation
- Verified marker separation

Performance: 5-10 minutes (nightly), not blocking dev
Marker: @pytest.mark.smoke + @pytest.mark.slow
Result: Fast tests (1.56s) + Smoke tests (5-10min) separated

Part of Testing Infrastructure Revamp Week 2"
```

---

## 🎯 Success Criteria

### Smoke Test Suite
- [ ] 5-10 smoke tests created
- [ ] All smoke tests validate production vault
- [ ] Smoke tests skip gracefully if vault unavailable
- [ ] Smoke tests have `@pytest.mark.smoke` marker
- [ ] Smoke tests NOT run with fast tests

### Marker Filtering
- [ ] `pytest -m "not slow"` → 140 fast tests, 0 smoke tests
- [ ] `pytest -m smoke` → 0 fast tests, 5-10 smoke tests
- [ ] Smoke tests take 5-10 minutes (acceptable for nightly)

### Documentation
- [ ] Smoke test README created
- [ ] Performance baselines documented
- [ ] Lessons learned captured

### Integration
- [ ] conftest.py updated for smoke markers
- [ ] Smoke test utilities extracted
- [ ] Base class pattern established

---

## 📊 Expected Performance

| Test Tier | Duration | When | Command |
|-----------|----------|------|---------|
| **Unit** | 0.21s | Every save | `pytest tests/unit/` |
| **Integration** | 1.35s | Every commit | `pytest tests/integration/` |
| **Fast Suite** | 1.56s | Pre-commit | `pytest -m "not slow"` |
| **Smoke** | 5-10 min | Nightly | `pytest -m smoke` |
| **All** | 5-10 min | Before release | `pytest` |

---

## 💎 Key Design Decisions

### 1. Smoke Tests Are Separate
**Not**: Mix smoke tests with integration tests  
**But**: Separate directory, separate markers, separate runs

**Why**: Keep fast tests fast. Smoke tests validate real world but don't block TDD.

### 2. Skip If Vault Unavailable
**Pattern**:
```python
if not KNOWLEDGE_DIR.exists():
    pytest.skip("Production vault not available")
```

**Why**: CI/CD might not have production vault. Tests should skip gracefully.

### 3. Performance Baselines
Track smoke test performance to detect regressions in real-world scenarios.

### 4. Minimal Coverage
**Not**: 100 smoke tests covering everything  
**But**: 5-10 smoke tests for critical workflows

**Why**: Smoke tests are expensive. Focus on high-value real-world validation.

---

## 🔗 Week 2 Complete Plan

**Week 2 Timeline** (Oct 14-18 or Days 4-5):

### TDD Iteration 6: Smoke Tests (Day 1-2)
- Real vault validation
- 5-10 smoke tests
- Marker separation

### TDD Iteration 7: Performance Benchmarks (Day 3)
- Create baselines.json with committed metrics
- Regression detection thresholds
- Performance test suite

### TDD Iteration 8: Load Tests (Day 4-5)
- 500 note vault simulation
- 1000 note vault simulation
- Memory usage profiling
- Scalability documentation

---

## 📋 Quick Start (Next Session)

```bash
# 1. Create new branch
git checkout -b feat/testing-week2-tdd-iteration-6-smoke-tests

# 2. Create smoke test directory
mkdir -p development/tests/smoke
cd development/tests/smoke

# 3. Create smoke test file (RED phase)
cat > test_real_vault_workflows.py << 'EOF'
import pytest
from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).parent.parent.parent.parent / "knowledge"

@pytest.mark.smoke
@pytest.mark.slow
class TestRealVaultWorkflows:
    def test_weekly_review_on_production_vault(self):
        """RED: Should fail - not implemented yet"""
        if not KNOWLEDGE_DIR.exists():
            pytest.skip("Production vault not available")
        
        # This will fail - drive implementation
        assert False, "Not implemented"
EOF

# 4. Run RED phase (should fail)
cd development
source venv/bin/activate
PYTHONPATH=. pytest tests/smoke/ -v
# Expected: 1 failed (RED phase success)

# 5. Begin GREEN phase implementation...
```

---

## 🎓 Week 1 Patterns to Apply

**From Week 1 learnings**:
1. ✅ **Vault Factories** - Already proven (don't need for smoke tests, use real vault)
2. ✅ **Static Analysis** - Apply marker verification to smoke tests too
3. ✅ **Fast Rewrites** - If design flawed, rewrite quickly
4. ✅ **Random Order** - Smoke tests should also pass in random order
5. ✅ **Document While Fresh** - Capture lessons after each iteration

---

## 📚 Related Documents

**Week 1 Foundation**:
- `testing-infrastructure-week1-complete-summary.md` - Week 1 achievements
- `.windsurf/workflows/testing-best-practices.md` - Updated with Week 1 learnings

**Manifest**:
- `Projects/ACTIVE/testing-infrastructure-revamp-manifest.md` - Original 3-week plan

**Next**:
- TDD Iteration 7: Performance Benchmarks (Week 2, Day 3)
- TDD Iteration 8: Load Tests (Week 2, Days 4-5)

---

**Status**: 📋 Ready to start TDD Iteration 6  
**Prerequisites**: ✅ Week 1 P0 complete (all targets exceeded)  
**Lazy Init Decision**: ✅ Skipped (1ms overhead, not needed)  
**Next Action**: Create smoke test branch and begin RED phase

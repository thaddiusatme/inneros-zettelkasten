# GitHub Issue: Python Version Mismatch Between CI Workflows

**Title**: Standardize Python version across CI workflows (3.11 vs 3.13)

**Labels**: `ci/cd`, `configuration`, `priority-medium`

---

## 🐛 Problem

CI workflows use different Python versions, potentially causing inconsistent behavior and test results.

**Current State**:
- `ci.yml`: Uses Python 3.13
- `ci-lite.yml`: Uses Python 3.11

---

## 🎯 Impact

- **Inconsistent test results** between workflows
- **Potential compatibility issues** not caught by one workflow
- **Confusing for developers** - which version is "correct"?
- **May hide Python version-specific bugs**

---

## 📋 Current Configuration

### `.github/workflows/ci.yml` (Line 19-22)
```yaml
- name: Set up Python 3.13
  uses: actions/setup-python@v5
  with:
    python-version: '3.13'
```

### `.github/workflows/ci-lite.yml` (Line 19-22)
```yaml
- name: Set up Python 3.11
  uses: actions/setup-python@v5
  with:
    python-version: '3.11'
```

---

## 🎯 Desired Behavior

All CI workflows should use the same Python version to ensure consistent behavior.

**Recommendation**: Use Python 3.11 (stable LTS)
- More widely adopted
- Better package compatibility
- Proven stability in production

**Alternative**: Use Python 3.13 if specific features required
- Document why 3.13 is needed
- Test thoroughly for package compatibility

---

## 📋 Acceptance Criteria

- [ ] Both `ci.yml` and `ci-lite.yml` use same Python version
- [ ] Version choice documented in `README.md` or `CONTRIBUTING.md`
- [ ] All workflows pass with chosen version
- [ ] `requirements.txt` updated if needed with version constraint
- [ ] No breaking changes introduced

---

## 🔧 Recommended Fix

**Option 1: Standardize on Python 3.11**
```yaml
# Both files should have:
- name: Set up Python 3.11
  uses: actions/setup-python@v5
  with:
    python-version: '3.11'
    cache: 'pip'
```

**Option 2: Standardize on Python 3.13**
```yaml
# Both files should have:
- name: Set up Python 3.13
  uses: actions/setup-python@v5
  with:
    python-version: '3.13'
    cache: 'pip'
```

**Also update**:
- `requirements.txt` header (if it specifies Python version)
- README.md development setup instructions
- Any Docker files or deployment configs

---

## 🧪 Testing

```bash
# Test locally with target version
python3.11 --version  # or python3.13
python3.11 -m venv testenv
source testenv/bin/activate
pip install -r requirements.txt
make test
```

---

## 📁 Files to Update

- `.github/workflows/ci.yml`
- `.github/workflows/ci-lite.yml`
- `.github/workflows/nightly-coverage.yml` (if exists)
- `README.md` (Python version requirements)
- `requirements.txt` (add version constraint if needed)

---

## 🔗 Related

- Part of CI/CD standardization effort
- May affect package compatibility
- Should align with production Python version

---

**Priority**: 🟡 MEDIUM - Not blocking but causes inconsistency
**Estimated Effort**: 30 minutes
**Assignee**: TBD

# YouTube Integration Maintenance Guide

## 📋 Overview

This document describes how we prevent future breakage of the YouTube transcript integration.

**Last Updated:** 2025-10-20  
**Current Version:** youtube-transcript-api v1.2.3

---

## 🛡️ Protection Mechanisms

### 1. **Automated Testing**

**File:** `tests/test_youtube_transcript_api_compat.py`

**What it does:**
- Verifies API methods exist (`.list()`, `.fetch()`)
- Checks error classes are importable
- Tests return value structures
- Validates our `YouTubeTranscriptFetcher` still works

**How to run:**
```bash
cd development
pytest tests/test_youtube_transcript_api_compat.py -v
```

**When to run:**
- Before upgrading youtube-transcript-api
- After modifying transcript fetcher code
- In CI/CD pipeline on every push

---

### 2. **Version Pinning**

**File:** `development/requirements.txt`

**Current constraint:**
```
youtube-transcript-api>=1.2.3,<2.0.0
```

**Why this range:**
- `>=1.2.3`: Minimum version with working API
- `<2.0.0`: Prevent auto-upgrade to v2.x (likely breaking changes)

**Update process:**
1. Read release notes
2. Update constraint in requirements.txt
3. Run tests
4. Update migration guide if needed

---

### 3. **Pre-commit Hook**

**File:** `.git/hooks/pre-commit`

**What it does:**
- Checks youtube-transcript-api version >= 1.2.3
- Runs tests if YouTube-related files changed
- Prevents commits that break compatibility

**Bypass (use sparingly):**
```bash
git commit --no-verify
```

---

### 4. **CI/CD Integration**

**File:** `.github/workflows/youtube-integration-tests.yml`

**Triggers:**
- Push to YouTube-related files
- Pull requests
- Manual workflow dispatch

**What it tests:**
- API compatibility
- Transcript fetcher integration
- Import verification

---

### 5. **Documentation**

**Migration Guide:** `docs/youtube-transcript-api-migration.md`
- Historical breaking changes
- How we fixed each issue
- Upgrade checklist

**Developer Guide:** `docs/DEVELOPER-QUICKSTART.md`
- Setup instructions
- Testing workflow
- Common issues

---

## 🔄 Upgrade Workflow

### When youtube-transcript-api releases a new version:

1. **Check release notes**
   ```bash
   pip3 show youtube-transcript-api
   # Check GitHub releases for breaking changes
   ```

2. **Create test branch**
   ```bash
   git checkout -b test/youtube-api-v{NEW_VERSION}
   ```

3. **Update requirements.txt**
   ```python
   # Before
   youtube-transcript-api>=1.2.3,<2.0.0
   
   # After
   youtube-transcript-api>={NEW_VERSION},<{NEXT_MAJOR}.0.0
   ```

4. **Install and test**
   ```bash
   pip3 install --upgrade youtube-transcript-api
   pytest tests/test_youtube_transcript_api_compat.py -v
   ```

5. **If tests fail:**
   - Read error messages
   - Check what API changed
   - Update `src/ai/youtube_transcript_fetcher.py`
   - Update test expectations if needed
   - Document changes in migration guide

6. **Integration test**
   ```bash
   # Start server
   python3 development/run_youtube_api_server.py
   
   # Test with real note
   curl -X POST http://localhost:8080/api/youtube/process \
     -H "Content-Type: application/json" \
     -d '{"note_path": "knowledge/Inbox/YouTube/TEST.md.md"}'
   ```

7. **Update documentation**
   - Add entry to migration guide
   - Update version numbers in docs

8. **Commit and PR**
   ```bash
   git add -A
   git commit -m "chore: upgrade youtube-transcript-api to v{NEW_VERSION}"
   git push origin test/youtube-api-v{NEW_VERSION}
   ```

---

## 🚨 Emergency Rollback

If a version breaks production:

```bash
# 1. Revert to known good version
pip3 install youtube-transcript-api==1.2.3

# 2. Update requirements.txt
echo "youtube-transcript-api==1.2.3" > requirements.txt

# 3. Restart server
pkill -f run_youtube_api_server
python3 development/run_youtube_api_server.py

# 4. Create issue
# Document what broke and why
```

---

## 📊 Testing Coverage

| Component | Test Type | File |
|-----------|-----------|------|
| API methods | Unit | `test_youtube_transcript_api_compat.py` |
| Error classes | Unit | `test_youtube_transcript_api_compat.py` |
| Return structures | Integration | `test_youtube_transcript_api_compat.py` |
| Transcript fetcher | Integration | `test_youtube_transcript_api_compat.py` |
| Full workflow | Manual | Developer guide instructions |

---

## 🔍 Monitoring

### Signs of API issues:

1. **Tests failing in CI**
   - Check GitHub Actions for failed workflows
   - Review error messages

2. **Runtime errors**
   - Check server logs for import errors
   - Look for "AttributeError" or "ImportError"

3. **User reports**
   - "No quotes generated"
   - "Processing fails silently"
   - "Transcript not found" (when it exists)

### Debug checklist:

```bash
# 1. Check version
pip3 show youtube-transcript-api

# 2. Run tests
pytest tests/test_youtube_transcript_api_compat.py -v

# 3. Test fetcher directly
python3 << 'EOF'
import sys
sys.path.insert(0, 'development')
from src.ai.youtube_transcript_fetcher import YouTubeTranscriptFetcher
fetcher = YouTubeTranscriptFetcher()
result = fetcher.fetch_transcript("h6fcK_fRYaI")
print(f"Result: {result}")
EOF

# 4. Check server logs
tail -f server.log  # If logging enabled
```

---

## 📚 Related Documentation

- [Migration Guide](youtube-transcript-api-migration.md) - Historical changes
- [Developer Quick Start](DEVELOPER-QUICKSTART.md) - Setup & testing
- [API Integration](../src/ai/youtube_transcript_fetcher.py) - Source code

---

## ✅ Health Checklist

Run this monthly to verify system health:

- [ ] Run full test suite: `pytest tests/ -v`
- [ ] Check dependency versions: `pip3 list | grep youtube`
- [ ] Review CI/CD status in GitHub Actions
- [ ] Test with real YouTube video
- [ ] Verify server starts without errors
- [ ] Check for library updates: `pip3 list --outdated`

---

**Maintainer Notes:**

This system is designed to catch breaking changes BEFORE they reach production. The multi-layered approach (tests + docs + CI + hooks) ensures we're protected even if one layer is bypassed.

The key is running tests BEFORE and AFTER any dependency changes. When in doubt, consult the migration guide.
